# typetrace

Trace Python execution and record type information for function calls.
Produces type annotations which strongly resemble [PEP 484](https://www.python.org/dev/peps/pep-0484/) "type comments".
Probably works in Python 2 and 3.


# Usage

~~~python
import typetrace
tt = typetrace.TypeTracer()

...

# start tracing
tt.set_trace()

# do some interesting stuff here
# consider invoking a test suite, or large sample application

# end tracing
tt.end_trace()

# print traced type annotations
tt.print_types()

# or write them to a file by passing a file object to tt.write_types(f)
~~~

Output looks like this:

~~~
lib/python2.7/inspect.py:155 isgeneratorfunction   # type: (Callable) -> bool
lib/python2.7/UserDict.py:103 __contains__     # type: (str) -> bool
lib/python2.7/UserDict.py:91 get   # type: (str, Union[None, int]) -> Union[None, int]
lib/python2.7/encodings/__init__.py:49 normalize_encoding      # type: (str) -> str
lib/python2.7/encodings/__init__.py:71 search_function # type: (str) -> Tuple[Callable, Callable, classobj, classobj]
lib/python2.7/encodings/utf_8.py:15 decode     # type: (Union[buffer, str], str) -> Tuple[unicode, int]
lib/python2.7/encodings/utf_8.py:33 getregentry        # type: () -> Tuple[Callable, Callable, classobj, classobj]
lib/python2.7/posixpath.py:120 dirname # type: (str) -> str
lib/python2.7/posixpath.py:329 normpath        # type: (str) -> str
lib/python2.7/posixpath.py:358 abspath # type: (str) -> str
lib/python2.7/posixpath.py:52 isabs    # type: (str) -> bool
lib/python2.7/posixpath.py:82 split    # type: (str) -> Tuple[str, str]
lib/python2.7/re.py:138 match  # type: (str, str, int) -> Union[SRE_Match, None]
lib/python2.7/re.py:148 sub    # type: (str, str, str, int, int) -> str
lib/python2.7/re.py:192 compile        # type: (str, int) -> SRE_Pattern
lib/python2.7/re.py:230 _compile       # type: (*Union[str, int]) -> SRE_Pattern
~~~

# Caveats

It works, but:

* It's slow.
* It may generate some nonsensical type annotations.
* It only outputs the Python 2 compatible type comment syntax.
* If you want to add the generated annotations to the source automatically, you'll need to write more code.
* Did I mention it's slow?
* It doesn't handle functions returning multiple lengths of tuples very well. It produces a union of each length it's seen.
* Doesn't simplify `Union[T, None]` to `Optional[T]`.
* It's poorly tested.
* Things that raise exceptions will include `None` among their return types, even if `None` is never otherwise returned.
* Probably doesn't handle `@classmethod` correctly.

# License

MIT license.
