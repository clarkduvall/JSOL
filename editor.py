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

# This program loads the JSOL Fibonacci file, and then edits it to start at
# a higher number. This shows how JSOL programs can be easily edited in code
# because they are representable as a standard data structure.

import jsol
import json

with open('examples/fib.jsol') as f:
   fib = json.load(f)

fib['main']['def'].insert(0, ['println', {'lit': 'Let\'s start fib at 8!'}])
fib['fib']['def'][0]['a'] = 5
fib['fib']['def'][0]['b'] = 8

# fib will now print 8 first.
jsol.Eval(fib)
