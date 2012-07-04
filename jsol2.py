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

###############################################################################
# Types                                                                       #
###############################################################################

class Type(object): pass

class Literal(Type):
   def __init__(self, val, env):
      self.val = val

   def __str__(self):
      return str(self.val)

class List(Literal):
   def __init__(self, val, env):
      super(List, self).__init__(val, env)
      for (i, v) in enumerate(self.val):
         self.val[i] = _Eval(v, env)

   def __str__(self):
      return str(map(lambda x: x.__str__(), self.val))

class Dict(Literal):
   def __init__(self, val, env):
      super(Dict, self).__init__(val, env)
      dict_env = copy.copy(env)
      for (k, v) in self.val.iteritems():
         self.val[k] = _Eval(v, dict_env)

class String(Literal): pass
class Number(Literal): pass

class Function(Type):
   def __init__(self, d, env):
      if isinstance(env, Function):
         self._env = {}
         self._env.update(env._env)
         self._env.update(env._run_env)
      else:
         self._env = copy.copy(env)
      self._params = d.get('params', [])
      self._def = d.get('def', [])
      self._run_env = {}

   def get(self, k, default=None):
      if k in self._run_env:
         return self._run_env[k]
      if k in self._env:
         return self._env[k]
      return default

   def __getitem__(self, k):
      if k in self._run_env:
         return self._run_env[k]
      return self._env[k]

   def __setitem__(self, k, v):
      if k in self._run_env or k not in self._env:
         self._run_env[k] = v
      else:
         self._env[k] = v

   def Eval(self, args):
      self._run_env = dict(zip(self._params, args))
      return _ExecList(self._def, self)

def Lit(val, env):
   return LITERALS[type(val)](val, env)

LITERALS = {
   list: List,
   dict: Dict,
   str: String,
   unicode: String,
   int: Number,
   bool: Number
}

###############################################################################
# Built-in Functions                                                          #
###############################################################################

def _Cond(f, l):
   print l
   return Lit(all(f(l[i].val, l[i + 1].val) for i in xrange(len(l) - 1)), {})

def _Add(args):
   return reduce(lambda x, y: Lit(x.val + y.val, {}), args)

def _Sub(args):
   return reduce(lambda x, y: Lit(x.val - y.val, {}), args)

def _Mult(args):
   return reduce(lambda x, y: Lit(x.val * y.val, {}), args)

def _Div(args):
   return reduce(lambda x, y: Lit(x.val / y.val, {}), args)

def _Print(args):
   for arg in args:
      print arg,
   print

def _Eq(args):
   return _Cond(lambda x, y: x == y, args)

def _NEq(args):
   return _Eval({'lit': not _Eq(args).val}, {})

def _Lt(args):
   return _Cond(lambda x, y: x < y, args)

def _Gt(args):
   return _Cond(lambda x, y: x > y, args)

def _LtE(args):
   return _Cond(lambda x, y: x <= y, args)

def _GtE(args):
   return _Cond(lambda x, y: x >= y, args)

def _Assert(args):
   if not _Eq(args).val:
      print 'Assert failed:', args[0], args[1]

OPS = {
      '+': _Add, '-': _Sub, '*': _Mult, '/': _Div, 'print': _Print,
      '=': _Eq, '!': _NEq, '<': _Lt, '>': _Gt, '<=': _LtE, '>=': _GtE,
      'assert': _Assert
}

###############################################################################
# Interpreter                                                                 #
###############################################################################

def _ExecList(l, env):
   for exp in l[:-1]:
      _Eval(exp, env)
   return _Eval(l[-1], env)

def _EvalList(exp):
   if exp[0] in OPS:
      return OPS[exp[0]](exp[1:])
   if isinstance(exp[0], (Dict, List)):
      if len(exp) == 2:
         return exp[0].val[exp[1].val]
      ret = exp[0].val[exp[1].val] = exp[2]
      return ret
   if isinstance(exp[0], Function):
      return exp[0].Eval(exp[1:])

def _Eval(exp, env):
   if isinstance(exp, Type):
      return exp
   if isinstance(exp, (str, unicode)) and exp in OPS:
      return exp
   if isinstance(exp, (float, int, bool)):
      return Number(exp, env)
   elif isinstance(exp, dict):
      if 'lit' in exp:
         return Lit(exp['lit'], env)
      if 'def' in exp:
         return Function(exp, env)
      new_env = copy.copy(env)
      # TODO make sure not empty
      for (k, v) in exp.iteritems():
         ret = env[k] = _Eval(v, new_env)
      return ret
   elif isinstance(exp, list):
      exp = map(lambda x: _Eval(x, env), exp)
      return _EvalList(exp)
   else:
      return env[exp]

def Eval(json_dict):
   env = {}
   _Eval(json_dict, env)
   for v in env.values():
      if isinstance(v, Function):
         v._env = env
   return env['main'].Eval([]).val

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
