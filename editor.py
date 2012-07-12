#!/usr/bin/env python
# This program loads the JSOL Fibonacci file, and then edits it to start at
# a higher number. This shows how JSOL programs can be easily edited in code
# because they are representable as a standard data structure.

import jsol
import json

with open('examples/fib.jsol') as f:
   fib = json.load(f)

fib['main']['def'].insert(0, ['print', {'lit': 'Let\'s start fib at 8!'}])
fib['fib']['def'][0]['a'] = 5
fib['fib']['def'][0]['b'] = 8

# fib will now print 8 first.
jsol.Eval(fib)
