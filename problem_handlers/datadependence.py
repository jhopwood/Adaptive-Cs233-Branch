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
class Datadependence(base_handler.BaseHandler):
  valid_types = [
    "datadependence",
	"mips_datadependence"
  ]
 #making the equation question
  def make_question(self):
	int1 = self.generator.randint(1,100)
   	int2 = self.generator.randint(1,100)
	var = ['x','y','z','m','j','t']
	(char1,char2,char3) = map(self.generator.choice,[var,var,var])
	while char1 == char2 or char1 == char3 or char2 == char3:
		char2 = self.generator.choice(var)
		char3 = self.generator.choice(var)
	opp = ['+','-','*','/']
	opp = self.generator.choice(opp)
	question = ([char1, ' = ', str(self.generator.choice([int1,char2])), ' ' , opp , ' ' ,  str(self.generator.choice([int2,char3]))])
	return question
# making the mips question
  def make_question2(self):
	int1 = self.generator.randint(1,100)
	offset = self.generator.choice([2,4,8,16])
	inst = ['lw','sw','add','sub','bne','beq']
	reg = ['$t0','$t1','$t2','$t3','$t4','$t5','$t6','$t7','$t8','$t9']
	reg2 = ['$t0','$t1','$t2','$t3','$t4','$t5','$t6','$t7','$t8','$t9']
	reg3 = ['$t0','$t1','$t2','$t3','$t4','$t5','$t6','$t7','$t8','$t9']
	(instruction,register,register2,register3) = map(self.generator.choice,[inst,reg,reg2,reg3])
	while register == register2:
			register2= self.generator.choice(['$t0','$t1','$t2','$t3','$t4','$t5','$t6','$t7','$t8','$t9'])
	if(instruction == 'add' or instruction == 'sub'):
		question = ([instruction,'  ' , register , ' , ' , register2 , ' , ' ,  str(self.generator.choice([register3,int1]))])
	if(instruction == 'lw' or instruction == 'sw'):
		question = ([instruction,'  ' , register , ' , ' , str(offset),'(', register2 ,')'])
	elif instruction == 'bne' or instruction == 'beq' :
		question = ([instruction,'  ' , register , ' , ' ,str(self.generator.choice([register2,int1])), ', skip'])
	return question
# this function counts all the nodes/registers/variables up to the first node/register/variable in line i
  def num_var_up_to(self,i,stop,q,q_type):
		count = 0
		j=0
		if(q_type == 'mips_datadependence'):
			while j <= i:
				x =('$t0','$t1','$t2','$t3','$t4','$t5','$t6','$t7','$t8','$t9')
				for y in xrange(0,len(q[j])):
					if j == i:
						if(y==stop):
							break;
					if q[j][y] in x:
						count+=1
				j+=1
		elif(q_type == 'datadependence'):
			while j <= i:
				x = ('x','y','z','m','j','t')
				for y in xrange(0,len(q[j])):
					if j==i:
						if(y==stop):
							break;
					if q[j][y] in x:
							count += 1
				j+=1
		return count
