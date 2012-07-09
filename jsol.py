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
import types

###############################################################################
# Errors                                                                      #
###############################################################################

class Error(Exception): pass

class FunctionError(Error):
   def __init__(self, e, n):
      if isinstance(e, Error):
         self.names = e.names
         self.names.append(n)
         self.e = e.e
      else:
         self.names = [n]
         self.e = e

   def __str__(self):
      return reduce(lambda x, y: x + y + ': ', self.names) + self.e.__str__()

###############################################################################
# Types                                                                       #
###############################################################################

class Type(object): pass

class Literal(Type):
   def __init__(self, val, env):
      self.val = copy.copy(val)

   def __str__(self):
      return str(self.val)

   def __eq__(self, o):
      return self.val == o.val

   def json(self):
      return dict([('lit', self.val)])

class List(Literal):
   def __init__(self, val, env):
      super(List, self).__init__(val, env)
      for (i, v) in enumerate(self.val):
         self.val[i] = _Eval(v, env)

   def __str__(self):
      return str(map(lambda x: x.__str__(), self.val))

   def json(self):
      return dict([('lit', map(lambda x: x.json(), self.val))])

class Dict(Literal):
   def __init__(self, val, env):
      super(Dict, self).__init__(val, env)
      dict_env = env.copy()
      for (k, v) in self.val.iteritems():
         self.val[k] = _Eval(v, dict_env)
      for v in self.val.values():
         if isinstance(v, Function):
            v._env = self.val

   def json(self):
      return dict([('lit',
                    dict(zip(self.val.keys(),
                             map(lambda x: x.json(), self.val.values()))))])

class String(Literal): pass
class Number(Literal):
   def json(self):
      return self.val

class Null(Literal):
   def json(self):
      return self.val

   def __str__(self):
      return 'Null'

class Function(Type):
   def __init__(self, d, env):
      self._env = env.copy()
      self._params = d.get('params', [])
      self._def = d.get('def', [])
      self._run_env = {}
      self.val = self

   def makeDict(self):
      env = {}
      env.update(self._env)
      env.update(self._run_env)
      return env

   def copy(self):
      return self.makeDict()

   def json(self):
      return dict([('params', self._params), ('def', self._def)])

   def get(self, k, default=None):
      return self.makeDict().get(k, default)

   def __getitem__(self, k):
      return self.makeDict()[k]

   def __setitem__(self, k, v):
      if k in self._run_env or k not in self._env:
         self._run_env[k] = v
      else:
         self._env[k] = v

   def Eval(self, args):
      self = copy.copy(self)
      self._run_env = dict(zip(self._params, args))
      return _ExecList(self._def, self)

def Lit(val, env=None):
   if env == None:
      env = {}
   if isinstance(val, Type):
      return val
   return LITERALS[type(val)](val, env)

TYPES = {
   List: "List",
   Dict: "Dict",
   String: "String",
   Number: "Number",
   Function: "Function",
   Null: "Null"
}

LITERALS = {
   list: List,
   dict: Dict,
   str: String,
   unicode: String,
   int: Number,
   long: Number,
   bool: Number,
   float: Number,
   types.NoneType: Null,
}

###############################################################################
# Built-in Functions                                                          #
###############################################################################

def _Cond(f, l):
   return Lit(all(f(l[i].val, l[i + 1].val) for i in xrange(len(l) - 1)))

def _Add(args):
   return reduce(lambda x, y: Lit(x.val + y.val), args)

def _Sub(args):
   return reduce(lambda x, y: Lit(x.val - y.val), args)

def _Mult(args):
   return reduce(lambda x, y: Lit(x.val * y.val), args)

def _Div(args):
   return reduce(lambda x, y: Lit(x.val / y.val), args)

def _Print(args):
   for arg in args:
      print arg,
   print

def _Eq(args):
   return _Cond(lambda x, y: x == y, args)

def _NEq(args):
   return Lit(not _Eq(args).val)

