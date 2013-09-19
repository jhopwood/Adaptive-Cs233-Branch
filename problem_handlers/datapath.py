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
import ast

from mips_assembler import instruction

from helpers.cache_address_generator import AddressGenerator

signals = {
  	   "add":  {'alu_op': "010", 'itype': "0", 'write_enable': "1", 'control_type': "00", 'mem_read': "0", 'word_write_enable': "0", 'byte_write_enable': "0", 'byte_load': "0", 'lui': "0", 'slt': "0", 'alu_src2': "0"}, 
		   "addi": {'alu_op': "010", 'itype': "1", 'write_enable': "1", 'control_type': "00", 'mem_read': "0", 'word_write_enable': "0", 'byte_write_enable': "0", 'byte_load': "0", 'lui': "0", 'slt': "0", 'alu_src2': "0"},
		   "and":  {'alu_op': "100", 'itype': "0", 'write_enable': "1", 'control_type': "00", 'mem_read': "0", 'word_write_enable': "0", 'byte_write_enable': "0", 'byte_load': "0", 'lui': "0", 'slt': "0", 'alu_src2': "0"},
		   "andi": {'alu_op': "100", 'itype': "1", 'write_enable': "1", 'control_type': "00", 'mem_read': "0", 'word_write_enable': "0", 'byte_write_enable': "0", 'byte_load': "0", 'lui': "0", 'slt': "0", 'alu_src2': "0"},
		   "jr":   {'alu_op': "xxx", 'itype': "0", 'write_enable': "0", 'control_type': "11", 'mem_read': "x", 'word_write_enable': "x", 'byte_write_enable': "x", 'byte_load': "x", 'lui': "x", 'slt': "x", 'alu_src2': "x"},
		   "lbu":  {'alu_op': "010", 'itype': "1", 'write_enable': "1", 'control_type': "00", 'mem_read': "1", 'word_write_enable': "0", 'byte_write_enable': "0", 'byte_load': "1", 'lui': "0", 'slt': "0", 'alu_src2': "1"},
		   "lw":   {'alu_op': "010", 'itype': "1", 'write_enable': "1", 'control_type': "00", 'mem_read': "1", 'word_write_enable': "0", 'byte_write_enable': "0", 'byte_load': "0", 'lui': "0", 'slt': "0", 'alu_src2': "1"},
		   "nor":  {'alu_op': "110", 'itype': "0", 'write_enable': "1", 'control_type': "00", 'mem_read': "0", 'word_write_enable': "0", 'byte_write_enable': "0", 'byte_load': "0", 'lui': "0", 'slt': "0", 'alu_src2': "0"},
		   "or":   {'alu_op': "101", 'itype': "0", 'write_enable': "1", 'control_type': "00", 'mem_read': "0", 'word_write_enable': "0", 'byte_write_enable': "0", 'byte_load': "0", 'lui': "0", 'slt': "0", 'alu_src2': "0"},
		   "ori":  {'alu_op': "101", 'itype': "1", 'write_enable': "1", 'control_type': "00", 'mem_read': "0", 'word_write_enable': "0", 'byte_write_enable': "0", 'byte_load': "0", 'lui': "0", 'slt': "0", 'alu_src2': "0"},
		   "slt":  {'alu_op': "011", 'itype': "0", 'write_enable': "1", 'control_type': "00", 'mem_read': "0", 'word_write_enable': "0", 'byte_write_enable': "0", 'byte_load': "x", 'lui': "0", 'slt': "1", 'alu_src2': "0"},
		   "slti": {'alu_op': "011", 'itype': "1", 'write_enable': "1", 'control_type': "00", 'mem_read': "0", 'word_write_enable': "0", 'byte_write_enable': "0", 'byte_load': "x", 'lui': "0", 'slt': "1", 'alu_src2': "0"},
		   "sll":  {'alu_op': "010", 'itype': "0", 'write_enable': "1", 'control_type': "00", 'mem_read': "0", 'word_write_enable': "0", 'byte_write_enable': "0", 'byte_load': "x", 'lui': "0", 'slt': "0", 'alu_src2': "0"},
		   "srl":  {'alu_op': "011", 'itype': "0", 'write_enable': "1", 'control_type': "00", 'mem_read': "0", 'word_write_enable': "0", 'byte_write_enable': "0", 'byte_load': "x", 'lui': "0", 'slt': "0", 'alu_src2': "0"},
		   "sb":   {'alu_op': "010", 'itype': "1", 'write_enable': "x", 'control_type': "00", 'mem_read': "x", 'word_write_enable': "0", 'byte_write_enable': "1", 'byte_load': "x", 'lui': "0", 'slt': "0", 'alu_src2': "1"},
		   "sw":   {'alu_op': "010", 'itype': "1", 'write_enable': "x", 'control_type': "00", 'mem_read': "x", 'word_write_enable': "1", 'byte_write_enable': "0", 'byte_load': "x", 'lui': "x", 'slt': "x", 'alu_src2': "1"},
		   "sub":  {'alu_op': "011", 'itype': "0", 'write_enable': "1", 'control_type': "00", 'mem_read': "0", 'word_write_enable': "0", 'byte_write_enable': "0", 'byte_load': "0", 'lui': "0", 'slt': "0", 'alu_src2': "0"}
		   }

