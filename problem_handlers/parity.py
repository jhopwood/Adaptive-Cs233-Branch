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
import string

G1 = [[1, 1, 0, 1],  #p1
	  [1, 0, 1, 1],  #p2
	  [1, 0, 0, 0],
	  [0, 1, 1, 1],  #p4
	  [0, 1, 0, 0],
	  [0, 0, 1, 0],
	  [0, 0, 0, 1]]

G2 = [[1, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1], #p1
	 [1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1],  #p2
	 [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
	 [0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1],  #p4
	 [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
	 [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
	 [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
	 [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1],  #p8
	 [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
	 [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
	 [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
	 [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
	 [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
	 [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
	 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]]

all_labels = ["p1", "p2", "d1", "p4", "d2", "d3", "d4", "p8", "d5", "d6", "d7", "d8", "d9", "d10", "d11"]

def matrix_mul(matrix, vec):
	result = [0] * len(matrix)
	for i in range(0,len(result)):
		for j in range(0,len(vec)):
			result[i] = (result[i] + matrix[i][j] * vec[j]) % 2
	return result

def ones(n):
        return sum(int(x) for x in n);

def hamming_distance(n, m):
	return sum(d1 != d2 for d1,d2 in zip(n, m))

def generate_sec_code(level):
	mat = G1 if level == 0 else G2
	data_len = len(mat[0])
	data_arr = [0] * data_len
	data_val = bin(Parity.generator.randint(1, (2 ** data_len) - 1))[2:].zfill(data_len)

	for i in range(0,len(data_arr)):
		data_arr[i] = string.atoi(data_val[i], 10)

	return matrix_mul(mat, data_arr)

class Parity(base_handler.BaseHandler):
	valid_types = [
		"par",     # Compute the parity
		"sec",     # Single-Error Correcting
		"hd",      # Hamming Distance (What is the distance)
		"hd2", 	   # Hamming Distance (What is an example number at that distance)
		"hdc"	   # How much Hamming Distance can be tolerated
	]

	def maximum_level(self, question_type):
		if question_type == "par":
			return 1
		if question_type == "sec":
			return 1
		if question_type == "hd":
			return 2
		if question_type == "hd2":
			return 1
		if question_type == "hdc":
			return 0

	def data_for_question(self, question_type):
		if question_type == "par":
			self.length = 2 ** (self.level + 2)
			upper_bound = (2 ** self.length) - 1
			num1 = bin(self.generator.randint(0, upper_bound))[2:].zfill(self.length)
			even_odd = self.generator.randint(0, 1);
			ones_count = ones(num1);			
			odd_parity = ones(num1) % 2;			
			return {"num1": num1, "even_odd": "even" if even_odd else "odd", "length": self.length, 
                                "ones_count": ones_count, "parity": 1 if even_odd == odd_parity else 0}

		if question_type == "hdc":
			correction = self.generator.randint(0,3)
			detection = (correction if correction != 0 else 1) + self.generator.randint(0,3)
		        dist = correction + detection + 1
			## dist = self.generator.randint(2,5)
			## temp1 = self.generator.randint(1,dist - 1)
			## temp2 = dist - temp1 - 1
			## detection = temp1 if temp1 >= temp2 else temp2
			## correction = dist - detection - 1
			return {"dist": str(dist), "detection": detection, "correction": correction}

		if question_type == "hd":
			self.length = 2 ** (self.level + 2)
			upper_bound = (2 ** self.length) - 1
			num1 = bin(self.generator.randint(1, upper_bound))[2:].zfill(self.length)
			num2 = bin(self.generator.randint(1, upper_bound))[2:].zfill(self.length)
			dist = hamming_distance(num1, num2)
			return {"num1": num1, "num2": num2, "dist": str(dist), "length": self.length}

		if question_type == "hd2":
			self.length = 2 ** (self.level + 2)
			upper_bound = (2 ** self.length) - 1
			num1 = bin(self.generator.randint(1, upper_bound))[2:].zfill(self.length)
			dist = self.generator.randint(1, self.length)
			return {"num1": num1, "dist": str(dist), "length": self.length}

		labels = all_labels[0:7] if self.level == 0 else all_labels

		flip_index = self.generator.randint(0, len(labels) - 1)
		flipped_arr = generate_sec_code(self.level)
		flipped_arr[flip_index] = (flipped_arr[flip_index] + 1) % 2
		flipped_string = "".join( str( val ) for val in flipped_arr )

		odd_parity = []
		syndrome = bin(flip_index + 1)[2:].zfill(3) if self.level == 0 else bin(flip_index + 1)[2:].zfill(4)
		for i in range(0,len(syndrome)):
			if syndrome[len(syndrome) - i - 1] == "1":
				odd_parity.append("p" + str(2 ** i))
		odd_par_str = ", ".join(odd_parity)

		return {"labels": labels, "flipped_string": flipped_string, "flip_index": flip_index, "length": len(labels), "odd_parity": odd_par_str}

	def score_student_answer(self, question_type, question_data, student_answer):
		if question_type == "sec":
			wanted = self.get_description_string(question_data)
			return (100.0 if wanted == student_answer else 0.0, (wanted, question_data["odd_parity"]))
		elif question_type == "hd2":
		        answer = hamming_distance(question_data["num1"], student_answer)
			wanted = question_data["dist"]
			return (100.0 if int(answer) == int(wanted) else 0.0, answer)
		elif question_type.startswith("hd"):
			wanted = question_data["dist"]
		elif question_type == "par":
		        wanted = question_data["parity"]
			logging.warn(wanted)
			logging.warn(student_answer)
			return (100.0 if int(wanted) == int(student_answer) else 0.0, (wanted, question_data["ones_count"]))
		if wanted == student_answer:
			return (100.0, wanted)
		return (0.0, wanted)

	def get_description_string(self, description):
		flip_index = description["flip_index"]
		return str(flip_index)
