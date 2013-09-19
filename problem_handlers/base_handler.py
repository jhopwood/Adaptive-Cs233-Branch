#!/usr/bin/env python
# TODO: Should this license be here? I mean, is the code we write copywright Google?
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
import webapp2
import sys
import os
import re
import jinja2
import json
import time
import zlib
import random

from models import Submission

from google.appengine.ext import db
from google.appengine.api import memcache

template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

def int_convert(s, default,
                minimum=sys.float_info.min, maximum=sys.float_info.max):
    if isinstance(s,int):
        return s
    if s.isdigit():
        val = int(s)
        if val >= minimum and val <= maximum:
            return val
    return default

class BaseHandler(webapp2.RequestHandler):
    
    # List of all valid question types for a problem.
    # This should be overriden for any subclass using the default get and post
    # methods
    valid_types = []
    
    # The random number generator 'generator' should be used whenever the
    # generated value is going to be used in a question.
    generator = random.Random()
    
    def initialize_random_number_generator(self,question_type):
      """
      Seeds the random number generator based on the request parameters
      
      This allows the generator to return the same value in different requests.
      This is useful so that we don't need to store the answer somewhere when
      we generate a random problem. Instead, we just generate the same problem
      again, and determine if the student is correct or not.
      """
      self.generator.seed(self.generate_index(self.magic, self.level, self.problem_id, question_type))
    
    def maximum_level(self, question_type):
      """
      The maximum level for a given problem type
      
      Defaults to 2, but should be implemented by any subclass using the default
      'get' and 'post' methods that want more than 3 levels.
      """
      return 2
      
    def is_valid_type(self, question_type):
      """
      Checks to see if the user entered a valid question type.
      
      The default implementation just checks to see whether the question type
      parameter is in the 'valid_types' array which any subclass should override
      """
      return question_type in self.valid_types
      
    def template_extra_functions(self):
      """
      Returns the functions that should be added to the jinja temlate
      
      The default implementation is empty. Subclasses which would like to add
      extra functions for use in the template should return a list of function 
      objects to be added.
      """
      return []
      
    def data_for_question(self, question_type):
      """
      Generates the data that will be displayed for the user to answer. For
      example, a 'mips representation' question could have data like
      
      {"mips":"sll $0, $0, 0", "binary": "00000000000000000000000000000000"}
      
      This method will be called both when the question should be displayed for
      the user, and when the user submits a response, and as such this method
      should generate all that is needed for both displaying and answering a
      particular type of problem.
      
      This should be implemented by any subclass using the default 'get' and
      'post' methods.
      """
      return {}
      
    def score_student_answer(self,question_type,question_data,student_answer):
      """
      Checks to see whether the answer that the student gave was acceptable or
      not.
      
      Retuns a tuple. The first element is the score that the student received
      for their answer, and the second element is the 'correct' answer
      """
      return (0.0,"")
      
    def template_for_question(self,question_type):
      """
      Returns the path to template to render relative to the templates directory
      
      Does not need to be overridden by subclasses, but can be if the author 
      would like more control of their templates
      """
      return self.__class__.__name__ + "/" + question_type + ".html"
    
    def get(self, question_type):
      """
      Default implementation of a 'get' request. This is designed to be general
      enough that a problem type only has to implement a few methods to get
      almost all of the functionality they need. This method takes care of:
      
      - Dealing with the 'random' question type, which will randomly choose a
        valid question type and use that instead
      - Dealing with invalid question types
      - Responding with the students grades if type is 'json'
      - Rendering a template '{question_type}.html'
      - Creating the object which will be passed to the template. This object
        includes all of the data needed to make a 'submit' url, along with the
        question data
      """
      self.get_basics(self.maximum_level(question_type))
      if self.request.get('f', None) == None or int(self.request.get('f', None)) > 5:
        self.family = random.choice([1, 2, 3, 4, 5])
      else:
        self.family = int(self.request.get('f'))
      # If the user wants a random question, replace question_type with
      # a random valid question type
      if question_type == "random":
        question_type = random.choice(self.valid_types)
        if self.request.get('l', None) == None:
          self.level = random.choice(range(self.maximum_level(question_type) + 1))
      # If the question type is valid, check to see if it is a grade request
      # (aka type=json), otherwise generate a new problem     
      if self.is_valid_type(question_type):
        if self.request.get('type') == 'json':
            return self.get_grades(question_type)
        score_type = question_type
        self.initialize_random_number_generator(question_type)
        question_data = self.data_for_question(question_type)
        # logging.warn(question_data)
        submit_data = { "question_type":question_type, "magic":self.magic,
                        "level":self.level, "problem_id":self.problem_id, "family": self.family, "score_type": score_type}
        data = {"submit": submit_data, "question":question_data}
        self.add_best_score(data, question_type)
        self.add_functions_to_jinja(self.template_extra_functions())
        self.render(self.template_for_question(question_type),**data)
      else:
        self.response.out.write("Invalid URL")
          
    def post(self, question_type):
      """
      Default implementation of a 'post' request. This is designed to be general
      enough that a problem type only has to implement a few methods to get 
      almost all of the functionality they need. This method takes care of:
      
      - Dealing with invalid question types
      - Adding the users score into the database
      - Outputting the answer and user score in json format
      """
      if question_type == "random":
        question_type = self.request.get('st', None)
      if not self.is_valid_type(question_type):
        return self.response.out.write("Invalid URL")
      self.get_basics(self.maximum_level(question_type))
      student_answer = self.request.get('answer')
      self.family = (self.request.get('f', None))
      if self.family != None:
        self.family = int(self.family)
      self.initialize_random_number_generator(question_type)
      question_data = self.data_for_question(question_type)
      (score,wanted) = self.score_student_answer(question_type,question_data,student_answer)
      # logging.warn({"student":student_answer,"wanted":wanted})
      # store the result in the database
      self.put_submission(question_type, int(self.level), score, self.request.get('answer'))
      blob = json.dumps(self.get_return_data(score, wanted, question_data, question_type))
      self.response.out.write(blob)
      
    def get_return_data(self, score, wanted, question_data, question_type):
      return {"score": score, "wanted": wanted}  

    def add_functions_to_jinja(self,functions):
      d = {}
      for f in functions:
        d[f.__name__] = f
      jinja_env.globals.update(d)
    
    def get_all_attempts(self, magic, level, problemid, prob_type):
        return Submission.all().filter('student_magic_number =', str(magic)).filter('type =', str(prob_type)).filter('level =', level).filter('problem_id =', problemid)

    def best_score(self, magic, level, problemid, prob_type, new_score=0):
        key = "%sbest%s%s%s" % (magic, level, prob_type, problemid)
        data = memcache.get(key)
        if data is None:
            data = new_score
            submissions = self.get_all_attempts(magic, level, problemid, prob_type)
            for submission in submissions:
                if submission.score > data:
    	            data = submission.score
            memcache.add(key, data, 1000000)
        else:
    	    if new_score > data:
                data = new_score
                memcache.replace(key, data, 1000000)
        return data    	

    def number_of_attempts(self, magic, level, problemid, prob_type):
        key = "%scount%s%s%s" % (magic, level, prob_type, problemid)
        data = memcache.get(key)
        if data is None:
            data = self.get_all_attempts(magic, level, problemid, prob_type).count()
            memcache.add(key, data, 1000000)
        return data    	

    def increment_number_of_attempts(self, magic, level, problemid, prob_type):
        key = "%scount%s%s%s" % (magic, level, prob_type, problemid)
        memcache.incr(key, initial_value=0)

    def generate_index(self, magic, level, problem_index, prob_type):
        # Turn out magic number string into an integer. We do this by xor-ing all of the
        # unicode character codes for each individual character int he string
        num_attempts = self.number_of_attempts(magic, level, problem_index, prob_type)
        text = magic + prob_type + "-l%s-i%s-n%s" % (level, problem_index, num_attempts)
        number = zlib.adler32(text)
        # logging.warn("index: %s -> %s" % (text, number))
        return number
    
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    # factor out the parsing of the URL parameters so we can have one copy of their validation
    def get_basics(self, max_level):    #fixme defensive programming
        self.magic = self.request.get('student')
        self.problem_id = int_convert(self.request.get('problem_id'), 0)
        self.level = int_convert(self.request.get('l'), 0, 0, max_level)
        # return (magic, problem_id, level)

    # a remote gradebook wanting to know our scores; grab all database records,
    # turn them into JSON, and return them.
    def get_grades(self, problem_name):  
        submissions = self.get_all_attempts(self.magic, self.level, self.problem_id, problem_name)
        submissions_objects = []

        # Do loop here where we add all of the submissions that were
        # filtered into the objects array
        for submission in submissions:
          utc = int(time.mktime(submission.answered_on.timetuple()))
          submissions_objects.append({"score":submission.score,"answered_on":utc})
        submissions_dictionary = {"submissions":submissions_objects}
        blob = json.dumps(submissions_dictionary)
        self.response.out.write(blob)

    def put_submission(self, problem_name, level, score, answer):
        submission = Submission(student_magic_number = self.magic,
                                problem_id = self.problem_id, answer = answer,
                                score = score, type = problem_name, level = level)
        # logging.warn("submit: %s %s %s %s %s %s" % (self.magic, self.problem_id, answer, score, problem_name, level))
        submission.put()
	self.increment_number_of_attempts(self.magic, self.level, self.problem_id, problem_name)
	self.best_score(self.magic, self.level, self.problem_id, problem_name, score)

    def add_best_score(self, data, problem_name):
	data["best_score"] = self.best_score(self.magic, self.level, self.problem_id, problem_name)
	data["complete"] = "complete" if data["best_score"] >= 100 else "incomplete"
