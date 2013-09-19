import base_handler
import math
import random
import json
import logging
import sys
import os
import urllib2
from helpers.bitstring import BitArray

class NumberBasedProblem(base_handler.BaseHandler):
  __my_random__ = None
  valid_types = ["abpp+","acpp+","acpn+","acnp+","acnn+", "ac+",
                "abpp-","acpp-","acpn-","acnp-","acnn-", "ac-",
                "nb2d","nb2h","nd2b","nd2h","nd2c","nh2b","nh2d","nc2d",
                "nb2b", "nc2c", "band", "bor", "bnot"]
  signs = {"and":"&", "or":"|", "not":"~"}

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
      return {"format":"b", "string":"%s-bit two's complement binary"%length, "base":"2", "value":self.twos_complement(number, length)}
    
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

  def is_valid_type(self, question_type):
    return question_type in self.valid_types

  def seed_random(self, question_type):
    if self.__my_random__ == None:
        self.__my_random__ = random.Random()
    self.__my_random__.seed(self.generate_index(self.magic, self.level, self.problem_id, question_type))
    
  def asBinary(self, value):
    return self.twos_complement(value, self.length+2)[2:]


  def get_number(self, positive):
    if self.twos_c:
        num_type = "+2'sC" if positive else "-2'sC" 
    else:
        num_type = "+unsigned"
    return self.generate_number(self.length, num_type)

  def get_numbers(self, question_type):
    self.seed_random(question_type)
    self.length = self.length_for_level(self.level)
    if question_type == "ac+":
      question_type = self.__my_random__.choice(self.valid_types[1:5])
    if question_type == "ac-":
      question_type = self.__my_random__.choice(self.valid_types[7:11])

    if question_type[0] == "n":
      given = question_type[1]
      want = question_type[3]
      num_type = "-2'sC" if given == "c" or want == "c" else "+unsigned"
      number = self.generate_number(self.length, num_type)
      given_dff = self.data_for_format(given, number, self.length)
      # If we are translating within the same format it is a sign-extension
      bonus_length = 0 if given != want else self.__my_random__.choice(range(1,4))
      want_dff = self.data_for_format(want, number, self.length + bonus_length)
      return (given_dff, want_dff)
    elif question_type[0] == "a":
      self.twos_c = question_type[1] == "c"
      self.plus = question_type[4] == "+"
      first = self.get_number(question_type[2] == "p")
      second = self.get_number(question_type[3] == "p")
    else:
      first  = self.generate_number(self.length, "+unsigned")
      second = self.generate_number(self.length, "+unsigned")
    return (first, second)

  def maximum_level(self, question_type):
    return 2

  def data_for_question(self, question_type):
    score_type = question_type
    iscomplement = question_type
    (first, second) = self.get_numbers(question_type)
    if question_type[0] == "a":
      data = {"secondb": second, "firstb": first, "qtype": question_type, "first": self.asBinary(first), "second": self.asBinary(second), "sign": "+" if self.plus else "-", "type": "two's complement" if self.twos_c else "unsigned", "length": self.length}
      naive_result = (first+second) if self.plus else (first-second)
      desired_result = self.asBinary(naive_result)
      decimal_desired_result = (naive_result) % (1<<self.length)
      if self.twos_c and decimal_desired_result >= (1 << (self.length-1)):
        decimal_desired_result -= (1 << self.length)
      data["thirdb"] = naive_result
      overflow = decimal_desired_result != naive_result
      data["overflow"] = overflow
      self.add_best_score(data, question_type)
    elif question_type[0] == "b":
      data = {"first": "" if question_type == "bnot" else self.asBinary(first), "second": self.asBinary(second), "length": self.length, "sign":self.signs[question_type[1:]]}
      self.add_best_score(data, question_type)
    else:
      sign_extension = question_type[1] == question_type[3]
      data = {"given":first, "want":second, "prob_type":"Convert" if not sign_extension else {"b":"Zero", "c":"Sign"}[question_type[1]] + " extend", "length": self.length }
      self.add_best_score(data, question_type)
    return data 
          

  def template_for_question(self,question_type):
    if question_type[0] == "n":
    	return self.__class__.__name__ + "/number_representation.html"
    if question_type[0] == "a":
    	return self.__class__.__name__ + "/arithmetic.html"
    else:
    	return self.__class__.__name__ + "/bitwise_logical.html"

  def score_student_answer(self, question_type, question_data, student_answer):
    if question_type[0] == "a":
      question_type = question_data["qtype"]
    (first, second) = self.get_numbers(question_type)
    if question_type[0] == "n":
        score = 100.0 if second['value'] == student_answer else 0.0
        wanted = second['value']
    elif question_type[0] == "b":
    	if question_type == "bnot":
    		result = ~second;
    	else:
    		result = (first & second) if question_type == "band" else (first | second)
    	result = result & ((1 << self.length)-1)
    	desired_result = self.asBinary(result)
        score = 100.0 if (desired_result == student_answer) else 0.0
        wanted = desired_result
    else:
        overflow_answer = student_answer[-1]
        student_answer = student_answer[:-1]
        naive_result = (first+second) if self.plus else (first-second)
        desired_result = self.asBinary(naive_result)
        decimal_desired_result = (naive_result) % (1<<self.length)
        if self.twos_c and decimal_desired_result >= (1 << (self.length-1)):
            decimal_desired_result -= (1 << self.length)
        overflow = decimal_desired_result != naive_result
        score = 50.0 if (desired_result == student_answer) else 0.0
        score += 50.0 if (overflow_answer == "o") == overflow else 0.0
        wanted = desired_result
    return (score, wanted)

  def get_return_data(self, score, wanted, question_data, question_type):
    if question_type[0] == "a":
      return {"score": score, "wanted": wanted, "first": question_data["firstb"], "second": question_data["secondb"], "third": question_data["thirdb"], "overflow": question_data["overflow"]}
    else:
      return {"score": score, "wanted": wanted}


