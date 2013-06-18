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
import sys
import os
import random

from helpers.bitstring import BitArray

import base_handler

class NumberBasedProblem(base_handler.BaseHandler):
    __my_random__ = None
    
    def generate_number(self, length, num_type):
      if num_type == "-2'sC":
        lower_bound = 0 - (math.pow(2, length - 1))
        return self.__my_random__.randint(lower_bound,0)
      elif num_type == "+2'sC":
        upper_bound = math.pow(2, length-1) - 1
        return self.__my_random__.randint(0,upper_bound)
      else: # num_type == "+unsigned":
        upper_bound = math.pow(2, length) - 1
        return self.__my_random__.randint(0,upper_bound)
    
    def length_for_level(self, level):
      if level == 2:
        return self.__my_random__.choice(range(9,12))
      if level == 1:
        return self.__my_random__.choice(range(6,9))
      return self.__my_random__.choice(range(3,6))

    
    def data_for_format(self, format, number, length):
      if format == "b":
        return {"format":format, "string":"%s-bit unsigned binary"%length, "base":"2", "value":self.binary(number, length+1)[1:]}
      if format == "d":
        return {"format":format, "string":"decimal", "base":"10", "value":self.decimal(number, length)}
      if format == "h":
        return {"format":format, "string":"%s-digit hexadecimal"%((length+3)/4), "base":"16", "value":self.hex(number, length)}
      if format == "c":
        return {"format":format, "string":"%s-bit two's complement binary"%length, "base":"2", "value":self.twos_complement(number, length)}
    
    def binary(self, number, length):
      return BitArray(int=number, length=length).bin
      
    def decimal(self, number, length):
      return str(number)
      
    def hex(self, number, length):
      # round length up to next multiple of 4.
      rounded_length = 4 + length&~3
      return BitArray(int=number, length=rounded_length).hex[-((length+3)/4):]
      
    def twos_complement(self, number, length):
      return BitArray(int=number, length=length).bin

    # FIXME: This function assumes that twos complement numbers are negative,
    # which is always true at time of writing (the generator only generates
    # negatives for twos comlement), but may not be true in the future.
    def sign_extend(self, binary_string, want_format):
      # We need to check the format. If it is Binary then we want to add 0s
      # until self.length, if it is Two's Complement we want to add ones until
      # we get to self.length
      #
      # If the string is larger than self.length, we want to equalize it down
      # to self.length. We will ONLY do that though if they are the padding
      # characters (0 for binary 1 for TC).
      padding_character = None
      if want_format == "b":
        padding_character = "0"
      if want_format == "c":
        padding_character = "1"
      # If the format is wrong, we just return the normal string
      if padding_character == None:
        return binary_string
      if len(binary_string) > self.length:
        while len(binary_string) != self.length:
          if binary_string[0] == padding_character:
            binary_string = binary_string[1:]
          else:
            return binary_string
      if len(binary_string) < self.length:
        while len(binary_string) != self.length:
          binary_string = padding_character + binary_string
      return binary_string

    def is_valid_type(self, conversion_type):
      return conversion_type in self.valid_types

    def seed_random(self, problem_type):
      if self.__my_random__ == None:
          self.__my_random__ = random.Random()
      self.__my_random__.seed(self.generate_index(self.magic, self.level, self.problem_id, problem_type))
    
    def asBinary(self, value):
      return self.twos_complement(value, self.length+2)[2:]