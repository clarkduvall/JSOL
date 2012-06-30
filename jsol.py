#!/usr/bin/env python

import copy
import json
import sys

def _Add(args, env):
   args = map(lambda x: _Eval(x, env), args)
   return reduce(lambda x, y: x + y, args)

def _Sub(args, env):
   args = map(lambda x: _Eval(x, env), args)
   return reduce(lambda x, y: x - y, args)

def _Mult(args, env):
   args = map(lambda x: _Eval(x, env), args)
   return reduce(lambda x, y: x * y, args)

def _Div(args, env):
   args = map(lambda x: _Eval(x, env), args)
   return reduce(lambda x, y: x / y, args)

def _Print(args, env):
   args = map(lambda x: _Eval(x, env), args)
   for i in args:
      print i,
   print
   return 0

def _Lt(args, env):
   return _Eval(args[0], env) < _Eval(args[1], env)

def _Gt(args, env):
   return _Eval(args[0], env) > _Eval(args[1], env)

def _Eq(args, env):
   return _Eval(args[0], env) == _Eval(args[1], env)

OPS = {
   '+': _Add,
   '-': _Sub,
   '*': _Mult,
   '/': _Div,
   '<': _Lt,
   '>': _Gt,
   '=': _Eq,
   'print': _Print
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
      return type(exp) in [str, unicode] and (
          exp in OPS or exp in env and 'def' in env[exp])
   except:
      return False

def _Eval(exp, env):
   # basic type
   if _IsFunc(exp, env) or type(exp) in [int, long, float, bool]:
      return exp
   # function definition
   if type(exp) == dict and 'def' in exp:
      return exp
   # variable
   if type(exp) in [str, unicode]:
      if exp in OPS:
         _Error('%s is a keyword.' % exp, env)
      if exp not in env:
         _Error('Variable %s not bound.' % exp, env)
      return env[exp]
   # string literal or assignment
   elif type(exp) == dict:
      if 'str' in exp:
         return exp['str']
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
      while not _IsFunc(name, env):
         name = _Eval(name, env)
      # built in function
      if name in OPS:
         return OPS[name](exp[1:], copy.copy(env))
      # function in environment
      else:
         f = env[name]
      # run function in copied env
      new_env = copy.copy(env)
      for (p, v) in zip(f['params'], args):
         new_env[p] = _Eval(v, env)
      return _ExecuteStatements(f['def'], new_env)
   # try to evaluate anything else
   else:
      return _Eval(exp, env)

def Eval(json_dict):
   return _ExecuteStatements(json_dict['main']['def'], json_dict)

def main():
   if len(sys.argv) != 2:
      print 'usage: jsol.py <jsol_file>'
      exit(0)
   with open(sys.argv[1], 'r') as f:
      j = json.load(f)
      print Eval(j)

if __name__ == '__main__':
   main()
