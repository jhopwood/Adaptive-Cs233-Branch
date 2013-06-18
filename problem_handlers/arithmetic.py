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

import urllib2
import logging #
import random
import json

import number_based_problem

class Arithmetic(number_based_problem.NumberBasedProblem):
    # b - Unsigned, c - Two's Complement; p = positive, n = negative
    valid_types = ["bpp+","cpp+","cpn+","cnp+","cnn+","c+",
                   "bpp-","cpp-","cpn-","cnp-","cnn-","c-",]

    def get_number(self, positive):
      if self.twos_c:
          num_type = "+2'sC" if positive else "-2'sC" 
      else:
          num_type = "+unsigned"
      return self.generate_number(self.length, num_type)

    def get_numbers(self, problem_type):
      self.seed_random(problem_type)
      self.length = self.length_for_level(self.level)
      self.twos_c = problem_type[0] == "c"
      self.plus = problem_type[3] == "+"
      first  = self.get_number(problem_type[1] == "p")
      second = self.get_number(problem_type[2] == "p")
      return (first, second)

    def get(self, problem_type):
      self.get_basics(2)
      score_type = problem_type
      if problem_type == "random":
          problem_type = random.choice(self.valid_types)
          if self.request.get('l', None) == None:
              self.level = random.choice(range(3))

      if problem_type == "c+":
          problem_type = random.choice(self.valid_types[1:5])
      if problem_type == "c-":
          problem_type = random.choice(self.valid_types[7:11])

      if self.is_valid_type(problem_type):
        if self.request.get('type') == 'json':
          return self.get_grades(problem_type)
        (first, second) = self.get_numbers(problem_type)
        submit_data = {"problem_type":problem_type, "magic":self.magic,
                       "level":self.level, "problem_id":self.problem_id, "score_type":urllib2.quote(score_type)}
        data = {"submit": submit_data, "first": self.asBinary(first), 
	        "second": self.asBinary(second), "sign": "+" if self.plus else "-",
		"type": "two's complement" if self.twos_c else "unsigned",
                "length": self.length}
	self.add_best_score(data, score_type)
        self.render("arithmetic.html", **data) 
      else:
        self.response.out.write("Invalid URL")
    
    def post(self, problem_type):
        self.get_basics(2)
        student_answer = self.request.get('answer')
        score_type = self.request.get('score_type')
        # logging.warn("score_type: %s" % (score_type))
	overflow_answer = student_answer[-1]
	student_answer = student_answer[:-1]
        (first, second) = self.get_numbers(problem_type)
	naive_result = (first+second) if self.plus else (first-second)
        desired_result = self.asBinary(naive_result)
	decimal_desired_result = (naive_result) % (1<<self.length)
	if self.twos_c and decimal_desired_result >= (1 << (self.length-1)):
	    decimal_desired_result -= (1 << self.length)
	overflow = decimal_desired_result != naive_result
	score = 50.0 if (desired_result == student_answer) else 0.0
	score += 50.0 if (overflow_answer == "o") == overflow else 0.0
        # store the result in the database
        self.put_submission(score_type, int(self.level), score, student_answer)

        blob = json.dumps({"score":score, "wanted":desired_result, 
                           "first":first, "second":second, 
			   "third":decimal_desired_result, 
			   "overflow":overflow})
        self.response.out.write(blob)
    
    def is_valid_type(self, problem_type):
      return problem_type in self.valid_types