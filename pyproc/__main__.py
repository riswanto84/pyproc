import sys
import argparse

try:
    import pyproc
except ImportError:
    sys.path.append('.')
    import pyproc

def main(args):
    with open(args.file) as inf:
        contents = inf.read()

    pyproc.Preprocessor(contents).process()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='The source file to parse.')
    parser.add_argument('-o', metavar='output_file', dest='output_file', default=None)
    main(parser.parse_args())
