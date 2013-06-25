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

class RegFile(base_handler.BaseHandler):
	valid_types = [
		"d2c",    # Description to Components
		"c2d"     # Components to Description
	]

	def maximum_level(self, question_type):
		return 0

	def data_for_question(self,question_type):
		log_num_regs = self.generator.randint(3,6) # 8 < num_regs < 64
		num_regs = 2 ** log_num_regs
		log_reg_width = self.generator.randint(3,6) # 8 <= reg_width <= 32
		reg_width = 2 ** log_reg_width # (reg-width)-bit registers
		num_write_ports = self.generator.randint(1,4) # number of write ports
		num_read_ports = self.generator.randint(2,4) # number of read ports

		description = ['To build a register file with ' + str(num_regs) + ' ' +
						str(reg_width) + '-bit registers, ' + str(num_write_ports) +
						' write ports and ' + str(num_read_ports) +' read ports, you would need:',
						'A register file that requires ' + str(num_write_ports) + ' ' +
						str(log_num_regs) + '-to-' + str(num_regs) + ' decoders\nand ' + str(num_read_ports) + ' ' + str(reg_width) + '-bit wide ' +
						str(num_regs) + '-to-1 multiplexors has:']

		desc_num = 0 if question_type == "d2c" else 1

		return {"description":description[desc_num],
				"regs":{"num_regs":num_regs, "log_num_regs":log_num_regs,
				"reg_width":reg_width, "log_reg_width":log_reg_width},
				"ports":{"num_write":num_write_ports, "num_read":num_read_ports}
				}

	def score_student_answer(self, question_type, question_data, student_answer):
		wanted_data = self.get_description_string(question_data, question_type)
		wanted_str = wanted_data[0]
		wanted = wanted_data[1]
		student_arr = map(int, student_answer.split(","))
		wanted_arr = map(int, wanted.split(","))

		if wanted == student_answer:
			return (100.0, wanted_str)
		else:
			score = 0.0
			length = len(wanted_arr)
			for i in range(0,length):
				if student_arr[i] == wanted_arr[i]:
					score += 100.0/length
			score = round(score, 2)
			return (score, wanted_str)

	def get_description_string(self, description, question_type):
		num_write_ports = description['ports']['num_write']
		log_num_regs = description['regs']['log_num_regs']
		num_regs = description['regs']['num_regs']
		num_read_ports = description['ports']['num_read']
		reg_width = description['regs']['reg_width']

		if question_type == "d2c":
			return ["%d %d-to-%d decoders, and\n%d %d-bit wide %d-to-%d multiplexors" % (num_write_ports, log_num_regs, num_regs, num_read_ports, reg_width, num_regs, 1), 
					"%d,%d,%d,%d,%d,%d,%d" % (num_write_ports, log_num_regs, num_regs, num_read_ports, reg_width, num_regs, 1)]

		return ["%d %d-bit registers, %d write ports and %d read ports" % (num_regs, reg_width, num_write_ports, num_read_ports),
				"%d,%d,%d,%d" % (num_regs, reg_width, num_write_ports, num_read_ports)]
