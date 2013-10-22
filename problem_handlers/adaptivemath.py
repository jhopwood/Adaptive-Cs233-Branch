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
import ast
import adaptive_base_handler
import number_based_problem

#must import the handlers to be used if form from (file name) import (class name)
from add import Addition
from sub import Subtraction
from mul import Multiplication
from div import Division
from parity import Parity
from true_false import TrueFalse

from models import Proficiency



class AdaptiveMath(adaptive_base_handler.AdaptiveBaseHandler):
	__my_random__ = None
	valid_types = ["math", "parity"]
	# TODO
	# Refactor
	# No chance for last problem
	# move matrix_from_file to abh along with the imports
	

	# get the information on problems from a file
	def matrix_from_file(self, question_type):
		# this gets the level matrix from a text file have been told eval is dangerous
		location = 'Adaptive_Lists/' + question_type + '.txt'
		logging.warn(location)
		s = open(location, 'r').read()
		holder = eval(s)
		self.level_matrix = holder['level']
		self.weight_matrix = holder['weight']
		self.default_rw = holder['default']
		
		
	#gets the max level of the question again used in baseclass
	def maximum_level(self, question_type):
		return 100
	
	#used by the basehelper to grade the students score also modifies the right_wrong array
	def score_student_answer(self, question_type, question_data, student_answer):
		wanted = question_data
		answer = student_answer
		
		#giving the new class a the self objects of the current class
		classtype = question_data['class']
		tester = classtype(self)
		tester.magic = self.magic
		tester.problem_id = question_data['id']
		tester.level = question_data['lev']
		
		(tscore,twanted)=tester.score_student_answer(question_data['typ'], wanted, answer)
		
		if (tscore == 100):
			if(classtype == TrueFalse):
				self.default_rw[question_data['index']]=self.default_rw[question_data['index']]+100
			else:
				self.default_rw[question_data['index']]=self.default_rw[question_data['index']]+1
		else:
			self.default_rw[question_data['index']]=self.default_rw[question_data['index']]-1
		
		return (float(tscore),twanted)
		
	#gets the data returns it as {"number1": num1, "number2":num2, "answer":ans, "button":self.request.get('button'), "sign":"-", "typ":typ, "lev":lev}
	#, "typ":typ, "lev":lev, "wr":rightwrong}  are for debugging purposes
	def data_for_question(self, question_type):
		if self.__my_random__ == None:
			self.__my_random__ = random.Random()
		self.__my_random__.seed(self.generate_index(self.magic, 0, self.problem_id, question_type))

		#gets the matrixes of classes to use
		self.matrix_from_file(question_type)
		
		#get the adjusted level based on the button pressed and their proficiency rating
		prof = self.get_adjusted_level(question_type, question_type)
		(typ, lev, index, cla, id)=self.newproblem_selector(prof, question_type)
		
		#giving the new class a the self objects of the current class
		classtype = cla
		tester = classtype(self)
		tester.magic = self.magic
		tester.problem_id = id
		tester.level = lev
		
		tester.generator.seed(self.generate_index(self.magic, self.level, self.problem_id, question_type))

		
		#gets question data from subclass
		ret=tester.data_for_question(typ)
		
		#adds on usefull information 
		ret.update({"button":self.request.get('button'), "typ":typ, "lev":lev, "wr":self.default_rw, "index":index, "class":cla, "id":id})
			
		return ret
	
	
	#will eventually provide the question type and level to the data_for_question method
	def newproblem_selector(self, prof, question_type):
		#gets array of rights and wrongs and fits the values to the curve
		weighted_rw = self.get_weight(len(self.default_rw), question_type)
			
		holder=[]
		probsum=-1
		indexer=0
		for i in self.level_matrix:
			if i['base'] < prof:
				holder.append(i)
				probsum=probsum+weighted_rw[indexer]
			indexer=indexer+1
		
		magic_num=self.__my_random__.uniform(0.0,float(probsum))
		
		indexer=0
		for i in holder:
			magic_num=magic_num-weighted_rw[indexer]
			indexer=indexer+1
			if(magic_num < 0):
				return (i['type'], int(i['level']), i['index'],i['class'], i['id'] )
			
	def get_right_wrong(self, question_type):
		#gets string from datastore and converts it an array of strings
		entry = self.get_student_proficiency(self.magic, question_type)
		rightwrong = entry[0].right_wrong
		rightwrong = rightwrong.split(',')
		
		#converts the array values to ints
		if(entry[0].right_wrong != ""):
			for i in range(0,len(rightwrong)):
				rightwrong[i]=int(rightwrong[i])
		
		#assigns the global to be the true right wrong array.  did this for ease of storage in database
		self.default_rw=rightwrong
		
		return rightwrong
		
		
	#n is the size of the level matrix   TODO look at generalizing this method to not need an N	
	def get_weight( self, n, question_type):
		res = []
		rightwrong = self.get_right_wrong(question_type)
		
		for i in range(n):
			temp = 0
			for j in range(n):
				temp = temp+self.weight_matrix[i][j]*rightwrong[j]
				
			res.append(temp)
			
		for i in range(n):	
			res[i] = self.curve_fit(res[i])
			
		return res	
		
		
		
		
		
		
 