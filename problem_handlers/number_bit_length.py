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

import math
import logging
import random
import json

import base_handler

class NumberBitLength(base_handler.BaseHandler):
  __my_random__ = None
  # c - Two's Complement, u - Unsigned
  # l - Length, x - Max, n - Min
  # un was removed from this list, because asking what the minimum number that
  # can be represented in unsigned binary wasn't quite the brain teaser I hoped.
  # Plus, I got sick of typing 0
  valid_types = ["ul","ux","cl","cx","cn"]
  
  def is_valid_type(self, question_type):
    return question_type in self.valid_types

  def get(self, question_type):
    self.get_basics(2)
    if question_type == "random":
        question_type = random.choice(self.valid_types)
        if self.request.get('l', None) == None:
            self.level = random.choice(range(3))

    if self.is_valid_type(question_type):
      if self.request.get('type') == 'json':
        return self.get_grades(question_type)
      question_data = self.data_for_question(question_type)
      submit_data = {"question_type":question_type, "magic":self.magic,
                     "level":self.level, "problem_id":self.problem_id}
      data = {"submit": submit_data, "question":question_data}
      self.add_best_score(data, question_type)
      self.render("bit_length.html", **data)
    else:
      self.response.out.write("Invalid URL")
      
  def post(self, question_type):
    if not self.is_valid_type(question_type):
      return self.response.out.write("Invalid URL")
    self.get_basics(2)
    student_answer = int(self.request.get('answer'))
    question_data = self.data_for_question(question_type)
    if question_data['type'] == 'l':
      wanted = question_data['length']
    elif question_data['type'] == 'x':
      wanted = question_data['upper_bound']
    elif question_data['type'] == 'n':
      wanted = question_data['lower_bound']
    # logging.warn("Wanted: %i" % wanted)
    score = 100.0 if wanted == student_answer else 0.0
    # store the result in the database
    self.put_submission(question_type, int(self.level), score, self.request.get('answer'))

    blob = json.dumps({"score":score, "wanted":wanted})
    self.response.out.write(blob)
    
  # The 'data' for a question should basically be:
  # type -  The question type. Should be either l, x, or n
  # length -  The number of bits. This will be used as the answer if type = 'l'
  #           and as the question if type is 'x' or 'n'
  # number -  [Length only] The 'question' for length questions. This number
  #           is given to the user to find out the minimum number of bits
  #           needed to represent it
  # upper_bound - [Bound only] The upper bound represented by 'length' bits
  # lower_bound - [Bound only] The lower bound represented by 'length' bits
  def data_for_question(self,question_type):
    if self.__my_random__ == None:
        self.__my_random__ = random.Random()
    self.__my_random__.seed(self.generate_index(self.magic, self.level, self.problem_id, question_type))
    binary_type = question_type[0]
    request = question_type[1]
    if request == "l":
      return self.data_for_length_request(binary_type)
    else:
      return self.data_for_bound_request(binary_type,request)
  
  def data_for_length_request(self,binary_type):
    # Find the maximum length we want from this level of question
    length = self.max_length_from_level()
    (lower_bound, upper_bound) = self.range_from_binary_type(binary_type, length)
    # Generate a number in the range represented by the maximum length
    number = self.__my_random__.randint(lower_bound,upper_bound)
    # Minimize the length. That is, if length is 12, but the number generated
    # is 3, that very obviously can fit in less than 12 bits. We need to
    # account for that possibility
    length = self.minimum_bits_for_number(number, binary_type)
    integer_type_string = self.string_from_binary_type(binary_type)
    return {"number":number, "length":length, "type":"l", "type_string":integer_type_string}
  
  def data_for_bound_request(self,binary_type,request_type):
    length = self.__my_random__.randint(2,self.max_length_from_level())
    (lower_bound, upper_bound) = self.range_from_binary_type(binary_type, length)
    binary_type_string = self.string_from_binary_type(binary_type)
    request_type_string = self.string_from_request_type(request_type)
    return {"length":length, "upper_bound":upper_bound, "lower_bound":lower_bound, "type":request_type, "binary_type_string":binary_type_string, "request_type_string":request_type_string}
  
  def max_length_from_level(self):
    if self.level == 2:
      return 12
    if self.level == 1:
      return 8
    return 4
  
  def range_from_binary_type(self, binary_type, length):
    if binary_type == "u":
      return (0, math.pow(2, length) - 1)
    else:
      i = math.pow(2, length-1)
      return (-i, i-1)
  
  def minimum_bits_for_number(self, number, binary_type):
    if binary_type == "u":
      bit = 1
      while (math.pow(2, bit) - 1) < number:
        bit += 1
      return bit
    else: # binary_type == "c"
      bit = 2
      if number < 0:
        while (0 - math.pow(2, bit-1)) > number:
          bit += 1
      else:
        while (math.pow(2, bit-1) - 1) < number:
          bit += 1
      return bit
  
  def string_from_binary_type(self, binary_type):
    if binary_type == "u":
      return "Unsigned Binary"
    else:
      return "Two's Complement Binary"
  
  def string_from_request_type(self, request_type):
    if request_type == "n":
      return "minimum"
    if request_type == "x":
      return "maximum"
    return "length"