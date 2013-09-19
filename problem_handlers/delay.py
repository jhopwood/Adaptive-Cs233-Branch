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

from helpers import circuit
from helpers import eparser
from helpers import expression
from helpers.kmap_simulator import *

import base_handler

three_rows = [["0", "0", "0"], ["0", "0", "1"], ["0", "1", "0"], ["0", "1", "1"], ["1", "0", "0"], ["1", "0", "1"], ["1", "1", "0"], ["1", "1", "1"]]

cg = circuit.generator()
#(longest, shortest, shortest x, shortest y)
expressions = [[("x+y'", 3, 2, 2, 3) , ("x'y", 3, 2, 3, 2), ("xy+x'", 4, 3, 3, 4)],  # level1
               [("(x'+y)'", 4, 3, 4, 3), ("(x'y')'", 4, 4, 4, 4), ("(yx)((x'+y)y)", 5, 2, 2, 2), ("x+((x+y)(x+y)')", 7, 2, 2, 6)],
               [("(x'y)+(x'y)+z", 5, 2, 5, 4), ("x'zy+xz", 5, 4, 4, 4), ("x'+y'zx", 5, 3, 3, 5), ("(xy'z)(x+z')", 5, 2, 2, 3)]]     # level2
                        # level3

truthtable_defaults = {
 3 : {"cols":["x", "y", "z", "f(x,y,z)"], "numrows":8, "terminals":"xyz"}, 
 2 : {"cols":["x", "y", "f(x,y)"], "numrows":4, "terminals":"xy"}}

class Delay(base_handler.BaseHandler):
	valid_types = [
		"delay"
	]

	__my_random__ = None

	def seed_random(self, question_type):
		if self.__my_random__ == None:
			self.__my_random__ = random.Random()
		self.__my_random__.seed(self.generate_index(self.magic, self.level, self.problem_id, question_type))

	def maximum_level(self, question_type):
		return 2

	def get_expression(self,level,index):
		exp = expressions[level]
		return self.__my_random__.choice(exp)

	def parse_expression(self, level, exp):
		logging.info("parse_expression(%s)" % exp)
		terminals = "xyz"
		parser = eparser.Parser(eparser.spec, terminals)
		parser.reset()
		parser.scan(exp)
		graph = parser.start[0].final
		return (parser, terminals, graph)


	def get_circuit(self,level,exp,name,output):
		logging.info("get_circuit(%s, %s)" % (exp, output))
		cg.reset()
		(parser, terminals, graph) = self.parse_expression(level, exp)
		cg.generate_circuit(graph, output)
		inputs = "x, y"
		return cg.generate_schematic()

	# the root of every question is generating an expression using all the parameters
	# also we populate "data" with a bunch of junk about the problem.
	def get_base_expression(self, question_type):
		self.seed_random(question_type)
		ask_type = self.__my_random__.choice(range(4))
		num_terminals = 2 if self.level < 3 else 3
		(exp, longest, shortest, shortx, shorty) = self.get_expression(self.level, self.generate_index(self.magic, self.level,
								  self.problem_id, question_type))
		data = {"magic": self.magic, "problem_id": self.problem_id, 
				"qtype": question_type, "level": self.level, "exp":exp, "longest":longest, "shortest":shortest, "shortx": shortx, "shorty":shorty }
		if ask_type == 0:
			data["answer"] = longest
			data["ask_type"] = "longest path through the circuit takes"
		elif ask_type == 1:
			data["answer"] = shortest
			data["ask_type"] = "shortest path through the circuit takes"
		elif ask_type == 2:
			data["answer"] = shortx
			data["ask_type"] = "shortest path from x to out takes"
		else:
			data["answer"] = shorty
			data["ask_type"] = "shortest path from y to out takes"

		return (exp, data, self.level, num_terminals)

	def data_for_question(self, question_type): # a student requested a problem.
		# generate an expression
		(exp, data, level, num_terminals) = self.get_base_expression(question_type)
		data["circuit"] = self.get_circuit(level, exp, "circuit", "out")

		# serve it using the correct template.
		return data

	def score_student_answer(self, question_type, question_data, student_answer):
		ans = question_data["answer"]
		if int(student_answer) == ans:
			score = 100.0
		else:
			score = 0.0
		return (score, ans)