#validates the answer and appends the number/name of the node to an array.		
  def validate_answer(self,q,q_type,des):
		ans =[]
		for i in q:
				for j in q:
					if j>i:
						if(q_type =='datadependence'):
							if(des == 'anti-dependencies'):
								for y in xrange(2,len(q[i])):
									if  q[i][y] == q[j][0]:
										a=self.num_var_up_to(i,y,q,q_type)
										b=self.num_var_up_to(j,0,q,q_type)
										ans.append((a,b))
							if(des == 'output dependencies'):
								if  q[i][0] == q[j][0]:
									a=self.num_var_up_to(i,0,q,q_type)
									b=self.num_var_up_to(j,0,q,q_type)
									ans.append((a,b))
							if(des == 'true dependencies'):	
								if q[i][0] == q[j][0]:
									break
								for y in xrange(2,len(q[j])):
									if  q[i][0] == q[j][y]:
										a=self.num_var_up_to(i,0,q,q_type)
										b=self.num_var_up_to(j,y,q,q_type)
										ans.append((a,b))
						if(q_type == 'mips_datadependence'):
							if(des == 'anti-dependencies'):
								if(q[j][0]  in ('lw','add','sub')):
									for y in xrange(0,len(q[i])):
										if q[i][0] in ('add','sub','lw'):
											if  y>2:
												if  q[i][y] == q[j][2]:
													a=self.num_var_up_to(i,y,q,q_type)
													b=self.num_var_up_to(j,2,q,q_type)
													ans.append((a,b))
										if(q[i][0] in ('bne','beq','sw')):
											if  q[i][y] == q[j][2]:
												a=self.num_var_up_to(i,y,q,q_type)
												b=self.num_var_up_to(j,2,q,q_type)
												ans.append((a,b))
							if(des == 'output dependencies'):
								x=('lw','add','sub')
								if (q[i][0] in x) and (q[j][0] in x):
									if  q[i][2] == q[j][2]:
										a=self.num_var_up_to(i,2,q,q_type)
										b=self.num_var_up_to(j,2,q,q_type)
										ans.append((a,b))
							if(des == 'true dependencies'):
								if(q[i][0] in ('lw','add','sub')):
									if q[i][2] == q[j][2]:
										break
									for y in xrange(2,len(q[j])):
										if(q[j][0] in ('bne','beq','sw')):
											if  q[i][2] == q[j][y]:
												a=self.num_var_up_to(i,2,q,q_type)
												b=self.num_var_up_to(j,y,q,q_type)
												ans.append((a,b))
										elif(q[j][0] in ('add','sub','lw')):
											if  q[i][2] == q[j][y]:
												a=self.num_var_up_to(i,2,q,q_type)
												b=self.num_var_up_to(j,y,q,q_type)
												ans.append((a,b))
		return ans
  def make_string(self,q):
		a = ''
		a = a.join(q)
		return a
  def maximum_level(self, question_type):
		return 3
  def data_for_question(self,question_type):
	 num_questions = self.generator.randint(4,6)
	 des = ['true dependencies','anti-dependencies','output dependencies']
	 description=''
	 if self.level == 1:
		description = 'output dependencies'
	 if self.level == 2:
		description = 'true dependencies'
	 if self.level == 3:
		description = 'anti-dependencies'
	 if self.level == 0:
		description = self.generator.choice(des)
	 ans =[]
	 if description == 'output dependencies':
		if (question_type == "datadependence"):
			while not(len(ans)  in(3,4)):
				q={0:self.make_question(),1:self.make_question(),2:self.make_question(),3:self.make_question(),4:self.make_question(),5:self.make_question(),6:self.make_question()}
				ans = self.validate_answer(q,question_type,description)
				a=len(ans)
				ans.append(a)
		elif (question_type == "mips_datadependence"):
			while not(len(ans) in(3,4)):
				q={0:self.make_question2(),1:self.make_question2(),2:self.make_question2(),3:self.make_question2(),4:self.make_question2(),5:self.make_question2(),6:self.make_question2()}
				ans = self.validate_answer(q,question_type,description)
				a=len(ans)
				ans.append(a)
	 else:
		 while len(ans) <= 5:
			if (question_type == "datadependence"):
				q={0:self.make_question(),1:self.make_question(),2:self.make_question(),3:self.make_question(),4:self.make_question(),5:self.make_question(),6:self.make_question()}
				ans = self.validate_answer(q,question_type,description)
				a=len(ans)
				ans.append(a)
			elif (question_type == "mips_datadependence"):
				q={0:self.make_question2(),1:self.make_question2(),2:self.make_question2(),3:self.make_question2(),4:self.make_question2(),5:self.make_question2(),6:self.make_question2()}
				ans = self.validate_answer(q,question_type,description)
				a=len(ans)
				ans.append(a)
	 question0 = self.make_string(q[0])
	 question1 = self.make_string(q[1])
	 question2 = self.make_string(q[2])
	 question3 = self.make_string(q[3])
	 question4 = self.make_string(q[4])
	 question5 = self.make_string(q[5])
	 question6 = self.make_string(q[6])
   	 return {'description':description,'question0':question0, 'question1':question1, 'question2':question2, 'question3':question3, 'question4':question4, 'question5':question5, 'question6':question6, 'question_type':question_type, 'a1':ans}
  def score_student_answer(self,question_type,question_data,student_answer):
		wanted = self.get_description_string(question_data)
		length = len(student_answer)
		length2= len(wanted)
		ans = 0
		wrong = 0
		i=0
		tup = []
		wtup =[]
		#looking at student answer and making a tupple from its ints
		while i < length:
			if student_answer[i] == '(': 
				if i+6 < length:
					if student_answer[i+6] == ')':
						if(student_answer[i+2].isdigit()):
							tup.append((student_answer[i+1]+student_answer[i+2],student_answer[i+4]))
						else:
							tup.append((student_answer[i+1],student_answer[i+4]+student_answer[i+5]))
				if i+7 < length:
					if student_answer[i+7] == ')':
						tup.append((student_answer[i+1]+student_answer[i+2],student_answer[i+5]+student_answer[i+6]))
				if student_answer[i+5]==')':
					tup.append((student_answer[i+1],student_answer[i+4]))
			i+=1
		j=1
		#looking at wanted and making a tupple from its ints 
		while j < length2:
			if wanted[j] == '(' : 
				if wanted[j+6] == ')':
					if(wanted[j+2].isdigit()):
						wtup.append((wanted[j+1]+wanted[j+2],wanted[j+4]))
					else:
						wtup.append((wanted[j+1],wanted[j+4]+wanted[j+5]))
				if wanted[j+7] == ')':
					wtup.append((wanted[j+1]+wanted[j+2],wanted[j+5]+wanted[j+6]))
				if wanted[j+5]==')':
					wtup.append((wanted[j+1],wanted[j+4]))
			j+=1
		#checking if the student answer is the right answer 
		for x in xrange(0,len(tup)):
			for y in xrange(0,len(wtup)):
				if tup[x] == wtup[y]:
					ans += 1
		wrong = len(tup)-ans
		if(wanted[len(wanted)-3].isdigit()):
			ab = wanted[len(wanted)-3]+wanted[len(wanted)-2]
		else:
			ab = wanted[len(wanted)-2]
		data =.25+(.75*(ans/float(ab))-(.1*(wrong)))
		score = max([data,0])
		return (round(float(score*100),2),wtup)
  def get_description_string(self,description):
	return "%s"% (description['a1'])