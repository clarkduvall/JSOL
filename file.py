import os

def _Open(args):
   return os.open(args[0].val, os.O_RDWR)

def _Read(args):
   return os.read(args[0].val, args[1].val)

def _Write(args):
   return os.write(args[0].val, args[1].val)

def _Close(args):
   return os.close(args[0].val)

OPS = {
   'open': _Open, 'read': _Read, 'write': _Write, 'close': _Close
}
