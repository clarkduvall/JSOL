#!/usr/bin/env python

import json

def _add(args, env):
   args = map(lambda x: _Eval(x, env), args)
   return sum(args)

def _sub(args, env):
   args = map(lambda x: _Eval(x, env), args)
   return reduce(lambda x, y: x - y, args)

def _mult(args, env):
   args = map(lambda x: _Eval(x, env), args)
   return reduce(lambda x, y: x * y, args)

def _div(args, env):
   args = map(lambda x: _Eval(x, env), args)
   return reduce(lambda x, y: x / y, args)

def _print(args, env):
   args = map(lambda x: _Eval(x, env), args)
   for i in args:
      print i,
   print
   return 0

def _lt(args, env):
   return _Eval(args[0], env) < _Eval(args[1], env)

def _gt(args, env):
   return _Eval(args[0], env) > _Eval(args[1], env)

def _eq(args, env):
   return _Eval(args[0], env) == _Eval(args[1], env)

OPS = {
   '+': _add,
   '-': _sub,
   '*': _mult,
   '/': _div,
   '<': _lt,
   '>': _gt,
   '=': _eq,
   'print': _print
}

def _Error(message):
   print message
   exit(0)

def ExecuteStatements(statements, env):
   for statement in statements[:-1]:
      _Eval(statement, env)
   return _Eval(statements[-1], env)

def _IfBlock(exp, env):
   if _Eval(exp[1], env):
      return ExecuteStatements(exp[2], env)
   index = 3
   while exp[index] == 'elif':
      if _Eval(exp[index + 1], env):
         return ExecuteStatements(exp[index + 2], env)
      index += 3
   return ExecuteStatements(exp[-1], env)

def _ForBlock(exp, env):
   _Eval(exp[1], env)
   while _Eval(exp[2], env):
      ret = ExecuteStatements(exp[-1], env)
      _Eval(exp[3], env)
   return ret

def _Eval(exp, env):
   if type(exp) == dict and 'def' in exp:
      return ExecuteStatements(exp['def'], env)
   if type(exp) in [int, long, float, bool]:
      return exp
   if type(exp) in [str, unicode]:
      if exp in OPS:
         _Error('%s is a keyword.' % exp)
      if exp not in env:
         _Error('Variable %s not bound.' % exp)
      return env[exp]
   elif type(exp) == dict:
      ret = 0
      for var in exp:
         ret = env[var] = _Eval(exp[var], env)
      return ret
   elif type(exp) == list:
      name = exp[0]
      args = exp[1:]
      if name in OPS:
         return OPS[name](exp[1:], env)
      if name == 'if':
         return _IfBlock(exp, env)
      if name == 'for':
         return _ForBlock(exp, env)
      if name not in env:
         _Error('Function %s not in environment.' % exp)
      f = env[name]
      new_env = {}
      for (p, v) in zip(f['params'], args):
         new_env[p] = _Eval(v, env)
      return _Eval(f, new_env)
   else:
      return _Eval(exp, env)
   _Error('You shouldn\'t be here! ' + exp.__str__())

def Eval(json_dict):
   return _Eval(json_dict['main'], json_dict)

def main():
   with open('main.jsol', 'r') as f:
      j = json.load(f)
      print Eval(j)

if __name__ == '__main__':
   main()
