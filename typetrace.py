import inspect
import sys

import collections
if sys.version_info.major == 2:
    Callable = collections.Callable
elif sys.version_info.major == 3:
    Callable = collections.abc.Callable


def function_id(frame):
    code = frame.f_code
    ident = code.co_filename, code.co_firstlineno, code.co_name
    return ident


def type_from(arg):
    if isinstance(arg, list) and len(arg) > 0:
        return type(arg), frozenset(type(a) for a in arg)
    if isinstance(arg, tuple) and len(arg) > 0:
        return type(arg), tuple(type(a) for a in arg)
    elif isinstance(arg, dict) and len(arg) > 0:
        return dict, frozenset(type(a) for a in arg.keys()), frozenset(type(a) for a in arg.values())
    else:
        return type(arg)


class Function(object):
    def __init__(self):
        self.args = collections.OrderedDict()
        self.varargs = set()
        self.kwargs = set()
        self.returns = set()

    def add_call(self, frame):
        arginfo = inspect.getargvalues(frame)
        if len(arginfo.args) > 0 and arginfo.args[0] == 'self':
            arginfo.args.pop(0)
        for arg in arginfo.args:
            if arg not in self.args:
                self.args[arg] = set()
            self.args[arg].add(type_from(arginfo.locals[arg]))
        self.varargs |= set(type_from(x) for x in arginfo.locals.get(arginfo.varargs, ()))
        self.kwargs |= set(type_from(x) for x in arginfo.locals.get(arginfo.keywords, {}).values())

    def add_return(self, arg):
        self.returns.add(type_from(arg))


class TypeTracer(object):
    def __init__(self):
        self.funcs = collections.defaultdict(Function)

        code = TypeTracer.end_trace.__code__
        self.end_ident = code.co_filename, code.co_firstlineno, code.co_name

    def __call__(self, frame, event, arg):
        ident = function_id(frame)
        # don't trace the function that ends tracing, we'll never see its return type
        if ident == self.end_ident:
            return self
        if ident[2].startswith('<'):
            return self
        if event == 'call':
            self.funcs[ident].add_call(frame)
            return self
        elif event == 'return':
            self.funcs[ident].add_return(arg)

    def set_trace(self):
        self.old = sys.gettrace()
        sys.settrace(self)

    def end_trace(self):
        sys.settrace(self.old)

    def stringify_types(self):
        for func, data in self.funcs.items():
            yield '{}:{}\t{}'.format(*func) + '\t# type: ' + format_args(data)

    def print_types(self):
        for l in self.stringify_types():
            print(l)

    def write_types(self, fileobj):
        for l in self.stringify_types():
            fileobj.write(l+'\n')


def format_types(t):
    if isinstance(t, (set, frozenset)) and len(t) > 1:
        return 'Union[' + ', '.join(format_types(x) for x in t) + ']'
    elif isinstance(t, (set, frozenset)) and len(t) == 1:
        return format_types(list(t)[0])
    elif isinstance(t, tuple):
        if issubclass(t[0], list):
            return 'List[' + format_types(t[1]) + ']'
        elif issubclass(t[0], tuple):
            return 'Tuple[' + ', '.join(format_types(x) for x in t[1]) + ']'
        elif issubclass(t[0], dict):
            return 'Dict[' + format_types(t[1]) + ', ' + format_types(t[2]) + ']'
    elif t == type(None):
        return 'None'
    elif issubclass(t, Callable):
        return 'Callable'
    else:
        return t.__name__


def format_args(data):
    args = data.args
    varargs = data.varargs
    kwargs = data.kwargs
    returns = data.returns
    out = []
    for arg, types in args.items():
        out.append(format_types(types))
    if varargs:
        out.append('*' + format_types(varargs))
    if kwargs:
        out.append('**' + format_types(kwargs))
    arg_str = '(' + ', '.join(out) + ')'
    arg_str += ' -> ' + format_types(returns)
    return arg_str

if __name__ == '__main__':
    def foo(x, y):
        # type:  (Union[float, int], int) -> Union[float, int]
        return x + y

    def bar(x, y):
        return x + y

    def baz(x, y=3):
        return x + y

    def kwa(*a, **kw):
        # type:  (*Union[str, int], **Union[tuple, dict]) -> NoneType
        return None

    tt = TypeTracer()

    tt.set_trace()


    z = 5
    foo(1, 3)
    foo(1.0, 3)

    bar('a', 'b')
    baz(1)
    baz(x=2)
    kwa()
    kwa(1, '', a=(1, ''), b={'': None})
    kwa(input)

    tt.end_trace()

    tt.print_types()
