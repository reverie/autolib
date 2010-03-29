import imp, os, parser, tempfile

AUTOLIB_SERVER = 'http://ianab.com/autolib-serv/'

class ServerComm(object):
    def get_src(self, name):
        # TODO: get from server

    def set_src(self, name, src):
        # TODO: send to server

    def list_modules(self):
        pass

    def __init__(self, url):
        self.url = url

class Autolib(object):
    def _make_module(name, src):
        fd, path = tempfile.mkstemp(suffix='.py')
        f = os.fdopen(f, 'w')
        f.write(src)
        f.close()
        return imp.load_source(name, path)

    def __getattr__(self, modname):
        if modname in _module_cache:
            return _module_cache[modname]
        src = self._comm.get_src(name)
        self._make_module(src)
        _module_cache[modname] = mod
        return mod

    def __setattr__(self, name, mod):
        # TODO: validate name (starts with letter, lowercase_-digits)
        path = mod.__file__
        if not path.endswith('.py'):
            raise ValueError, 'Module must be a .py file'
        src = open(path).read()
        try:
            parser.suite(src)
        except (TypeError, SyntaxError, parser.ParserError):
            raise ValueError, 'Module does not parse correctly.'
        self._comm.set(name, src)

    def List(self):
        return _comm.list_modules()

    def __init__(self, comm=ServerComm(AUTOLIB_SERVER)):
        self._module_cache = {}
        self._comm = comm

autolib = Autolib()

