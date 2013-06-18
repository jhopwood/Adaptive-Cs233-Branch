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
from models import Proficiency

correct=1
incorrect=1

class AdaptiveMath(base_handler.BaseHandler):
	__my_random__ = None
	valid_types = ["math"]
	
	#TODO
	#put the formula into the proficiency alter method
	#make a baseclass handler for adaptive problems
	#reorginize html files into base and extended
	#expand for multiple question types
	#Refactor
	
	def get(self, question_type):
		self.get_basics(self.maximum_level(question_type))
		if self.is_valid_type(question_type):
			if self.request.get('type') == 'json':
				return self.get_grades(question_type)
			
			#gets the proficiency of the student or initializes it if no records exist
			entry = self.get_student_proficiency(self.magic, question_type)
			if entry.count() == 0:
				prof = 1.00
				self.put_proficiency(question_type, 1.0)
			else:
				prof=entry[0].proficiency
			
			
			submit_data = { "question_type":question_type, "magic":self.magic,
							"level":self.level, "problem_id":self.problem_id}
			data = {"submit": submit_data, "question":{"button":1.0}, "proficiency":prof, "type":"get", "count":entry.count()}
			self.render(self.template_for_question(question_type),**data)
		else:
			self.response.out.write("Invalid URL")
	
	def post(self, question_type):
		if not self.is_valid_type(question_type):
			return self.response.out.write("Invalid URL")
			
		if self.request.get('type')=="question request":
			self.get_basics(self.maximum_level(question_type))
			
			entry = self.get_student_proficiency(self.magic, question_type)
			prof=entry[0].proficiency
			
			question_data = self.data_for_question(question_type)
			submit_data = { "question_type":question_type, "magic":self.magic,
							"level":self.level, "problem_id":self.problem_id}
			data = {"submit": submit_data,"question":question_data, "proficiency":prof, "type":"post"}
			self.render(self.template_for_question(question_type),**data)
		else:
			self.get_basics(self.maximum_level(question_type))
			student_answer = self.request.get('answer')
			self.initialize_random_number_generator(question_type)
			question_data = self.data_for_question(question_type)
			(score,wanted) = self.score_student_answer(question_type,question_data,student_answer)
			self.alter_proficiency(question_type, score)
			# store the result in the database
			self.put_submission(question_type, 0, score, self.request.get('answer'))
			blob = json.dumps(self.get_return_data(score, wanted))
			self.response.out.write(blob)
	
	#gets the students proficiency for a problem type should have latest entry as 0th index
	def get_student_proficiency(self, magic, prob_type):
		return Proficiency.all().filter('student_magic_number =', str(magic)).filter('question_type = ', str(prob_type)).order('-time')
	
	#can be implemented differently for partial credit problems
	def alter_proficiency(self, question_type, score):
		if score == 100:
			entry = self.get_student_proficiency(self.magic, question_type)
			prof=entry[0].proficiency
			prof=prof+correct
			self.put_proficiency(question_type, prof)
		else:
			entry = self.get_student_proficiency(self.magic, question_type)
			prof=entry[0].proficiency
			prof=prof-incorrect
			prof=max(prof,0.0)
			self.put_proficiency(question_type, prof)
	
	#adds a students new proficiency to the database
	def put_proficiency(self, type, prof):
		prof = Proficiency(student_magic_number = self.magic,
								question_type = type, proficiency = prof)
		prof.put()
	
	#gets the max level of the question again used in baseclass
	def maximum_level(self, question_type):
		return 10
	
	#used by the basehelper to render the page
	def template_for_question(self, question_type):
		return "adaptivemath.html"
	
	#used by the basehelper to grade the students score
	def score_student_answer(self,question_type,question_data,student_answer):
		wanted = self.data_for_question(question_type)
		answer = student_answer
		if (wanted["answer"] == float(answer)):
			score = 100
		else:
			score = 0
		
		return (float(score),wanted)
		
	#gets the data returns it as {"number1": num1, "number2":num2, "answer":ans, "proficiency":proficiency}
	def data_for_question(self, question_type):
		if self.__my_random__ == None:
			self.__my_random__ = random.Random()
		self.__my_random__.seed(self.generate_index(self.magic, 0, self.problem_id, question_type))
		
		#get the adjusted level based on the button pressed and their proficiency rating
		prof=self.get_adjusted_level(question_type)
		
		#generates num1 and num2 to be added
		num1=exponent = self.__my_random__.randint(1,10)*max(prof,1)
		num2=exponent = self.__my_random__.randint(1,10)*max(prof,1)
		
		ans = num1 + num2
			
		return {"number1": num1, "number2":num2, "answer":ans, "button":self.request.get('button')}
	
	#gets student proficiency and then adjusts level based on which button was pressed
	def get_adjusted_level(self, question_type):
		entry = self.get_student_proficiency(self.magic, question_type)
		prof=entry[0].proficiency
		
		prof=prof+float(self.request.get('button'))
		
		prof=max(prof,0.0)
		prof=min(prof,float(self.maximum_level(question_type)))
		
		return prof
		
	
 