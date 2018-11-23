#!/usr/bin/python

import io
import sys

from .parser import parse

__PY_VERSION__ = '__PY%s__' % sys.version_info[0]
_SYS_PLATFORM__ = '__%s__' % sys.platform.upper()

_DEVICE_DATA = {
    _SYS_PLATFORM__: True,
    __PY_VERSION__: None,
}

class Preprocessor:
    ''' Abstract representation of a preprocessor instance. '''

    namespace = {
        '__PYVERSION__': '.'.join(str(_) for _ in sys.version_info[:3]),
        **_DEVICE_DATA,
    }

    def __init__(self, contents, *, input_file, output_file=None):
        self.tree = tree = parse(contents)
        self._iter_tree = iter(tree)

        self.block = None

        self.write_offset = 0
        self.source = contents

        self._input = input_file
        self._output = input_file
        self.body = io.StringIO()

    def __len__(self):
        return len(self.body.getvalue())

    def op_define(self, pos, name, value=None):
        cast = lambda v: v

        if value is None:
            pass

        elif value.isdigit():
            cast = int

        elif value[0] in ('"', '\''):
            value = value[1:-1]

        self.namespace[name] = cast(value)

    def op_ifdef(self, pos, label):
        if label in self.namespace:

            start, end = pos

            while self.block[1] != 'endif':
                self.block = next(self._iter_tree)
                _pos, op, args = self.block
                _end = self.source.index('\n', end)

                self.body.write(self.source[_end:_pos[0]])

                getattr(self, 'op_%s' % op)(_pos, *args)

                start, end = _pos
                self.write_offset += end - (start + self.source.index('\n', end))

        # Skip to the next 'endif'
        while self.block[1] != 'endif':
            self.block = next(self._iter_tree)

    def op_endif(self, pos):
        pass # we should probably be doing some sanity checks here.

    def op_include(self, pos, file):
        start, end = pos
        self.write_offset += end - (start + self.source.index('\n', end))

        if file[0] not in ('"', '\''):
            raise SyntaxError('Include directive must have file argument inside quotes')

        path = self._input.rsplit('/', 1)[0] + '/%s'

        with open(path % file[1:-1]) as inf:
            self.body.write(inf.read())

    def process(self):
        for block in self._iter_tree:
            self.block = block

            pos, op, args = block or self.block
            start, end = pos

            self.body.write(self.source[len(self) + self.write_offset:start])

            getattr(self, 'op_%s' % op)(pos, *args)

            self.write_offset += end - (start + self.source.index('\n', end))

        if self._output:
            self._output.write(self.body.getvalue())
