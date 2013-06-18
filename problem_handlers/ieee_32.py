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


import math
import logging
import random
import json

import base_handler
import number_based_problem

#globals you can modify to determine how hard or easy a level is
easyexponent=7
mediumexponent=10
hardexponent=15

mediummantissa=5
hardmantissa=10

class IeeeProblem(base_handler.BaseHandler):
	__my_random__ = None
	# d=decimal and ieee= I triple e notation
	valid_types = ["d2ieee","ieee2d"]
  
	#TODO
	#getmaxlevel function
	#remove post and implement 
	#	-score_student_answer(self, question_type,question_data,student_answer)
	
	#gets the max level of the question again used in baseclass
	def maximum_level(self, question_type):
		return 2
	
	#used by the basehelper to render the page
	def template_for_question(self, question_type):
		return "ieee.html"
	
	#used by the basehelper to grade the students score
	def score_student_answer(self,question_type,question_data,student_answer):
		wanted = self.data_for_question(question_type)
		if question_type=="d2ieee":
			answer=student_answer
			if (wanted["sign"] == answer[0:1] and wanted["exponent"] == answer[1:9] and wanted["mantissa"] == answer[9:32]):
				score=100
			else:
				score=0
		elif question_type=="ieee2d":
			answer=student_answer
			if wanted["decimal"] == float(answer):
				score=100
			else:
				score=0
		
		return (float(score),wanted)
		
	#gets the data returns it as {"sign":signbit, "exponent":exponent, "mantissa":mantissa, "decimal":decimal}
	def data_for_question(self, question_type):
		if self.__my_random__ == None:
			self.__my_random__ = random.Random()
		self.__my_random__.seed(self.generate_index(self.magic, self.level, self.problem_id, question_type))
		
		#generates the signbit
		signbit=str(self.__my_random__.randint(0,1))
		
		#this generates the exponent and mantissa based on the difficulty level
		if self.level == 0:
			exponent = self.__my_random__.randint(127-easyexponent,127+easyexponent)
			mantissa = "00000000000000000000000"
		elif self.level == 1:
			exponent = self.__my_random__.randint(127-easyexponent,127+easyexponent)
			mantissa = ""
			for i in range(0, mediummantissa):
				mantissa = mantissa+ str(self.__my_random__.randint(0,1))
			for i in range(0, 23-mediummantissa):
				mantissa = mantissa+"0"
		elif self.level == 2:
			exponent = self.__my_random__.randint(127-hardexponent,127+hardexponent)
			mantissa = ""
			for i in range(0, hardmantissa):
				mantissa=mantissa+ str(self.__my_random__.randint(0,1))
			for i in range(0, 23-hardmantissa):
				mantissa=mantissa+"0"
		else:
			mantissa="Error level is not suported"
			
		#this calculates the decimal value of whatever iee is generated	
		decimal=(1-2*int(signbit))* math.pow(2,exponent-127) * self.mantissa_to_decimal(mantissa)

		exponent=self.int_to_bit(exponent)
		return {"sign":signbit, "exponent":exponent, "mantissa":mantissa, "decimal":decimal}
		
	
	#changes a decimal into a string of "0" and "1" assumes value will fit in 8 bits
	def int_to_bit(self, value):
		ret=""
		for i in range(0,8):
			if value-math.pow(2,7-i)>=0:
				ret=ret+"1"
				value=value-math.pow(2,7-i)
			else:
				ret=ret+"0"
		return ret
	
	# this takes a mantissa in form 10101010 ect and turns it into a decimal for calculations someting like 1.25
	def mantissa_to_decimal(self, value):
		retval=1
		for i in range(0, len(value)):
			if value[i]=="1":
				retval=retval + 1/math.pow(2,i+1)
		return retval		