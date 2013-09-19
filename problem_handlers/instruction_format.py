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

import base_handler
import math
import random
import json
import logging

from helpers.cache_address_generator import AddressGenerator

R_format = {'opcode': [26,31], 'rs': [21,25], 'rt': [16,20], 'rd': [11,15], 'shamt': [6,10], 'funct': [0,5]}
I_format = {'opcode': [26,31], 'rs': [21,25], 'rt': [16,20], 'immediate': [0,15]}
J_format = {'opcode': [26,31], 'address': [0,25]}

class InstructionFormat(base_handler.BaseHandler):
	valid_types = [
		"if"	# basic instruction format
	]
	formats = {"R": {'opcode': [26,31], 'rs': [21,25], 'rt': [16,20], 'rd': [11,15], 'shamt': [6,10], 'funct': [0,5]}, 
			   "I": {'opcode': [26,31], 'rs': [21,25], 'rt': [16,20], 'immediate': [0,15]}, 
			   "J": {'opcode': [26,31], 'address': [0,25]}}
	format_types = ["R", "I", "J"]

	def maximum_level(self, question_type):
		return 0

	def data_for_question(self, question_type):
		format_type = self.generator.choice(self.format_types)
		return {'format_type': format_type}

	def score_student_answer(self,question_type,question_data,student_answer):
		format_type = question_data['format_type']
		format = self.formats[format_type]
		wanted = [""] * 32
		for field in format.keys():
			lo = format[field][0]
			hi = format[field][1]
			for i in range(lo,hi+1):
				wanted[31-i] = field
		student_answer = student_answer.split(",")
		score = 0.0
		if len(student_answer) == 0:
			return (score, wanted)
		for i in range(len(wanted)):
			if wanted[i] == student_answer[i]:
				score += 100.0/len(wanted)
		score = round(score, 2)
		return (score, wanted)
