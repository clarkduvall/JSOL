#!/usr/bin/env python

# Copyright 2012 Clark DuVall
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

import copy
import json
import sys

def EvalList(l, env):
   return map(lambda x: _Eval(x, env), l)

def _Add(args, env):
   args = EvalList(args, env)
   return reduce(lambda x, y: x + y, args)

def _Sub(args, env):
   args = EvalList(args, env)
   return reduce(lambda x, y: x - y, args)

def _Mult(args, env):
   args = EvalList(args, env)
   return reduce(lambda x, y: x * y, args)

def _Div(args, env):
   args = EvalList(args, env)
   return reduce(lambda x, y: x / y, args)

def _Print(args, env):
   args = EvalList(args, env)
   for i in args:
      print i,
   print
   return 0

def _Assert(args, env):
   if not _Eq(args[:], env):
      print 'Assert failed: ',
      print args

def ListChecker(l, f):
   return all(f(l[i], l[i + 1]) for i in xrange(len(l) - 1))

def _Lt(args, env):
   args = EvalList(args, env)
   return ListChecker(args, lambda x, y: x < y)

def _Gt(args, env):
   args = EvalList(args, env)
   return ListChecker(args, lambda x, y: x > y)

def _Eq(args, env):
   args = EvalList(args, env)
   return ListChecker(args, lambda x, y: x == y)

def _NEq(args, env):
   return not _Eq(args, env)

OPS = {
   '+': _Add,
   '-': _Sub,
   '*': _Mult,
   '/': _Div,
   '<': _Lt,
   '>': _Gt,
   '=': _Eq,
   '!': _NEq,
   'print': _Print,
   'assert': _Assert
}

def _Error(message, code):
   print '%s: ' % message,
   print code
   exit(0)

def _ExecuteStatements(statements, env):
   for statement in statements[:-1]:
      _Eval(statement, env)
   return _Eval(statements[-1], env)

def _IfBlock(exp, env):
   try:
      if _Eval(exp[1], env):
         return _ExecuteStatements(exp[2], env)
      index = 3
      while exp[index] == 'elif':
         if _Eval(exp[index + 1], env):
            return _ExecuteStatements(exp[index + 2], env)
         index += 3
      return _ExecuteStatements(exp[-1], env)
   except:
      _Error('if', exp)

def _ForBlock(exp, env):
   try:
      _Eval(exp[1], env)
      while _Eval(exp[2], env):
         ret = _ExecuteStatements(exp[-1], env)
         _Eval(exp[3], env)
      return ret
   except:
      _Error('for', exp)

def _IsFunc(exp, env):
   try:
      return type(exp) == tuple or (type(exp) in [str, unicode] and exp in OPS)
   except:
      return False

def _Eval(exp, env):
   # basic type
   if _IsFunc(exp, env) or type(exp) in [int, long, float, bool]:
      return exp
   # function definition
   if type(exp) == dict and 'def' in exp:
      return (exp, copy.copy(env))
   # variable
   if type(exp) in [str, unicode]:
      if exp in OPS:
         _Error('%s is a keyword.' % exp, env)
      if exp not in env:
         _Error('Variable %s not bound.' % exp, env)
      return env[exp]
   # string literal or assignment
   elif type(exp) == dict:
      if 'lit' in exp:
         return exp['lit']
      ret = 0
      for var in exp:
         ret = env[var] = _Eval(exp[var], env)
      return ret
   # function call/if/for
   elif type(exp) == list:
      name = exp[0]
      args = exp[1:]
      # if statement
      if name == 'if':
         return _IfBlock(exp, env)
      # for loop
      if name == 'for':
         return _ForBlock(exp, env)
      if name not in env and name not in OPS:
         _Error('Function %s not in environment.' % exp, env)
      # evaluate function name
      f = name
      while not _IsFunc(f, env):
         f = _Eval(name, env)
      # built in function
      if type(f) != tuple and f in OPS:
         return OPS[f](exp[1:], env)
      # function in environment
      else:
         body = f[0]
      # run function in copied env
      for (p, v) in zip(body['params'], args):
         f[1][p] = _Eval(v, f[1])
      return _ExecuteStatements(body['def'], f[1])
   # try to evaluate anything else
   else:
      return _Eval(exp, env)

def Eval(json_dict, env=None):
   if not env:
      env = {}
   _Eval(json_dict, env)
   for func in env:
      if type(env[func]) == tuple:
         env[func] = (env[func][0], env)
   return _ExecuteStatements(json_dict['main']['def'], env)

def main():
   if len(sys.argv) < 2:
      print 'usage: jsol.py <jsol_files>'
      exit(0)
   for arg in sys.argv[1:]:
      print 'Running ' + arg
      with open(sys.argv[1], 'r') as f:
         j = json.load(f)
         Eval(j)

if __name__ == '__main__':
   main()
