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

    def __init__(self, contents: str, *, input_file: str, output_file=None):
        '''
        Parameters
        ----------
            contents: str
                The contents of the file the preprocessor should parse.
            input_file: str
                The name of the input file (used for the inlude directive).
            output_file: file-like object
                The output file to write to.
        '''
        self.tree = tree = parse(contents)
        self._iter_tree = iter(tree)

        self.block = None

        self.write_offset = 0
        self.source = contents

        self._input = input_file
        self._output = output_file
        self.body = io.StringIO()

    def __len__(self):
        return len(self.body.getvalue())

    def op_define(self, pos: tuple, name: str, value: str=None):
        '''
        handler for the `define` directive.

        usage:
        ```py
        ##define _PRESENCE_
        ##define _MAGIC_ 0x86
        ```

        Parameters
        ----------
        pos: Tuple[int, int]
            The start and end position of the declaration (not including operands)
        name: str
            The label to define
        value: Optional[str]
            The value bound to the label
            The value will automatically be casted to its appropriate type.
        '''
        cast = lambda v: v

        if value is None:
            pass

        elif value.isdigit():
            cast = int

        elif value[0] in ('"', '\''):
            value = value[1:-1]

        self.namespace[name] = cast(value)

    def op_ifdef(self, pos: tuple, label: str):
        '''
        handler for `ifdef` declaration.

        usage:
        ```python
        ##ifdef __LINUX__
        print('Compiled on linux.')
        ##else
        print('Not compiled on linux.')
        ##endif
        ```

        Parameters
        ----------
        pos: Tuple[int, int]
            The start and end position of the declaration (not including operands)
        name: str
            The label whos presence must be checked.
        '''
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

    def op_endif(self, pos: tuple):
        '''
        handler for `endif` directive.

        usage:
            Anywhere you use a conditional declaration, you must use an endif.

        Currently a NOP.
        '''
        pass # we should probably be doing some sanity checks here.

    def op_include(self, pos: tuple, file: str):
        '''
        handler for `include` directive.

        usage:
        ```python
        ##include "some_file.py"
        ```

        Parameters
        ----------
        pos: Tuple[int, int]
            The start and end position of the declaration (not including operands)
        file: str
            The file whos contents must be inlined.
        '''
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
