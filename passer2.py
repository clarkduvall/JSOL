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

# This program illustrates how a JSOL program can be sent between applications.
# A fib function is created in the first Eval, and then sent to the second Eval
# to be run.

import jsol
import json
import parser

with open('syntax/part1.j') as f:
   fib = jsol.Eval(parser.Parse(f.read())).json()

print 'JSOL created!:'
print json.dumps(fib, indent=3)
print 'Passing to other instance...'

with open('syntax/part2.j') as f:
   jsol.Eval(parser.Parse(f.read()), argv=fib)
