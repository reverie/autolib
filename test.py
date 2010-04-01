from autolib import Autolib, NoSuchLib, ServerStore, AUTOLIB_SERVER
import tempfile, os, imp

class LocalStore(object):
    def get_src(self, name):
        if name not in self.dict:
            raise NoSuchLib
        return self.dict[name]

    def set_src(self, name, src):
        self.dict[name] = src

    def list_modules(self):
        return self.dict.keys()

    def __init__(self):
        self.dict = {}


a = Autolib(store=LocalStore())

fd, path = tempfile.mkstemp(suffix='.py')
f = os.fdopen(fd, 'w')
f.write("""
import math

en = enumerate

def foo():
    return 3

def bar():
    return math.exp(-1)
""")
f.close()

mod = imp.load_source('testmod', path)

a.tester = mod

print a.tester.foo()
print a.tester.bar()
print a.List()

ss = ServerStore()
b = Autolib(store=ss)

b.tester = mod

print b.tester.foo()
print b.tester.bar()
print b.List()