def _Lt(args):
   return _Cond(lambda x, y: x < y, args)

def _Gt(args):
   return _Cond(lambda x, y: x > y, args)

def _LtE(args):
   return _Cond(lambda x, y: x <= y, args)

def _GtE(args):
   return _Cond(lambda x, y: x >= y, args)

def _Len(args):
   return Lit(sum(map(lambda x: len(x.val), args)))

def _Ins(args):
   args[0].val.insert(args[1].val, args[2])
   return args[2]

def _Del(args):
   return args[0].val.pop(args[1].val)

def _Cut(args):
   return Lit([Lit(args[0].val[:args[1].val]), Lit(args[0].val[args[1].val:])])

def _Map(args):
   return Lit(map(lambda x: args[0].Eval([x]), args[1].val))

def _Fold(args):
   return Lit(reduce(lambda x, y: args[0].Eval([x, y]), args[1].val))

def _Filter(args):
   return Lit(filter(lambda x: args[0].Eval([x]).val, args[1].val))

def _Assert(args):
   if not _Eq(args).val:
      print 'Assert failed:', args[0], args[1]

def _Round(args):
   return Lit(int(round(args[0].val)))

def _Type(args):
   return Lit(TYPES[type(args[0])])

OPS = {
      '+': _Add, '-': _Sub, '*': _Mult, '/': _Div, 'print': _Print,
      '=': _Eq, '!': _NEq, '<': _Lt, '>': _Gt, '<=': _LtE, '>=': _GtE,
      'len': _Len, 'ins': _Ins, 'del': _Del, 'cut': _Cut, 'map': _Map,
      'fold': _Fold, 'filter': _Filter, 'assert': _Assert, 'round': _Round,
      'type': _Type
}

###############################################################################
# Interpreter                                                                 #
###############################################################################

def _ExecList(l, env):
   if len(l) == 0:
      return Lit(None)
   for exp in l[:-1]:
      _Eval(exp, env)
   return _Eval(l[-1], env)

def _EvalList(exp, env):
   if exp[0] in OPS:
      return OPS[exp[0]](exp[1:])
   if isinstance(exp[0], (Dict, List, String)):
      if len(exp) == 2:
         return Lit(exp[0].val[exp[1].val])
      ret = exp[0].val[exp[1].val] = exp[2]
      return ret
   if isinstance(exp[0], Function):
      return exp[0].Eval(exp[1:])

def _IfBlock(exp, env):
   for i in range(0, len(exp) - 1, 2):
      if _Eval(exp[i], env).val:
         return _ExecList(exp[i + 1], env)
   if len(exp) % 2:
      return _ExecList(exp[-1], env)
   return Lit(None)

def _Eval(exp, env):
   if isinstance(exp, Type):
      return exp
   if isinstance(exp, (str, unicode)) and exp in OPS:
      return exp
   if isinstance(exp, (float, int, bool, types.NoneType)):
      return Lit(exp, env)
   if isinstance(exp, dict):
      if 'lit' in exp:
         return Lit(exp['lit'], env)
      if 'def' in exp:
         return Function(exp, env)
      new_env = copy.copy(env)
      ret = Lit(None)
      for (k, v) in exp.iteritems():
         ret = env[k] = _Eval(v, new_env)
      for k in exp:
         if isinstance(env[k], Function):
            temp_env = env.copy()
            temp_env.update(env[k]._env)
            env[k]._env = temp_env
      return ret
   if isinstance(exp, list):
      name = exp[0]
      if name == 'if':
         return _IfBlock(exp[1:], env)
      exp = map(lambda x: _Eval(x, env), exp)
      try:
         return _EvalList(exp, env)
      except Exception as e:
         raise FunctionError(e, name)
   return env[exp]

def Eval(json_dict, **kwargs):
   env = {}
   json_dict.update(kwargs)
   _Eval(json_dict, env)
   try:
      return env['main'].Eval([])
   except FunctionError as e:
      print e

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
