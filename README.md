# pyproc
A Python preprocessor implemenatation

## Installation

You can install pyproc via pip:
 - `pip install --user -U git+https://github.com/mental32/pyproc`

or git clone and run `python setup.py install --user`

## Usage

Current usage is through `python -m pyproc <file> [-o (output file)]`

## Examples

Take, for example, a file with the following contents.
```python
##ifdef __PY2__
print "Compiled using python2"
##else
print("Compiled using python3")
##endif
```

And then we run it through the preprocessor with:
 - `python -m pyproc example.py`

Depending on if your `python` pointed to an implementation of Python 2 or Python 3 you should only see one of the print statements.
