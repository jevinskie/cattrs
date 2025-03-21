"""Useful internal functions."""

from types import CodeType
from typing import Any, Callable, NoReturn, TypeVar

from ._compat import TypeAlias
from .errors import StructureHandlerNotFoundError

T = TypeVar("T")

Predicate: TypeAlias = Callable[[Any], bool]
"""A predicate function determines if a type can be handled."""


def identity(obj: T) -> T:
    """The identity function."""
    return obj


def raise_error(_, cl: Any) -> NoReturn:
    """At the bottom of the condition stack, we explode if we can't handle it."""
    msg = f"Unsupported type: {cl!r}. Register a structure hook for it."
    raise StructureHandlerNotFoundError(msg, type_=cl)


import hashlib
import astroid
import sys
import pdb
import IPython

_seen_code = set()
_seen_func_names: set[str] = set()
_seen_digests: dict[str, bytes] = dict()


class JevException(Exception): pass


def evalz(source: Any,
        globals: dict[str, Any] | None = None,
        locals: dict[str, object] | None = None) -> Any:
    eval(source, globals, locals)


def compilez(source: str, filename: str, mode: str) -> CodeType:
    if mode != "exec":
        raise NotImplementedError(f"mode '{mode}' != exec")
    h = hashlib.sha1(source.encode(), usedforsecurity=False)
    digest = h.digest()
    d = digest.hex()
    # print(f"filename: {filename} str: {str(filename)}")
    # print(f"src: {source}")
    open(f"/tmp/cattrs/hashed/cattrs_dbg_{d}.py", "w").write(source)
    mod = astroid.parse(source)
    func = mod.body[0]
    if not isinstance(func, astroid.FunctionDef):
        raise TypeError(f"Expection FunctionDef for '{filename}' in:\n{source}")
    # filename = <cattrs generated structure instdec.util.Trits>
    pfile = filename[1:-1]
    pfile = pfile.replace(" ", "_")
    pfile = pfile.replace(".", "_")
    fname = func.name
    print(f"filename: {filename}", flush=True)
    if filename == "":
        # pdb.set_trace()
        # IPython.embed()
        # raise JevException(f"no filename fname: '{fname}' source: {source}")
        pass
    key = f"{pfile}-KVP-{fname}"
    if pfile in _seen_func_names:
        if key in _seen_digests and digest != _seen_digests[key]:
            emsg = f"func name: '{fname}' from filename '{filename}' sha1: {d} pfile: '{pfile}' is already seen. DIDSEEN: {_seen_func_names}\nsource:\n{source}"
            print(emsg)
            # raise JevException(emsg)
        elif key not in _seen_digests:
            emsg = f"func name: '{fname}' from filename '{filename}' sha1: {d} pfile: '{pfile}' is already seen. NOTSEEN: {_seen_func_names}\nsource:\n{source}"
            print(emsg)
            # raise JevException(emsg)
    _seen_func_names.add(pfile)
    _seen_digests[key] = digest
    open(f"/tmp/cattrs/named/fname_{fname}_pfile_{pfile}_hash_{d}.py", "w").write(source)
    return compile(source, filename, mode)
