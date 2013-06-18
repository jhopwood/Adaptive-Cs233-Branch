#!/bin/env python
#===============================================================================
# Copyright (c) 2007 Jason Evans <jasone@canonware.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
#===============================================================================

import sys
import Parsing
# import math

#===============================================================================
# Tokens/precedences.  See Parsing documentation to learn about the
# significance of left-associative precedence.

class PAddOp(Parsing.Precedence):
    "%left pAddOp"
class TokenPlus(Parsing.Token):
    "%token plus [pAddOp]"

class PMulOp(Parsing.Precedence):
    "%left pMulOp >pAddOp"
class TokenStar(Parsing.Token):
    "%token star [pMulOp]"

class PExpr(Parsing.Precedence):
    "%left pExpr"
class TokenLeftParen(Parsing.Token):
    "%token lparen [split]"
class TokenRightParen(Parsing.Token):
    "%token rparen [none]"

class PNot(Parsing.Precedence):
    "%left pNot >pMulOp"
class TokenNot(Parsing.Token):
    "%token tick [pNot]"

class TokenTerminal(Parsing.Token):
    "%token terminal"
    def __init__(self, parser, terminal, i):
	Parsing.Token.__init__(self, parser)
	self.val = i
        self.terminal = terminal
    def evaluate(self):
        return self.val

#===============================================================================
# Nonterminals, with associated productions.  In traditional BNF, the following
# productions would look something like:
#
#   Expr ::= terminal
#          | lparen Expr rparen
#          | Expr plus Expr
#          | Expr star Expr.
#          | Expr Not
#   Result ::= Expr.

class Expr(Parsing.Nonterm):
    "%nonterm"

    TERMINAL=0
    NOT=1
    AND=2
    OR=3

    def does_nothing(self):
        return self.type == self.TERMINAL

    def evaluate(self):
        if self.type == self.TERMINAL:
            return self.term1.evaluate()
        if self.type == self.NOT:
            return not self.term1.evaluate()
        if self.type == self.AND:
            return self.term1.evaluate() and self.term2.evaluate()
        if self.type == self.OR:
            return self.term1.evaluate() or self.term2.evaluate()
        print "SUPER BIG FAILURE!!!!"

    def reduceTerminal(self, i):
	"%reduce terminal"
        self.type = self.TERMINAL
	self.term1 = i

    def reduceNot(self, exprA, tick):
	"%reduce Expr tick [pExpr]"
        self.type = self.NOT
	self.term1 = exprA

    def reduceParens(self, lparen, exprA, rparen):
	"%reduce lparen Expr rparen [pExpr]"
        self.type = self.TERMINAL
	self.term1 = exprA

    def reduceAdd(self, exprA, plus, exprB):
	"%reduce Expr plus Expr [pAddOp]"
        self.type = self.OR
	self.term1 = exprA
	self.term2 = exprB

    def reduceMul(self, exprA, star, exprB):
	"%reduce Expr star Expr [pMulOp]"
        self.type = self.AND
	self.term1 = exprA
	self.term2 = exprB

# This is the start symbol; there can be only one such class in the grammar.
class Result(Parsing.Nonterm):
    "%start"
    def reduce(self, Expr):
	"%reduce Expr"
        self.final = Expr
	#print "Result: %d" % Expr.evaluate()
        pass

#===============================================================================
# Parser.

# Parser subclasses the Lr parser driver.  Since the grammar is unambiguous, we
# have no need of the Glr driver's extra functionality, though there is nothing
# preventing us from using it.
#
# If you are curious how much more work the GLR driver has to do, simply change
# the superclass from Parsing.Lr to Parsing.Glr, then, run this program with
# verbosity enabled.
class Parser(Parsing.Lr):
    def __init__(self, spec, terminals):
	Parsing.Lr.__init__(self, spec)
        self.terminals = {}
        i = 1
        for c in terminals:
            self.terminals[c] = TokenTerminal(self, c, i)
            i += 1

    # Scanner: tolerates whitespace, inserts implied *'s
    def scan(self, input):
	syms = {"+": TokenPlus,
		"*": TokenStar,
		"'": TokenNot,
                "(": TokenLeftParen,
                ")": TokenRightParen,
		}

        last_token = TokenPlus

	for c in input:
            if c.isspace():   # remove whitespace
                continue
	    if c in syms:     # recognize operators
		token = syms[c](self)
            else:             # recognize terminals
                if not self.terminals.has_key(c):
		    raise Parsing.SyntaxError("Unrecognized token: %s" % c)
		token = self.terminals[c]
                
            # Insert any implied Star tokens
            if isinstance(last_token, TokenTerminal) or \
               isinstance(last_token, TokenRightParen) or \
               isinstance(last_token, TokenNot):
                if isinstance(token, TokenTerminal) or \
                   isinstance(token, TokenLeftParen):
                    self.token(TokenStar(self))
	    # Feed token to parser.
	    self.token(token)
            last_token = token
	# Tell the parser that the end of input has been reached.
	self.eoi()

spec = Parsing.Spec(sys.modules[__name__],
		    pickleFile=None,
		    skinny=False,
		    verbose=False)