class DataPath(base_handler.BaseHandler):
	valid_types = [
		"datapath"	# basic instruction format
	]

	valid_instructions = {
		# R type instructions
		"add":["r","r","r"],
		"and":["r","r","r"],
		"nor":["r","r","r"],
		"or":["r","r","r"],
		"sll":["r","r","s"],
		"srl":["r","r","s"],
		"sub":["r","r","r"],
		"slt":["r","r","r"],
		# I type instructions
		"addi":["r","r","i"],
		"andi":["r","r","i"],
		"lw":["r","r","i"],
		"lbu":["r","r","i"],
		"ori":["r","r","i"],
		"sw":["r","r","i"],
		"sb":["r","r","i"],
		"slti":["r","r","i"],
		# J type instructions (and jr of course)
		# "j":["a"],
		# "jal":["a"],
		"jr":["r"]
	}
	
	valid_registers = [
		# I'm not going to include $ra, as it is only really used for jr $ra,
		# and jr isn't one of the valid instructions
		"$v0", "$v1",
		"$a0", "$a1", "$a2", "$a3",
		"$t0", "$t1", "$t2", "$t3", "$t4", "$t5", "$t6", "$t7",
		"$s0", "$s1", "$s2", "$s3", "$s4", "$s5", "$s6", "$s7",
		"$t8", "$t9",
		# Since there is no reason to do most functions with $sp (like
		# 'sll $t0, $sp, 4'), I will just leave it out until I come up with
		# a better solution
		# "$sp"
	]

	def maximum_level(self, question_type):
		return 0

	def random_mips_instruction(self, inst_type):
		"""
		Generates a random valid MIPS string. It will be something along the 
		lines of
		
		'srl $a0, $s7, 2'
		'addi $t0, $t1, 10'
		
		etc...
		"""
		data = []
		for datatype in self.valid_instructions[inst_type]:
			if datatype == 'r':   # Register
				component = self.generator.choice(self.valid_registers)
			elif datatype == 'i': # Immediate (16 bits)
				component = str(self.generator.randint(0, 255))
			elif datatype == 's': # Shift Amount (5 bits)
				component = str(self.generator.randint(0,31))
			elif datatype == 'a': # Address (26 bits)
				component = str(self.generator.randint(0,33554431))
			data.append(component)
		data_string = ", ".join(data)
		return "%s %s" % (inst_type,data_string)

	def data_for_question(self, question_type):
		inst_type = self.generator.choice(self.valid_instructions.keys())
		instruction = self.random_mips_instruction(inst_type)
		return {"instruction": instruction, "inst_type": inst_type}

	def score_student_answer(self,question_type,question_data,student_answer):
		student_answer = ast.literal_eval(student_answer)
		logging.info(student_answer)
		inst_type = question_data['inst_type']
		wanted = signals[inst_type]
		score = 0.0
		for field in wanted.keys():
			logging.info(wanted[field])
			logging.info(student_answer[field])
			if wanted[field] == "x":
				score += 50.0 / len(wanted.keys())
			else:
				wanted_field = int(wanted[field],2)
				student_answer_field = int(student_answer[field],2)
				if wanted_field == student_answer_field:
					score += 100.0 / len(wanted.keys())

		score = round(score,2)
		return (score, wanted)
