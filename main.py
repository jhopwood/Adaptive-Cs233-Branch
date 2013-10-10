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

# notes
# Google AppEngine DataStore GQL
# p = urllib2.urlopen("http://www.google.com")
# dir(p)
# from xml.dom import minidom
# parsed = minidom.parse(p)
# parsed.getElementsByTagName("item")
# import json
# x = json.loads(j)
# hostip.info
# google static maps API
# strftime

import logging
import webapp2
import json
import time
# import iclicker

from models import Submission



# from google.appengine.ext import db

from problem_handlers import *
  
class MainHandler(base_handler.BaseHandler):
    def get(self):
        self.redirect("/html/home.html")

#server = "http://localhost:8082/digital_logic/"
#server = "http://arkitecktur.appspot.com/digital_logic/"
server = "/"
boolean_problems1 = [
   {"url":server+"digital_logic/t2e?l=0","id":"0", "height":"170"},
   {"url":server+"digital_logic/e2t?l=0","id":"0", "height":"170"},
   {"url":server+"digital_logic/c2e?l=0","id":"0", "height":"300"},
   {"url":server+"digital_logic/v2c?l=0","id":"0", "height":"350"},
   {"url":server+"digital_logic/c2t?l=0","id":"0", "height":"300"},
   {"url":server+"digital_logic/t2e?l=1","id":"0", "height":"170"},
   {"url":server+"digital_logic/e2c?l=0","id":"0", "height":"350"},
   {"url":server+"digital_logic/v2e?l=0","id":"0", "height":"250"},
   {"url":server+"digital_logic/t2c?l=0","id":"0", "height":"350"},
   {"url":server+"digital_logic/c2t?l=1","id":"0", "height":"300"},
   ]
number_problems1 = [
   {"url":server+"number_representation/b2d?l=0","id":"0", "height":"130"},
   {"url":server+"bitwise_logical/not?l=1","id":"0", "height":"130"},
   {"url":server+"number_representation/b2h?l=0","id":"0", "height":"130"},
   {"url":server+"number_bit_length/ul?l=0","id":"0", "height":"130"},
   {"url":server+"bitwise_logical/and?l=0","id":"0", "height":"130"},
   {"url":server+"number_representation/b2d?l=1","id":"0", "height":"130"},
   {"url":server+"number_bit_length/ux?l=1","id":"0", "height":"130"},
   {"url":server+"number_representation/d2b?l=1","id":"0", "height":"130"},
   {"url":server+"bitwise_logical/or?l=0","id":"0", "height":"130"},
   {"url":server+"number_representation/b2h?l=1","id":"0", "height":"130"},
   {"url":server+"number_bit_length/ul?l=2","id":"0", "height":"130"},
   ]
number_problems2 = [
   {"url":server+"number_representation/h2b?l=1","id":"0", "height":"130"},  # move to previous?
   {"url":server+"number_representation/b2b?l=0","id":"0", "height":"130"},
   {"url":server+"number_representation/h2d?l=1","id":"0", "height":"130"},  # move to previous?
   {"url":server+"arithmetic/bpp+?l=0","id":"0", "height":"130"},
   {"url":server+"arithmetic/bpp-?l=0","id":"0", "height":"130"},
   {"url":server+"number_representation/c2d?l=1","id":"0", "height":"130"},
   {"url":server+"number_representation/d2c?l=1","id":"0", "height":"130"},
   {"url":server+"number_representation/c2c?l=0","id":"0", "height":"130"},
   {"url":server+"arithmetic/c+?l=1","id":"0", "height":"130"},
   {"url":server+"arithmetic/c-?l=0","id":"0", "height":"130"},
   ]
boolean_problems2 = [
   {"url":server+"digital_logic/t2e?l=3","id":"0", "height":"300"},
   {"url":server+"digital_logic/e2t?l=3","id":"0", "height":"300"},
   {"url":server+"digital_logic/c2e?l=4","id":"0", "height":"400"},
   {"url":server+"digital_logic/e2c?l=3","id":"0", "height":"350"},
   {"url":server+"digital_logic/t2c?l=3","id":"0", "height":"350"},
   {"url":server+"digital_logic/c2t?l=3","id":"0", "height":"300"},
   {"url":server+"digital_logic/t2e?l=4","id":"0", "height":"300"},
   {"url":server+"digital_logic/e2t?l=4","id":"0", "height":"300"},
   {"url":server+"digital_logic/v2c?l=4","id":"0", "height":"350"},
   ]

