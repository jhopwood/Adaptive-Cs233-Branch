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

import logging
import random
import json 

import number_based_problem
    
class BitwiseLogical(number_based_problem.NumberBasedProblem):
    valid_types = ["and", "or", "not"]
    signs = {"and":"&", "or":"|", "not":"~"}
    def get_numbers(self, problem_type):
      self.seed_random(problem_type)
      self.length = self.length_for_level(self.level)
      first  = self.generate_number(self.length, "+unsigned")
      second = self.generate_number(self.length, "+unsigned")
      return (first, second)

    def get(self, problem_type):
      self.get_basics(2)
      if problem_type == "random":
          problem_type = random.choice(self.valid_types)
          if self.request.get('l', None) == None:
              self.level = random.choice(range(3))

      if self.is_valid_type(problem_type):
        if self.request.get('type') == 'json':
          return self.get_grades(problem_type)
        (first, second) = self.get_numbers(problem_type)
        submit_data = {"problem_type":problem_type, "magic":self.magic,
                       "level":self.level, "problem_id":self.problem_id}
        data = {"submit": submit_data, "first": "" if problem_type == "not" else self.asBinary(first), 
	        "second": self.asBinary(second), "length": self.length, 
		"sign":self.signs[problem_type]}
	self.add_best_score(data, problem_type)
        self.render("bitwise_logical.html", **data) 
      else:
        self.response.out.write("Invalid URL")

    def post(self, problem_type):
        self.get_basics(2)
        student_answer = self.request.get('answer')
        (first, second) = self.get_numbers(problem_type)
	if problem_type == "not":
	  result = ~second;
	else:
  	  result = (first & second) if problem_type == "and" else (first | second)
	result = result & ((1 << self.length) - 1)   # mask off top bits
        desired_result = self.asBinary(result)
	score = 100.0 if (desired_result == student_answer) else 0.0
        # store the result in the database
        self.put_submission(problem_type, int(self.level), score, student_answer)

        blob = json.dumps({"score":score, "wanted":desired_result, 
                           "first":first, "second":second, 
			   "third":desired_result})
        self.response.out.write(blob)
    
    def is_valid_type(self, problem_type):
      return problem_type in self.valid_types