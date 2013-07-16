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



class AdaptiveMath(adaptive_base_handler.AdaptiveBaseHandler):
	__my_random__ = None
	valid_types = ["math","add","subtract"]
	level_matrix=[
				( {'index':0 , 'type':"add"     , 'level':1, 'base':-1, 'prob':1} ),
				( {'index':1 , 'type':"add"     , 'level':2, 'base':-1, 'prob':1} ),
				( {'index':2 , 'type':"subtract", 'level':1, 'base':-1, 'prob':1} ),
				( {'index':3 , 'type':"subtract", 'level':2, 'base':0 , 'prob':1} ),
				( {'index':4 , 'type':"add"     , 'level':3, 'base':0 , 'prob':1} ),
				( {'index':5 , 'type':"multiply", 'level':1, 'base':1 , 'prob':1} ),
				( {'index':6 , 'type':"multiply", 'level':2, 'base':2 , 'prob':1} ),
				( {'index':7 , 'type':"divide"  , 'level':1, 'base':3 , 'prob':1} ),
				( {'index':8 , 'type':"subtract", 'level':3, 'base':3 , 'prob':1} ),
				( {'index':9 , 'type':"divide"  , 'level':2, 'base':4 , 'prob':1} ),
				( {'index':10, 'type':"multiply", 'level':3, 'base':4 , 'prob':1} ),
				( {'index':11, 'type':"divide"  , 'level':3, 'base':5 , 'prob':1} ) ]
				
	weight_matrix=[
					[1,0,0,0,0,0,0,0,0,0,0,0],
					[0,1,0,0,0,0,0,0,0,0,0,0],
					[0,0,1,0,0,0,0,0,0,0,0,0],
					[0,0,0,1,0,0,0,0,0,0,0,0],
					[0,0,0,0,1,0,0,0,0,0,0,0],
					[0,0,0,0,0,1,0,0,0,0,0,0],
					[0,0,0,0,0,0,1,0,0,0,0,0],
					[0,0,0,0,0,0,0,1,0,0,0,0],
					[0,0,0,0,0,0,0,0,1,0,0,0],
					[0,0,0,0,0,0,0,0,0,1,0,0],
					[0,0,0,0,0,0,0,0,0,0,1,0],
					[0,0,0,0,0,0,0,0,0,0,0,1]
					]
	
	#this array's size will be the number of questions in the levelmatrix
	default_rw=[0,0,0,0,0,0,0,0,0,0,0,0]
	#TODO
	#Refactor
	#make level matrix type, level, base mastery, height
	
	
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
			self.default_rw[question_data['index']]=self.default_rw[question_data['index']]+1
		else:
			score = 0
			self.default_rw[question_data['index']]=self.default_rw[question_data['index']]-1
		
		return (float(score),wanted)
		
	#gets the data returns it as {"number1": num1, "number2":num2, "answer":ans, "button":self.request.get('button'), "sign":"-", "typ":typ, "lev":lev}
	#, "typ":typ, "lev":lev, "wr":rightwrong}  are for debugging purposes
	def data_for_question(self, question_type):
		if self.__my_random__ == None:
			self.__my_random__ = random.Random()
		self.__my_random__.seed(self.generate_index(self.magic, 0, self.problem_id, question_type))
		
		#get the adjusted level based on the button pressed and their proficiency rating
		prof = self.get_adjusted_level(question_type, self.get_container())
		(typ, lev, index)=self.newproblem_selector(prof)
		
		if typ == "subtract":	
			#generates num1 and num2 to be subtracted
			num1 = self.__my_random__.randint(1,10)*max(lev,1)
			num2 = self.__my_random__.randint(1,10)*max(lev,1)
			
			ans = num1 - num2
				
			return {"number1": num1, "number2":num2, "answer":ans, "button":self.request.get('button'), "sign":"-", "typ":typ, "lev":lev, "wr":self.default_rw, "index":index}
		elif typ == "add":
			#generates num1 and num2 to be added
			num1 = self.__my_random__.randint(1,10)*max(lev,1)
			num2 = self.__my_random__.randint(1,10)*max(lev,1)
			
			ans = num1 + num2
				
			return {"number1": num1, "number2":num2, "answer":ans, "button":self.request.get('button'), "sign":"+", "typ":typ, "lev":lev, "wr":self.default_rw, "index":index}
		elif typ == "multiply":
			#generates num1 and num2 to be multiplied
			num1 = self.__my_random__.randint(1,10)*max(lev,1)
			num2 = self.__my_random__.randint(1,10)*max(lev,1)
			
			ans = num1 * num2
				
			return {"number1": num1, "number2":num2, "answer":ans, "button":self.request.get('button'), "sign":"X", "typ":typ, "lev":lev, "wr":self.default_rw, "index":index}
		elif typ == "divide":
			#generates num1 and num2 to be a bug exists when it divides to a repeating decimal at this point this is not important
			num1 = self.__my_random__.randint(1,10)*max(lev,1)
			num2 = self.__my_random__.randint(1,10)*max(lev,1)
			
			ans = float(num1) / float(num2)
			
			return {"number1": num1, "number2":num2, "answer":ans, "button":self.request.get('button'), "sign":"/", "typ":typ, "lev":lev, "wr":self.default_rw, "index":index}
		
	
	#will eventually provide the question type and level to the data_for_question method
	def newproblem_selector(self, prof):
		#gets array of rights and wrongs and fits the values to the curve
		weighted_rw = self.get_weight(12)
			
		holder=[]
		probsum=-1
		indexer=0
		for i in self.level_matrix:
			if i['base'] < prof:
				holder.append(i)
				probsum=probsum+weighted_rw[indexer]
			indexer=indexer+1
		
		magic_num=self.__my_random__.uniform(0.0,float(probsum))
		magi=magic_num
		
		indexer=0
		for i in holder:
			magic_num=magic_num-weighted_rw[indexer]
			indexer=indexer+1
			if(magic_num < 0):
				return (i['type'], int(i['level']), i['index'] )
			
	def get_right_wrong(self):
		#gets string from datastore and converts it an array of strings
		entry = self.get_student_proficiency(self.magic, self.get_container())
		rightwrong = entry[0].right_wrong
		rightwrong = rightwrong.split(',')
		
		#converts the array values to ints
		if(entry[0].right_wrong != ""):
			for i in range(0,len(rightwrong)):
				rightwrong[i]=int(rightwrong[i])
		
		#assigns the global to be the true right wrong array.  did this for ease of storage in database
		self.default_rw=rightwrong
		
		return rightwrong
		
		
		
	def get_weight( self, n):
		res = []
		rightwrong = self.get_right_wrong()
		
		for i in range(n):
			temp = 0
			for j in range(n):
				temp = temp+self.weight_matrix[i][j]*rightwrong[j]
				
			res.append(temp)
			
		for i in range(n):	
			res[i] = self.curve_fit(res[i])
			
		return res	
		
		
		
		
		
		
 