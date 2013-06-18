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
import sys
import os
import random
import json

import number_based_problem

class NumbersConversion(number_based_problem.NumberBasedProblem):
    # b - Unsigned Binary, d - Decimal, h - Hex, c - Two's Complement
    valid_types = ["b2d","b2h","d2b","d2h","d2c","h2b","h2d","c2d",
                   "b2b", "c2c"]

    def get_number(self, conversion_type):
      self.seed_random(conversion_type)
      self.length = self.length_for_level(self.level)
      given = conversion_type[0]
      want = conversion_type[2]
      # We only want to generate negative numbers if they request a twos complement
      num_type = "-2'sC" if given == "c" or want == "c" else "+unsigned"
      number = self.generate_number(self.length, num_type)
      given_dff = self.data_for_format(given, number, self.length)
      # If we are translating within the same format it is a sign-extension
      bonus_length = 0 if given != want else self.__my_random__.choice(range(1,4))
      want_dff = self.data_for_format(want, number, self.length + bonus_length)
      return (given_dff, want_dff)

    def get(self, conversion_type):
      self.get_basics(2)
      if conversion_type == "random":
          conversion_type = random.choice(self.valid_types)
          if self.request.get('l', None) == None:
              self.level = random.choice(range(3))

      if self.is_valid_type(conversion_type):
        if self.request.get('type') == 'json':
          return self.get_grades(conversion_type)
        (given_dff, want_dff) = self.get_number(conversion_type)
        submit_data = {"conversion_type":conversion_type, "magic":self.magic,
                       "level":self.level, "problem_id":self.problem_id}
        sign_extension = conversion_type[0] == conversion_type[2]
        data = {"submit": submit_data, "given": given_dff, "want":  want_dff,
                "prob_type":"Convert" if not sign_extension else {"b":"Zero", "c":"Sign"}[conversion_type[0]] + " extend" }
	self.add_best_score(data, conversion_type)
        self.render("number_representation.html", **data) #resentation
      else:
        self.response.out.write("Invalid URL")
    
    def post(self, conversion_type):
      self.get_basics(2)
      student_answer = self.request.get('answer').lower()
      (given_dff, want_dff) = self.get_number(conversion_type)
      # score = 100.0 if want_dff['value'] == self.sign_extend(student_answer,want_dff['format']) else 0.0
      score = 100.0 if want_dff['value'] == student_answer else 0.0
      # store the result in the database
      self.put_submission(conversion_type, int(self.level), score, student_answer)

      blob = json.dumps({"score":score, "wanted":want_dff['value']})
      self.response.out.write(blob)