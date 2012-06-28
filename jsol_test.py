#!/usr/bin/env python

import json
import os
import unittest

from jsol import Eval

class JSOLTest(unittest.TestCase):
   def _ReadFile(self, filename):
      with open(os.path.join('test_data', filename)) as f:
         return f.read()

   def testJSOL(self):
      self.assertEquals(135, Eval(json.loads(self._ReadFile('test1.jsol'))))

if __name__ == '__main__':
   unittest.main()