cache_problems1 = [
   {"url":server+"cache/d2c?l=1","id":"0", "height":"150"},
   {"url":server+"cache/d2c?l=0","id":"0", "height":"150"},
   {"url":server+"cache/d2c?l=0","id":"1", "height":"150"},
   {"url":server+"cache/d2c?l=0","id":"2", "height":"150"},
   {"url":server+"cache/c2a?l=0","id":"0", "height":"400"},
   {"url":server+"cache/c2a?l=1","id":"0", "height":"400"},
   {"url":server+"cache/c2a?l=2","id":"0", "height":"400"},
   {"url":server+"cache/c2a?l=4","id":"0", "height":"400"},
   {"url":server+"cache/c2a?l=24","id":"0", "height":"400"},
   ]

assignments = [
      {"viewable":True, "name":"HW1: Number Representation I", "date_due":"January 23, 2013 10:00:00", "problems":number_problems1},
      {"viewable":True, "name":"HW2: Boolean Functions I", "date_due":"January 24, 2013 22:00:00", "problems":boolean_problems1},
      {"viewable":True, "name":"HW3: Number Representation II", "date_due":"January 28, 2013 22:00:00", "problems":number_problems2},
      {"viewable":True, "name":"HW4: Boolean Functions II", "date_due":"January 29, 2013 22:00:00", "problems":boolean_problems2},
      {"viewable":True, "name":"HW5: Cache Problems I", "date_due":"April 22, 2013 22:00:00", "problems":cache_problems1},
      ]

class WebHomeworks(base_handler.BaseHandler):
  def post(self):
    blob = json.dumps({"result":assignments})
    self.response.out.write(blob)

class AssignmentScore(base_handler.BaseHandler):
  def post(self):
    magic = self.request.get('student')
    name = self.request.get('name')
    percent = 0
    problems = None
    for a in assignments:
       if a["name"] == name:
       	  problems = a["problems"]
          for i in range(len(problems)):
             percent += self.best_score(magic, int(problems[i]["url"][-1]), int(problems[i]["id"]), problems[i]["url"].split("/")[-1].split("?")[0])
    	  percent = round(percent / len(problems))
    	  break
    
    blob = json.dumps(percent)
    self.response.out.write(blob)



class Iclicker(base_handler.BaseHandler):
  def get(self):
    self.redirect("/html/iclicker.html")
  def post(self):
    self.response.out.write("found")

class Download(base_handler.BaseHandler):
  def get(self):
    magic = self.request.get('student')
    submissions = Submission.all().filter('student_magic_number =', str(magic))
    submissions_objects = []
    for submission in submissions:
       utc = int(time.mktime(submission.answered_on.timetuple()))
       submissions_objects.append({"type":submission.type, "level":submission.level, "id":submission.problem_id, "score":submission.score, "answered_on":utc, "answer":submission.answer})
    blob = json.dumps(submissions_objects)
    self.response.out.write(blob)


    


# The string contained after the second / should be passed as a parameter
# to the 'get' method of the class

app = webapp2.WSGIApplication([('/', MainHandler),
                               ('/digital_logic/(.*)', digital_logic.DigitalLogic),
                               ('/number_bit_length/(.*)', number_bit_length.NumberBitLength),
                               ('/number_based_problem/(.*)', number_based_problem.NumberBasedProblem),
                               ('/mips_representation/(.*)', mips_representation.MIPSRepresentation),
                               ('/register_file/(.*)', register_file.RegisterFile),
                               ('/cache/(.*)', cache.Cache),
                               ('/webhomeworks', WebHomeworks),
                               ('/assignmentscore', AssignmentScore),
			                         ('/iclicker', Iclicker),
			                         ('/download', Download),
                               ('/msi_component/(.*)', msi_component_problem.MSIComponentProblem),
                               ('/finite_state/(.*)', finite_state_problem.FiniteStateProblem),
                               ('/shift_and_mask/(.*)', bit_shift_and_mask_problem.BitShiftAndMaskProblem),
                               ('/rf/(.*)', rf.RegFile),
                               ('/ieee_32/(.*)', ieee_32.IeeeProblem),
                               ('/parity/(.*)', parity.Parity),
                               ('/msi_actions/(.*)',msi_actions.Msi_actions),
                               ('/datadependence/(.*)',datadependence.Datadependence),
                               ('/flip_flop/(.*)',flip_flop.FlipFlop),
                               ('/instruction_format/(.*)', instruction_format.InstructionFormat),
                               ('/delay/(.*)', delay.Delay),
                               ('/build/(.*)', build.Build),
							   ('/adaptive/(.*)', adaptivemath.AdaptiveMath),
							   ('/true_false/(.*)', true_false.TrueFalse)
                               ],
                              debug=True)
