import imp, os, parser, tempfile

AUTOLIB_SERVER = 'http://ianab.com/autolib-serv/'

class NoSuchLib(Exception):
    pass

class ServerStore(object):
    def get_src(self, name):
        # TODO: get from server
        pass

    def set_src(self, name, src):
        # TODO: send to server
        pass

    def list_modules(self):
        pass

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
        return _store.list_modules()

    def __init__(self, store=ServerStore(AUTOLIB_SERVER)):
        self._module_cache = {}
        self._store = store

autolib = Autolib()

