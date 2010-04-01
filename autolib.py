import imp, os, parser, tempfile, re, urllib2

from urllib import urlencode

AUTOLIB_SERVER = 'http://ianab.com/autolib/'

lib_re = '[a-z][\w\-\.]*'

def get_url(url, data=None):
    try:
        result = urllib2.urlopen(url, data=data)
    except urllib2.HTTPError, result:
        pass
    return result.code, result.read()

class ServerStore(object):
    def get_src(self, name):
        url = self.url + 'lib/' + name + '/'
        code, content = get_url(url)
        if code == 404:
            raise AttributeError, 'Library not found.'
        elif code != 200:
            raise Exception, 'The server could not handle your request.'
        else:
            return content

    def set_src(self, name, src):
        url = self.url + 'lib/' + name + '/'
        data = urlencode({'src': src})
        code, content = get_url(url, data)
        if code == 403:
            raise ValueError, "Library with that name already exists."
        elif code != 200:
            raise Exception, 'The server could not handle your request.'

    def list_modules(self):
        url = self.url + 'list/'
        code, content = get_url(url)
        if code == 500:
            raise Exception, 'The server could not handle your request.'
        return content.split()

    def __init__(self, url=AUTOLIB_SERVER):
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
        if name.startswith('_'):
            return object.__setattr__(self, name, val)
        if not re.match(lib_re, name):
            raise ValueError, "Invalid library name."
        path = val.__file__
        if path.endswith('.pyc'):
            path = path[:-1]
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

    def __init__(self, store=ServerStore()):
        self._module_cache = {}
        self._store = store

autolib = Autolib()

