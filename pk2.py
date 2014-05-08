#!/usr/bin/env python

import sys, os

import rs5file

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('archives', nargs='*', metavar='ARCHIVE')
    parser.add_argument('-x', '--extract', action='store_true',
            help='Extract the files from archive')
    args = parser.parse_args()

    for file in args.archives:
        pk2 = open(file, 'rb')
        size = os.fstat(pk2.fileno()).st_size
        while pk2.tell() < size:
            f = rs5file.rs5_file_decoder_factory(pk2, pk2=True)
            if f.magic == 'FREE':
                print>>sys.stderr, 'Skipping FREE %s...' % f.filename
                pk2.seek(f.filesize, 1)
                continue
            if args.extract:
                if hasattr(f, 'extract_chunks'):
                    f.extract_chunks('.', False)
                else:
                    path = f.filename.replace('\\', os.path.sep)
                    rs5file.mkdir_recursive(os.path.dirname(path))
                    try:
                        data = f.data
                        open(path, 'wb').write(data)
                    except Exception as e:
                        print '%s occurred while writing %s %s: %s' % (e.__class__.__name__, f.magic, f.filename, str(e))
            else:
                pk2.seek(f.filesize, 1)
            print f.magic, f.filename

if __name__ == '__main__':
    sys.exit(main())
