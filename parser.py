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

# This is a parser for a new syntax that can be used to write JSOL. Examples
# of this can be found in the syntax/ folder.
# I haven't had a chance to clean this up, so right now its UGLY.

import jsol
import string
import sys

def Error(s):
   print s
   exit(0)

def _ParseString(code):
   buf = ''
   for i in range(len(code)):
      if code[i] == '"' and code[i - 1] != '\\':
         return (code[i + 1:], {'lit': buf})
      if code[i] != '\\' or code[i - 1] == '\\':
         if code[i - 1] == '\\' and code[i] == 'n':
            buf += '\n'
            continue
         buf += code[i]

def _GetParens(code):
   l = 0
   for i in range(len(code)):
      if code[i] == '(':
         l += 1
      if code[i] == ')':
         if l == 0:
            return (code[:i], code[i + 1:])
         l -= 1
   Error('No closing parens')

def _ParseCall(code, name):
   args, rest = _GetParens(code)
   args_list = []
   while len(args.strip()):
      args, arg = _Parse(args)
      args_list.append(arg)
   return (rest, [name] + args_list)

def _ParseCond(if_list, code):
   cond, code = code.split('{', 1)
   if_list.append(_Parse(cond)[1])
   code, statements = _ParseBlock('{' + code)
   if_list.append(statements)
   return code

def _ParseIf(code):
   if_list = ['if']
   code = _ParseCond(if_list, code)
   temp, next = _Parse(code)
   while next == 'elif':
      code = temp
      _ParseCond(if_list, code)
      temp, next = _Parse(code)
   if next == 'else':
      code = temp
      code, statements = _ParseBlock(code)
      if_list.append(statements)
   return (code, if_list)

def _ParseBlock(code):
   code = code.lstrip()
   if code[0] != '{':
      Error('Code block must begin with "{"')
   code = code[1:]
   statements = []
   while code.lstrip()[0] != '}':
      code, statement = _Parse(code)
      statements.append(statement)
   return (code.lstrip()[1:], statements)

def _ParseFunction(code):
   params, rest = code.split(')', 1)
   params = params.split()
   rest, body = _ParseBlock(rest)
   return (rest, { 'params': params, 'def': body })

def _ParseList(code):
   statements = []
   while code.lstrip()[0] != ']':
      code, statement = _Parse(code)
      statements.append(statement)
   return (code.lstrip()[1:], {'lit': statements})

def _ParseDict(code):
   code, d_list = _ParseBlock('{' + code)
   d = {}
   [d.update(x) for x in d_list]
   return (code, {'lit': d})

def _GetNum(num):
   if num == 'null':
      return None
   if num.isdigit():
      return int(num)
   try:
      return float(num)
   except:
      return num

def _Parse(code):
   buf = ''
   has_space = False
   for i in range(1, len(code) + 1):
      c = code[i - 1]
      if c in string.whitespace + ',;':
         has_space = True
         continue
      if has_space and buf or c in [']', '}', ')']:
         if buf == 'if':
            return _ParseIf(code[i - 1:])
         return (code[i - 1:], _GetNum(buf))
      if c == ':':
         rest, result = _Parse(code[i:])
         return (rest, { buf: result })
      if c == '"':
         return _ParseString(code[i:])
      if c == '(':
         if buf == 'def':
            return _ParseFunction(code[i:])
         code, call = _ParseCall(code[i:], buf)
         while len(code.lstrip()) and code.lstrip()[0] == '(':
            code, call = _ParseCall(code.lstrip()[1:], call)
         return (code, call)
      if c == '[':
         return _ParseList(code[i:])
      if c == '{':
         return _ParseDict(code[i:])
      buf += c
      has_space = False
   return (code[i:], _GetNum(buf))

def Parse(code):
   d = {}
   while code:
      code, var = _Parse(code)
      d.update(var)
   return d

if __name__ == '__main__':
   for arg in sys.argv[1:]:
      with open(arg, 'r') as f:
         jsol.Eval(Parse(f.read()))
