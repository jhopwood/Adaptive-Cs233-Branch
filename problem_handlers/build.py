#!/usr/bin/env python
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

from helpers import circuit_mod
from helpers import eparser
from helpers import expression
from helpers.kmap_simulator import *

import base_handler

terminals_4_to_1 = "abcdef"
terminals_8_to_1 = "abcdefghxyz"
expression_mux2 = "ac'+bc"
expression_mux4 = "ae'f'+bef'+ce'f+def"
expression_mux8 = "ax'y'z' + bxy'z'+cx'yz'+dxyz'+ex'y'z+fxy'z+gx'yz+hxyz"

num_inp_sel = {3: [2, 1], 6: [4, 2], 11: [8, 3]}
two_rows = [["0", "0"], ["0", "1"], ["1", "0"], ["1", "1"]]
three_rows = [["0", "0", "0"], 
  		  ["0", "0", "1"], 
			  ["0", "1", "0"], 
			  ["0", "1", "1"], 
			  ["1", "0", "0"], 
			  ["1", "0", "1"], 
			  ["1", "1", "0"], 
			  ["1", "1", "1"]]

cg = circuit_mod.generator()

truthtable_defaults = {
 3 : {"terminals":"abc", "num_select": 1, "num_inputs": 2},
 6 : {"terminals":"abcdef", "num_select": 2, "num_inputs": 4}, 
 11 : {"terminals":"abcdefghxyz", "num_select": 3, "num_inputs": 8}}

class Build(base_handler.BaseHandler):
	valid_types = [
		"mux",    # Multiplexer
		"dec"     # Decoder
	]

	def maximum_level(self, question_type):
		return 1

	def get_expression(self,level,index):
		logging.info("get_expression()")
		if self.level == 0:
			return expression_mux4
		return expression_mux8

	def parse_expression(self, level, exp):
		logging.info("parse_expression(%s)" % exp)
		terminals = terminals_4_to_1 if level == 0 else terminals_8_to_1
		parser = eparser.Parser(eparser.spec, terminals)
		parser.reset()
		parser.scan(exp)
		graph = parser.start[0].final
		return (parser, terminals, graph)

	def get_truthtable(self, level, exp):
		logging.info("get_truthtable(%s)" % exp)
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

	def draw_circuit(self,level,num_terminals,exp,solution):
		logging.info("draw_circuit(%i)" % num_terminals)
		num_inputs = num_inp_sel[num_terminals]
		cg.reset()
		(parser, terminals, graph) = self.parse_expression(level, exp)
		cg.hardcode_circuit(num_terminals, level, solution)
		return cg.generate_schematic()

	def get_base_expression(self, question_type):
		logging.info("get_base_expression(%s)" % question_type)
		num_terminals = 6 if self.level == 0 else 11
		exp = self.get_expression(self.level, self.generate_index(self.magic, self.level,
								  self.problem_id, question_type))

		data = {"magic": self.magic, "problem_id": self.problem_id, 
				"qtype": question_type, "level": self.level, "exp":exp}
		data.update(truthtable_defaults[num_terminals])
		return (exp, data, self.level, num_terminals)

	def data_for_question(self, question_type):
		logging.info("data_for_question(%s)" % question_type)
		# generate an expression
		(exp, data, level, num_terminals) = self.get_base_expression(question_type)
		tt = self.get_truthtable(level, exp)
		circuit = self.draw_circuit(level, num_terminals, exp, False)
		logging.info(circuit)
		logging.info(data)
		data.update({'truthtable': tt, 'circuit': circuit})
		return data

	def score_student_answer(self,question_type,question_data,student_answer):
		logging.info("score_student_answer(%s)" % question_type)
		# generate the expression for the problem that we're trying to grade
		(exp, data, level, num_terminals) = self.get_base_expression(question_type)
		result_tt = self.get_truthtable(level, exp)
		user_tt = self.get_truthtable(level, student_answer)

		score = 100.0 * reduce(lambda x, y: x * y, 
							   map(lambda x: 1 if x[0] == x[1] else 0, 
								   zip(map(lambda x: "%s"%x, result_tt), 
									   map(lambda x: "%s"%x, user_tt))), 1)
		return (score, "")

	def get_return_data(self, score, wanted, question_data, question_type):
		(exp, data, level, num_terminals) = self.get_base_expression(question_type)
		circuit = self.draw_circuit(level, num_terminals, exp, True)
		result_tt = self.get_truthtable(level, exp)
		return {'score': score, 'wanted': wanted, 'exp': exp, 'result_tt': result_tt, 'circuit': circuit}
