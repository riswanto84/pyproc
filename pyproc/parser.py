#!/usr/bin/python

import re

_command_pattern = r'##([a-zA-Z^\w]+)'
_operand_pattern = r'(".*"|[.^\w]+)+'
_co_body_pattern = r'.+'

def parse(source: str) -> tuple:
    '''
    parse a source string and return a syntax tree containing the command and operands.

    returns: Tuple[Tuple[int, int], str, Tuple[str...]...]
    '''
    for match in re.finditer(_command_pattern, source):
        start, end = match.span()
        args_end = source.index('\n', match.end())
        operands = re.finditer(_operand_pattern, match.string[end:args_end].strip())
        yield (start, end), match[0][2:], tuple(operand[0] for operand in operands)
