#!/usr/bin/env python

import tokenizer
import parser
import util
from lxml import etree
import vm_writer

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
        tokens = tokenizer.tokenize(f)
        vm_filename = '.'.join(f.split('.')[0:-1])+'.vm'
        writer = vm_writer.VmWriter(vm_filename)
        module_name = f.split('.')[-2].split('/')[-1]
        p = parser.Parser(tokens, writer, module_name)
        tree = p.parse()
        xml = etree.tostring(util.tree2xml(tree), pretty_print=True)
        fileout = '.'.join(f.split('.')[0:-1])+'.F.xml'
        print fileout
        fout = open(fileout, 'w')
        fout.write(xml)
        writer.close()


