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

import os

def _Open(args):
   return os.open(args[0].val.strip(), os.O_RDWR)

def _Read(args):
   return os.read(args[0].val, args[1].val)

def _Write(args):
   return os.write(args[0].val, args[1].val)

def _Close(args):
   return os.close(args[0].val)

OPS = {
   'open': _Open, 'read': _Read, 'write': _Write, 'close': _Close
}
