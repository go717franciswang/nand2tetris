#!/usr/bin/env python

import tokenizer

if __name__ == '__main__':
    import sys
    import os
    import glob

    filein = sys.argv[1]

    if os.path.isdir(filein):
        fileins = glob.glob(os.path.join(filein, '*.jack'))
    else:
        fileins = [filein]

    for f in fileins:
        print 'compiling ' + str(f)
        tokenizer.tokenize(f)

