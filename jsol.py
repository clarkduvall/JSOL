#!/usr/bin/env python

import json

def add(args, env):
   args = map(lambda x: eval(x, env), args)
   return sum(args)

def sub(args, env):
   args = map(lambda x: eval(x, env), args)
   return reduce(lambda x, y: x - y, args)

def mult(args, env):
   args = map(lambda x: eval(x, env), args)
   return reduce(lambda x, y: x * y, args)

def div(args, env):
   args = map(lambda x: eval(x, env), args)
   return reduce(lambda x, y: x / y, args)

def print_(args, env):
   args = map(lambda x: eval(x, env), args)
   for i in args:
      print i,
   print
   return 0

def lt(args, env):
   return eval(args[0], env) < eval(args[1], env)

def gt(args, env):
   return eval(args[0], env) > eval(args[1], env)

def eq(args, env):
   return eval(args[0], env) == eval(args[1], env)

OPS = {
   '+': add,
   '-': sub,
   '*': mult,
   '/': div,
   '<': lt,
   '>': gt,
   '=': eq,
   'print': print_
}

def Error(message):
   print message
   exit(0)

def ExecuteStatements(statements, env):
   for statement in statements[:-1]:
      eval(statement, env)
   return eval(statements[-1], env)

def IfBlock(exp, env):
   if eval(exp[1], env):
      return ExecuteStatements(exp[2], env)
   index = 3
   while exp[index] == 'elif':
      if eval(exp[index + 1], env):
         return ExecuteStatements(exp[index + 2], env)
      index += 3
   return ExecuteStatements(exp[-1], env)

def ForBlock(exp, env):
   eval(exp[1], env)
   while eval(exp[2], env):
      ExecuteStatements(exp[-1], env)
      eval(exp[3], env)
   return 0

def eval(exp, env):
   if type(exp) == dict and 'def' in exp:
      return ExecuteStatements(exp['def'], env)
   if type(exp) in [int, long, float, bool]:
      return exp
   if type(exp) in [str, unicode]:
      if exp in OPS:
         Error('%s is a keyword.' % exp)
      if exp not in env:
         Error('Variable %s not bound.' % exp)
      return env[exp]
   elif type(exp) == dict:
      ret = False
      for var in exp:
         ret = env[var] = eval(exp[var], env)
      return ret
   elif type(exp) == list:
      name = exp[0]
      args = exp[1:]
      if name in OPS:
         return OPS[name](exp[1:], env)
      if name == 'if':
         return IfBlock(exp, env)
      if name == 'for':
         return ForBlock(exp, env)
      if name not in env:
         Error('Function %s not in environment.' % exp)
      f = env[name]
      new_env = {}
      for (p, v) in zip(f['params'], args):
         new_env[p] = eval(v, env)
      return eval(f, new_env)
   else:
      return eval(exp, env)
   Error('You shouldn\'t be here! ' + exp.__str__())

def main():
   with open('main.jsol', 'r') as f:
      j = json.load(f)
      print eval(j['main'], j)

if __name__ == '__main__':
   main()
