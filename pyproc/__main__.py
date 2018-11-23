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

    output_file = args.output_file or '%s_proc.py' % args.file.rsplit('.', 1)[0]

    with open(output_file, 'w') as inf:
        proc = pyproc.Preprocessor(contents, output=inf)
        proc.process()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='The source file to parse.')
    parser.add_argument('-o', metavar='output_file', dest='output_file', default=None)
    main(parser.parse_args())
