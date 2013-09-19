#!/usr/bin/env python
# TODO: Should this license be here? I mean, is the code we write copywright Google?
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import math
import logging
import sys
import os
import re
import random
import string
import json

from helpers import circuit
from helpers import eparser
from helpers import expression
from helpers.kmap_simulator import *

import base_handler

terminals2 = "xy"
terminals3 = "xyz"
cg = circuit.generator()

two_rows = [["0", "0"], ["0", "1"], ["1", "0"], ["1", "1"]]
three_rows = [["0", "0", "0"], ["0", "0", "1"], ["0", "1", "0"], ["0", "1", "1"], ["1", "0", "0"], ["1", "0", "1"], ["1", "1", "0"], ["1", "1", "1"]]

cells = ('0000', '0100', '1100', '1000',
		'0001', '0101', '1101', '1001',
		'0011', '0111', '1111', '1011',
		'0010', '0110', '1110', '1010')

truthtable_defaults = {
 3 : {"cols":["x", "y", "z", "f(x,y,z)"], "rows":three_rows, "numrows":8, "terminals":"xyz"}, 
 2 : {"cols":["x", "y", "f(x,y)"], "rows":two_rows, "numrows":4, "terminals":"xy"}}

def int_convert(s, default, minimum=sys.float_info.min, maximum=sys.float_info.max):
	if isinstance(s,int):
		return s
	if s.isdigit():
		val = int(s)
		if val >= minimum and val <= maximum:
			return val
	return default

class DigitalLogic(base_handler.BaseHandler):
	valid_types = ["e2c", "c2t",
				   "t2c", "e2t",
				   "t2e", "v2c",
				   "c2e", "v2e", "v2t"]

	def tt_to_kmap(self, tt, num_terminals):
		bits = [0] * 16
		if num_terminals == 2:
			tt[2], tt[3] = tt[3], tt[2]
			bits = tt * 4
			return bits
		tt[4], tt[6] = tt[6], tt[4]
		tt[5], tt[7] = tt[7], tt[5]
		for i in range(0,16):
			bits[i] = tt[2 * (i % 4)] if i < 8 else tt[(2 * (i % 4)) + 1]
		return bits

	def convert_family(self, level, exp, num_terminals):
		if self.family == 1:
			return exp
		tt = self.get_truthtable(level, exp)
		bits = self.tt_to_kmap(tt, num_terminals)
		kmap = KmapSimulator(bits, cells)
		answer = kmap.getAnswer()
		for (a,b) in [("A", "x"), ("B", "y"), ("C", "z"), ("D", "w")]:
			answer = answer.replace(a,b)
		return answer

	def get_expression(self, level, index, family):
		etemplates = expression.equation_templates[family/2]
		if level < 3:
			num_terminals = 2
			etemplate = etemplates[0][level]
		else:
			num_terminals = 3
			etemplate = etemplates[1][level-3]
		exp = expression.get_expression(num_terminals, etemplate, index)
		return exp

	def parse_expression(self, level, exp):
		terminals = terminals2 if level < 3 else terminals3
		parser = eparser.Parser(eparser.spec, terminals)
		parser.reset()
		parser.scan(exp)
		graph = parser.start[0].final
		return (parser, terminals, graph)

	def get_truthtable(self, level, exp):
		tt = []
		(parser, terminals, graph) = self.parse_expression(level, exp)
		terminals_map = parser.terminals
		num_combinations = int(math.pow(2,len(terminals)))
		num_terminals = len(terminals)
		for i in range(num_combinations):
			for j in range(num_terminals):
				# setting the value of terminal j
				val = (i >> (num_terminals - 1 - j)) & 1
				terminals_map[terminals[j]].val = val
			tt.append(1 if graph.evaluate() else 0)
		return tt

	def get_verilog(self, level, exp, name, output):
		cg.reset(family=self.family)
		(parser, terminals, graph) = self.parse_expression(level, exp)
		cg.generate_circuit(graph, output)
		inputs = "x, y%s" % ('' if level < 3 else ', z')
		return cg.generate_verilog(name, output, inputs)

	def get_circuit(self, level, exp, name, output):
		cg.reset(family=self.family)
		(parser, terminals, graph) = self.parse_expression(level, exp)
		cg.generate_circuit(graph, output)
		inputs = "x, y%s" % ('' if level < 3 else ', z')
		return cg.generate_schematic()

	# the root of every question is generating an expression using all the parameters
	# also we populate "data" with a bunch of junk about the problem.
	def get_base_expression(self, question_type):
		num_terminals = 2 if self.level < 3 else 3
		exp = self.get_expression(self.level, self.generate_index(self.magic, self.level,
								  self.problem_id, question_type), self.family)
		new_exp = self.convert_family(self.level, exp, num_terminals)

		data = {"magic": self.magic, "problem_id": self.problem_id, 
				"qtype": question_type, "level": self.level,
				"family":self.family}
		data.update(truthtable_defaults[num_terminals])
		return (exp, new_exp, data, self.level, num_terminals)

	def data_for_question(self, question_type): # a student requested a problem.
		logging.info("serve_problem(%s)" % question_type)
		# generate an expression
		(exp, new_exp, data, level, num_terminals) = self.get_base_expression(question_type)
		
		data["new_exp"] = new_exp
		data["exp"] = exp
		data["family"] = self.family
		# convert that into the right type of "given"
		given_type = question_type[0]

		if given_type == "e":
			data["expression"] = ("f(x,y) = " if level == 2 else "f(x,y,z) = ") + new_exp
		elif given_type == "t":
			data["truthtable"] = self.get_truthtable(level, exp)
		elif given_type == "v":
			ver = self.get_verilog(level, exp, "circuit", "out")
			data["verilog"] = string.join(ver, "\n")
		elif given_type == "c":
			data["circuit"] = self.get_circuit(level, exp, "circuit", "out")
		return data

	def score_student_answer(self, question_type, question_data, student_answer):   # this is a request for grading a problem.  
		# validate that is a useful thing to grade
		
		level = question_data["level"]
		exp = question_data["exp"]
		(exp, new_exp, data, level, num_terminals) = self.get_base_expression(question_type)
		result_tt = self.get_truthtable(level, exp)

		# evaluate student answer based on the type of "ask"
		ask_type = question_type[2]
		if ask_type == "e" or ask_type == "c":
			user_tt = self.get_truthtable(level, student_answer)
			score = 100.0 * reduce(lambda x, y: x * y, 
								   map(lambda x: 1 if x[0] == x[1] else 0, 
									   zip(map(lambda x: "%s"%x, result_tt), 
										   map(lambda x: "%s"%x, user_tt))), 1)
		elif ask_type == "t":
			score = 100.0 * reduce(lambda x, y: x + y, 
								   map(lambda x: 1 if x[0] == x[1] else 0, 
									   zip(map(lambda x: "%s"%x, result_tt), 
										   map(lambda x: x[-1], student_answer.split()))))
			score /= len(result_tt)
		return (score, "if you are reading this something probably went wrong")

		# send back a response to the user

	def maximum_level(self, question_type):
		return 4

	def get_return_data(self, score, wanted, question_data, question_type):
		result_tt = self.get_truthtable(question_data["level"], question_data["new_exp"])
		returndata = {"score":score, "wanted":wanted, "exp": question_data["new_exp"], "result_tt": result_tt}
		if question_type[2] == "c":
			returndata["circuit"] = self.get_circuit(question_data["level"], question_data["exp"], "circuit", "out")
		return returndata