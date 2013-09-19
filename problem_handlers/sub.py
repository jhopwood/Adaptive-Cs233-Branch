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
import adaptive_base_handler
import number_based_problem
from models import Proficiency



class Subtraction(adaptive_base_handler.AdaptiveBaseHandler):
	__my_random__ = None
	valid_types = ["sub"]
	
	#gets the max level of the question again used in baseclass
	def maximum_level(self, question_type):
		return 10
	
	#used by the basehelper to render the page
	def template_for_question(self, question_type):
		return "adaptivemath.html"
	
	#used by the basehelper to grade the students score also modifies the right_wrong array
	def score_student_answer(self,question_type,question_data,student_answer):
		wanted = question_data
		answer = student_answer
		if (wanted["answer"] == float(answer)):
			score = 100
		else:
			score = 0
		
		return (float(score),wanted)
		
	#gets the data returns it as {"number1": num1, "number2":num2, "answer":ans, "button":self.request.get('button'), "sign":"-", "typ":typ, "lev":lev}
	#, "typ":typ, "lev":lev, "wr":rightwrong}  are for debugging purposes
	def data_for_question(self, question_type):
		if self.__my_random__ == None:
			self.__my_random__ = random.Random()
		self.__my_random__.seed(self.generate_index(self.magic, 0, self.problem_id, question_type))
		
		#generates num1 and num2 to be added
		num1 = self.__my_random__.randint(1,10)*max(self.level,1)
		num2 = self.__my_random__.randint(1,10)*max(self.level,1)
		
		ans = num1 - num2
			
		return {"number1": num1, "number2":num2, "answer":ans, "sign":"-"}