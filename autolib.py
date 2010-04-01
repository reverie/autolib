import imp, os, parser, tempfile, re, urllib

from httplib2 import Http
from urllib import urlencode

AUTOLIB_SERVER = 'http://ianab.com/autolib-serv/'

lib_re = '[a-z][\w\-\.]*'

class NoSuchLib(Exception):
    pass

class ServerStore(object):
    def get_src(self, name):
        # TODO: get from server
        url = self.url + 'lib/' + name + '/'
        h = Http()
        resp, content = h.request(url, 'GET')
        code = int(resp['status'])
        if code == 404:
            raise AttributeError, 'Library not found.'
        elif code == 500:
            raise Exception, 'The server could not handle your request.'
        else:
            return content

    def set_src(self, name, src):
        # TODO: send to server
        url = self.url + 'lib/' + name + '/'
        h = Http()
        data = urlencode({'src': src})
        resp, content = h.request(url, 'POST', data)

        code = int(resp['status'])
        if code == 500:
            raise Exception, 'The server could not handle your request.'


    def list_modules(self):
        url = self.url + 'list/'
        h = Http()
        resp, content = h.request(url, 'GET')
        code = int(resp['status'])
        if code == 500:
            raise Exception, 'The server could not handle your request.'
        return content.split()

    def __init__(self, url):
        self.url = url

class Autolib(object):
    def _make_module(self, name, src):
        fd, path = tempfile.mkstemp(suffix='.py')
        f = os.fdopen(fd, 'w')
        f.write(src)
        f.close()
        return imp.load_source(name, path)

    def __getattr__(self, modname):
        if modname in self._module_cache:
            return self._module_cache[modname]
        src = self._store.get_src(modname)
        mod = self._make_module(modname, src)
        self._module_cache[modname] = mod
        return mod

    def __setattr__(self, name, val):
        # TODO: validate name (starts with letter, lowercase_-digits)
        if name.startswith('_'):
            return object.__setattr__(self, name, val)
        if not re.match(lib_re, name):
            raise ValueError, "Invalid library name."
        path = val.__file__
        if not path.endswith('.py'):
            raise ValueError, 'Module must be a .py file'
        src = open(path).read()
        try:
            parser.suite(src)
        except (TypeError, SyntaxError, parser.ParserError):
            raise ValueError, 'Module does not parse correctly.'
        self._store.set_src(name, src)

    def List(self):
        return self._store.list_modules()

    def __init__(self, store=ServerStore(AUTOLIB_SERVER)):
        self._module_cache = {}
        self._store = store

autolib = Autolib()

