#!/usr/bin/env python
#
# Copyright 2013 University of Illinois
#

import math
import logging
import re

class Rect(object):
	def __init__(self, x, y, w, h):
		self.x = x;
		self.y = y;
		self.w = w;
		self.h = h;
		self.weight=0;

class KmapSimulator(object):
	def __init__(self, bits, cells):
		self.bits = bits
		self.answer = ""
		self.cells = cells;
		self.sorted=[]
		self.cover=[False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False]
		self.weight=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

		self.solve()

	def good(self, minterms):
		re_terms = []
		for term in minterms:
			rex = r"";
			for v in self.variable:
				if v[0] in term:
					rex=rex+"0"
				elif v[1] in term:
					rex=rex+"1"
				else:
					rex=rex+"."
			re_terms.append(rex)	

		#print re_terms
			
		i = 0
		for cell in self.cells:
			ok = False
			for rex in re_terms:
				match = re.search(rex, cell)

#				print match
#				print rex
#				print cell
#				print self.bits[i]
#				print "\n"
				
				if match and self.bits[i]==0:
					return False
				elif match:
					ok = True
			if not ok and self.bits[i]==1:
				return False
			i+=1
		return True
			
	def allTrue(self, r):
		for x in range(r.h):
			for y in range(r.w):
				if self.bits[self.coor(r.x, x, 4)*4+self.coor(r.y, y, 4)] == 0:
					return False
		return True

	def isCovered(self, r):
		for x in range(r.h):
			for y in range(r.w):
				if self.cover[self.coor(r.x, x, 4)*4+self.coor(r.y, y, 4)]==0:
					return False
		return True

	def coverMap(self, r, flag):
		for x in range(r.h):
			for y in range(r.w):
				self.cover[self.coor(r.x, x, 4)*4+self.coor(r.y, y, 4)] = flag
	
	def checkRect(self,width, height, rects, cover):
		w = 4;
		h = 4;
		if width==4 and height==4:
			w = 1;
			h = 1;

		for x in range(h):
			for y in range(w):
				r = Rect(x = x, y = y, w = width, h = height)
				if self.allTrue(r):
					if not self.isCovered(r):
						rects.append(r)
						if cover:
							self.coverMap(r, True)				

	def addWeight(self, r, value):
		for x in range(r.h):
			for y in range(r.w):
				self.weight[self.coor(r.x, x, 4)*4+self.coor(r.y, y, 4)]+=value

	def computeWeight(self, r):
		res=0
		for x in range(r.h):
			for y in range(r.w):
				res+=self.weight[self.coor(r.x, x, 4)*4+self.coor(r.y, y, 4)]
		return res

	def tryAllRects(self):
		for rect in self.sorted:
			if self.allTrue(rect) and not self.isCovered(rect):
				self.rects.append(rect)
				self.coverMap(rect, True)
	
	def intersect(self, r1, r2):
		if (r1.x+r1.w>r2.x) and (r2.x+r2.w>r1.x) and (r1.y+r1.h>r2.y) and (r2.y+r2.h>r1.y):
			return True;
		return False;

	def coor(self, x, dx, m):
		return (x+dx)%m
	
	def findoptimal(self):
		mvalue = 100000
		
		for x in range(4):
			for y in range(4):
				if (self.cover[self.coor(0, x, 4)*4+self.coor(0, y, 4)]):
					self.weight[self.coor(0, x, 4)*4+self.coor(0, y, 4)] = mvalue
				else:
					self.weight[self.coor(0, x, 4)*4+self.coor(0, y, 4)] = 0

		for i in self.rects2:
			self.addWeight(i, 1)
		
		while (len(self.rects2) > 0):
			for rect in self.rects2:
				rect.weight = self.computeWeight(rect)
				
			self.rects2.sort(key=lambda rect: rect.weight)

			for	i in self.rects2:	
				logging.warn("x=%d y=%d w=%d h=%d wi=%d"%(i.x,i.y,i.w,i.h, i.weight))
			print "\n"

			r = self.rects2.pop(0)
			self.sorted.append(r)
			
			if len(self.rects2) == 0:
				break

			self.addWeight(r, mvalue-1)

			for i in self.rects2:
				if self.intersect(r, i):
					self.addWeight(i, -1)
					
		self.tryAllRects()


	variable = [("A\'","A"),("B\'","B"),("C\'","C"),("D\'","D")]

	def same(self, r, ind):
		first = self.cells[r.x*4+r.y][ind]
		
		for x in range(r.h):
			for y in range(r.w):
				if first!=self.cells[self.coor(r.x, x, 4)*4+self.coor(r.y, y, 4)][ind]:
					return 2
		return int(first)
	
	def getExpression(self):
		for i in self.rects:
			if i:
				text=""
				for j in range(4):
					ret=self.same(i, j)
					if ret in range(2):
						text=text+self.variable[j][ret]
				if len(self.answer) == 0:
					self.answer = text
				else:
					self.answer+="+"+text			
				
		logging.warn(self.answer)
				
	def getAnswer(self):
		#print "i am ok %s"%self.answer
		return self.answer

	def solve(self):
		dimensions = ((4,4),(4,2),(2,4),(1,4),(4,1),(2,2))
		self.rects = []
		self.rects2 = []

		for i in dimensions:
			self.checkRect(i[0], i[1], self.rects, True)

		self.checkRect(2, 1, self.rects2, False)
		self.checkRect(1, 2, self.rects2, False)

		self.findoptimal()

		self.checkRect(1, 1, self.rects, True)

		self.coverMap(Rect(0,0,4,4), False)

		for i in xrange(len(self.rects)-1,0,-1):
			if self.isCovered(self.rects[i]):
				self.rects[i]=None;
			else:
				self.coverMap(self.rects[i], True);
		self.getExpression()
