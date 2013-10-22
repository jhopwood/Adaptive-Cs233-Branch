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

from models import TrueFalseQuestion

TrueFalseQuestion(number = 17, question = "Parity enables the correction of single-bit errors.", answer = "false", 
                  explanation = "Parity only enables the <b>detection</b> of single-bit errors.  It doesn't have enough information to determine which bit has been flipped.").put()

TrueFalseQuestion(number = 18, question = "Odd parity means that the data word including its parity bit should have an odd number of ones", answer = "true", 
                  explanation = "In even parity, the parity bit is set so that there are even number of ones in the data word and the parity bit combined.  In odd parity, the parity bit is set so that there are an odd number of ones.").put()

TrueFalseQuestion(number = 19, question = "SECDED stands for Single-bit Error Correction, Double-bit Error Detection", answer = "true", 
                  explanation = "That's what it stands for.  SECDED is commonly used for ECC memory because the most common failure mode is a single-bit flip to a memory word.  SECDED is able to correct these errors, and in the unlikely event that a second error occurs before the first one is corrected, we can at least detect the data corruption.").put()

TrueFalseQuestion(number = 20, question = "Parity requires a Hamming distance of 1 between valid code words.", answer = "false", 
                  explanation = "Parity requires a Hamming distance of 2 between valid code words, so that there is an invalid code word between valid code words to enable 1-bit error detection.").put()



class TrueFalse(base_handler.BaseHandler):
	__my_random__ = None
	valid_types = ["add","question"]
  

	#gets the max level of the question again used in baseclass
	def maximum_level(self, question_type):
		return 0
	
	#used by the basehelper to render the page
	def template_for_question(self, question_type):
		return "true-false.html"
	
	#used by the basehelper to grade the students score
	def score_student_answer(self,question_type,question_data,student_answer):
		#adds a question to the database
		if(question_type == "add"):
			answer = str(self.request.get('answer[answer]'))
			question = str(self.request.get('answer[question]'))
			number = int(self.request.get('answer[number]'))
			explanation = str(self.request.get('answer[explanation]'))
			self.put_question(number, question, answer, explanation)
			return(0.0, "It submitted correctly")
		else:		
			wanted = self.data_for_question(question_type)
			
			if (wanted["answer"] == student_answer) :
				score=100
			else:
				score=0
			
			return (float(score),wanted)
			
	def data_for_question(self, question_type):
		if self.__my_random__ == None:
			self.__my_random__ = random.Random()
		self.__my_random__.seed(self.generate_index(self.magic, self.level, self.problem_id, question_type))
		
		#for adding questions to the database
		if(question_type == "add"):
			return {}
		
		problem=self.problem_id
		
		recieved=self.get_question(problem)
		
		#problem number is returned for use in the submit url
		return {"question":recieved[0].question, "answer":recieved[0].answer, "explanation":recieved[0].explanation, "problem":problem, "use":"question"}
		
		
	def get_question(self, number):
		return TrueFalseQuestion.all().filter('number =', number)
	
	
	def put_question(self, num, quest, ans, exp):
		quest = TrueFalseQuestion(number = num,
								question = quest, 
								answer = ans,
								explanation = exp
							)
		quest.put()