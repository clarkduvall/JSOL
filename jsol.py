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
import random
import sys

def EvalList(l, env):
   return map(lambda x: _Eval(x, env), l)

def _Arithmetic(args, env, f):
   args = EvalList(args, env)
   return reduce(f, args)

def _Add(args, env):
   return _Arithmetic(args, env, lambda x, y: x + y)

def _Sub(args, env):
   return _Arithmetic(args, env, lambda x, y: x - y)

def _Mult(args, env):
   return _Arithmetic(args, env, lambda x, y: x * y)

def _Div(args, env):
   return _Arithmetic(args, env, lambda x, y: x / y)

def _Print(args, env):
   args = EvalList(args, env)
   for i in args:
      print i,
   print
   return 0

def _Assert(args, env):
   if not _Eq(args[:], env):
      print 'Assert failed: ', args

def _Len(args, env):
   args = EvalList(args, env)
   lens = map(len, args)
   return sum(lens)

def _Ins(args, env):
   args = EvalList(args, env)
   args[0].insert(args[1], args[2])
   return args[2]

def _Del(args, env):
   args = EvalList(args, env)
   return args[0].pop(args[1])

def _Rand(args, env):
   args = EvalList(args, env)
   return random.randint(args[0], args[1])

def ListChecker(args, env, f):
   l = EvalList(args, env)
   return all(f(l[i], l[i + 1]) for i in xrange(len(l) - 1))

def _Lt(args, env):
   return ListChecker(args, env, lambda x, y: x < y)

def _Gt(args, env):
   return ListChecker(args, env, lambda x, y: x > y)

def _LtE(args, env):
   return ListChecker(args, env, lambda x, y: x <= y)

def _GtE(args, env):
   return ListChecker(args, env, lambda x, y: x >= y)

def _Eq(args, env):
   return ListChecker(args, env, lambda x, y: x == y)

def _NEq(args, env):
   return not _Eq(args, env)

OPS = {
   '+': _Add, '-': _Sub, '*': _Mult, '/': _Div,
   '<': _Lt, '>': _Gt, '<=': _LtE, '>=': _GtE, '=': _Eq, '!': _NEq,
   'print': _Print, 'assert': _Assert, 'len': _Len, 'ins': _Ins, 'del': _Del,
   'rand': _Rand
}

def _Error(message, code):
   print message + ': ', code
   print
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
   except Exception as e:
      _Error('for', exp)

def _IsFunc(exp, env):
   try:
      return type(exp) == tuple or (type(exp) in [str, unicode] and exp in OPS)
   except:
      return False

def _IsBasic(exp, env):
   return _IsFunc(exp, env) or (type(exp) in [int, long, float, bool]) or (
       type(exp) == dict and 'lit' in exp)

def _GetBasic(exp, env):
   if type(exp) == dict and 'lit' in exp:
      lit = exp['lit']
      if type(lit) == list:
         for i in range(len(lit)):
            if not _IsBasic(lit[i], env):
               lit[i] = _Eval(lit[i], env)
      if type(lit) == dict:
         new_env = copy.copy(env)
         _Eval(lit, new_env)
         for func in new_env:
            if type(new_env[func]) == tuple:
               new_env[func] = (new_env[func][0], new_env)
         return new_env
      return lit
   return exp

def _Eval(exp, env):
   # basic type
   if _IsBasic(exp, env):
      return _GetBasic(exp, env)
   # function definition
   if type(exp) == dict and 'def' in exp:
      return (exp, copy.copy(env))
   # variable
   if type(exp) in [str, unicode]:
      if exp in OPS:
         _Error('%s is a keyword' % exp, env)
      if exp not in env:
         _Error('Variable %s not bound' % exp, env)
      return env[exp]
   # string literal or assignment
   elif type(exp) == dict:
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
      # evaluate function name
      f = _Eval(name, env)
      # built in function
      if type(f) in [str, unicode] and f in OPS:
         return OPS[f](exp[1:], env)
      if not _IsFunc(f, env):
         if len(args) == 2:
            val = _Eval(args[1], env)
            f[_Eval(args[0], env)] = val
            return val
         val = f[_Eval(args[0], env)]
         if _IsBasic(val, env):
            return _Eval(val, env)
         return val
      # function in environment
      for (p, v) in zip(f[0]['params'], args):
         f[1][p] = _Eval(v, f[1])
      return _ExecuteStatements(f[0]['def'], f[1])
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
      with open(arg, 'r') as f:
         j = json.load(f)
         Eval(j)

if __name__ == '__main__':
   main()
