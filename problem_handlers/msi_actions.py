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

class Msi_actions(base_handler.BaseHandler):
  valid_types = [
    "msi_actions",
    "processor_actions", 
	"msi_animation"
  ]

  def make_letter(self,Letter):
   	 a=self.generator.choice(['M','S'])
   	 if a=='M':
   		 j= self.generator.randint(0,2)
   	 else:
   		 j=self.generator.randint(1,3)
   	 return (j,a)
  def set_processorM(self,i,Letter,l):
   		 if i==0:
   			 Letter[i]=(l,self.generator.randint(1,100),' Modified')
   			 Letter[1]= ('','','')
   			 Letter[2]= ('','','')
   		 elif i==1:
   			 Letter[i]=(l,self.generator.randint(1,100),' Modified')
   			 Letter[0]= ('','','')
   			 Letter[2]= ('','','')
   		 elif i ==2:
   			 Letter[i]=(l,self.generator.randint(1,100),' Modified')
   			 Letter[0]= ('','','')
   			 Letter[1]= ('','','')    
   	 
    
  def set_processorS(self,i,MV,Letter,l):
   	 m = self.generator.randint(0,2)
   	 for i in Letter:
   		 Letter[m]=(l,MV,' Shared')
   		 if m==2 :
   			 m=0
   		 else:
   			 m+=1
   	 
  def make_cache(self,A,B,C,MA,MB,MC):
   	 (i1,S1) = self.make_letter(A)
   	 (i2,S2) = self.make_letter(B)
   	 (i3,S3) = self.make_letter(C)
   	 if S1 == 'M':
   		 self.set_processorM(i1,A,"A: ")
   	 if S2 == 'M':
   		 self.set_processorM(i2,B,"B: ")
   	 if S3 == 'M':
   		 self.set_processorM(i3,C,"C: ")
   	 if S1 == 'S':
   		 self.set_processorS(i1,MA,A,"A: ")
   	 if S2 == 'S':
   		 self.set_processorS(i2,MB,B,"B: ")
   	 if S3 == 'S':
   		 self.set_processorS(i3,MC,C,"C: ")
		 
  def solution(self,pro,action,letter):
		a = ''
		if action == 'loads':
			if letter[pro][2]== ' Shared':
				a = 'd'
			if letter[pro][2] == '':
				a = 'a'
			if letter[pro][2] == ' Modified':
				a = 'd'
		if action == 'stores':
			if letter[pro][2] == ' Shared':
				a = 'c'
			if letter[pro][2] == ' Modified':
				a = 'd'
			if letter[pro][2] == '':
				a = 'b'
		return a
  def solution2(self,pro,letter,act):
		a = ''
		if act == 'GETS':
			if letter[pro][2]== ' Shared':
				a = 'false,false,false,false,true'
			if letter[pro][2] == '':
				a = 'false,false,false,false,true'
			if letter[pro][2] == ' Modified':
				a = 'true,true,true,true,false'
		if act == 'GETX':
			if letter[pro][2] == ' Shared':
				a = 'true,false,false,false,false'
			if letter[pro][2] == ' Modified':
				a = 'true,false,true,false,false'
			if letter[pro][2] == '':
				a = 'false,false,false,false,true'
		return a
   		 
  def data_for_question(self,question_type):
	 A4 = 'A: '
   	 B4 = 'B: '
   	 C4 = 'C: '
   	 A4i = self.generator.randint(1,100)
   	 B4i = self.generator.randint(1,100)
   	 C4i = self.generator.randint(1,100)
   	 A =[('A: ','',''),('A: ','',''),('A: ','','')]
   	 B =[('B: ','',''),('B: ','',''),('B: ','','')]
   	 C =[('C: ','',''),('C: ','',''),('C: ','','')]
   	 self.make_cache(A,B,C,A4i,B4i,C4i)
   	 
   	 (pro, pro2, letter, action, act) = map(self.generator.choice, [[0,1,2],[0,1,2],['A','B','C'],['loads','stores'], ['GETS','GETX']])
	 while pro == pro2:
		pro2 = self.generator.randint(0,2)
		
	 answer = ''

		
	 if question_type == "msi_actions":
		type = 0
		if letter == 'A':
			answer = self.solution(pro,action,A)
		if letter == 'B':
			answer = self.solution(pro,action,B)
		if letter == 'C':
			answer = self.solution(pro,action,C)
			
	 if question_type ==  "processor_actions":
		type = 1
		if letter == 'A':
			if A[2][2] == ' Shared' or A[2][2] == ' Modified':
				A[2] = ('','','')
			answer = self.solution2(0,A,act)
			answer += "," + self.solution2(1,A,act) + ","

		if letter == 'B':
			if B[2][2] == ' Shared' or B[2][2] == ' Modified':
				B[2] = ('','','')
			answer = self.solution2(0,B,act)
			answer +=  "," + self.solution2(1,B,act)+","
			
		if letter == 'C':
			if C[2][2] == ' Shared' or C[2][2] == ' Modified':
				C[2] = ('','','')
			answer = self.solution2(0,C,act)
			answer += "," + self.solution2(1,C,act)+","
			
	 if question_type == "msi_animation":
		type = 2
		if letter == 'A':
			answer = self.solution(pro,action,A)
		if letter == 'B':
			answer = self.solution(pro,action,B)
		if letter == 'C':
			answer = self.solution(pro,action,C)
		
			
		
	 description = ['Processor ' + str(pro+1) + ' ' + str(action) + ' ' + str(letter), 'Processor ' + str(3) + ' does a ' + act + ' for ' + letter,'Animate MSI protocol' ]
	 
	 ques = ['Which of the following actions should the processor perform if the action following the above state is: ', '','']
	 
	 choice = ['a) GETS   b) GETX   c) UPGRADE  d) no coherence action','','']
	 
	 
   	 return {"description":description[type],"ques":ques[type], "choice":choice[type],'A4i':A4i,'B4i': B4i,'C4i': C4i,'A4':A4,'B4':B4,'C4':C4,'A1' : A[0][0],'A2' : A[1][0],'A3' :A[2][0],'A1i':A[0][1],'A2i':A[1][1],'A3i':A[2][1],'SharedA':A[0][2],'SharedA2':A[1][2],'SharedA3':A[2][2],'B1' : B[0][0] ,'B2' : B[1][0],'B3' : B[2][0],'B1i' :B[0][1],'B2i' :B[1][1],'B3i' :B[2][1],'SharedB': B[0][2] ,'SharedB2':B[1][2],'SharedB3':B[2][2],'C1':C[0][0],'C2':C[1][0],'C3':C[2][0],'C1i':C[0][1],'C2i':C[1][1],'C3i':C[2][1],'SharedC':C[0][2],'SharedC2':C[1][2],'SharedC3':C[2][2],'answer':answer
   	 }
		
		
	 
  def score_student_answer(self,question_type,question_data,student_answer):
		wanted = self.get_description_string(question_data)
		if wanted == student_answer:
			return (100.0, wanted)
		else:
			return (0.0,wanted)
  def get_description_string(self,description):
	return "%s" % (description['answer'])