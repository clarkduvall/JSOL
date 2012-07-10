#!/usr/bin/env python
# This program illustrates how a JSOL program can be sent between applications.
# A fib function is created in the first Eval, and then sent to the second Eval
# to be run.

import jsol
import json

with open('examples/part1.jsol') as f:
   fib = jsol.Eval(json.load(f)).json()

print 'JSOL created!:'
print json.dumps(fib, indent=3)
print 'Passing to other instance...'

with open('examples/part2.jsol') as f:
   jsol.Eval(json.load(f), argv=fib)
