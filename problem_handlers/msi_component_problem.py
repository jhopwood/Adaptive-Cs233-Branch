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
import logging
import random
import json
import itertools
import os

from base_handler import BaseHandler

class MSIComponentProblem(BaseHandler):
  # The valid types are multiplexer and decoder problems
  valid_types = ["mux", "dec"]

  def is_valid_type(self, problem_name):
    return problem_name in self.valid_types

  def maximum_level(self, question_type):
    return 2

  def template_for_question(self,question_type):
    return self.__class__.__name__ + "/msi_representation.html"

  def score_student_answer(self, question_type, question_data, student_answer):
    correct_answer = int(self.get_correct_output(question_data, question_type))
    student_answer = int(student_answer)
    score = 100.0 if correct_answer == student_answer else 0.0
    return (score, correct_answer)

  # Given question data and whether the problem is a mux or decoder problem, 
  # generate the correct output
  def get_correct_output(self, question_data, problem_name):
    question_data = json.loads(question_data)
    # Convert the control signal to decimal
    control_value = self.binary_convert(question_data["selects"])
    # Convert the inputs to decimal
    if problem_name == "dec":
      output = 2 ** control_value
    else:
      input_value = self.binary_convert(question_data["inputs"])
      output = question_data["inputs"][control_value]
    return output

  # Take in a list of binary digits and convert to a number
  def binary_convert(self, lst):
    bin_total = 0
    for i, digit in enumerate(lst):
      bin_total = bin_total + ((2 ** i) * digit)
    return bin_total

  # The 'data' for a question should basically be:
  # lst: A list of inputs and control bits for the decoder/mux
  def data_for_question(self, problem_name):
    lst = []
    lst2 = []
    if problem_name == "mux":
      for i in range(int(self.level) + 1):
        lst2.append(self.generator.choice([0,1]))
      for i in range(2 ** (int(self.level) + 1)):
        lst.append(self.generator.choice([0,1]))
      return json.dumps({"inputs": lst, "selects": lst2})
    else:
      for i in range(int(self.level) + 1):
        lst2.append(self.generator.choice([0,1]))
      return json.dumps({"selects": lst2})
