#!/usr/bin/env python

def parse(line):
    cmd = line.split('//')[0].strip()
    if cmd == '':
        return None

    tokens = cmd.split(' ')
    if tokens[0] == 'push':
        if tokens[1] == 'constant':
            return {'cmd': 'push constant', 'value': tokens[2]}
    elif tokens[0] == 'add':
        return {'cmd': 'add'}

def code(parsed):
    cmd = parsed['cmd']
    if cmd == 'push constant':
        return '''
            @'''+parsed['value']+''' // store value in D
            D=A
            @SP   // access global stack
            A=M
            M=D   // push D onto stack
            @SP   // increment SP
            D=M+1
            @SP
            M=D'''
    elif cmd == 'add':
        return '''
            @SP   // set D = *(SP-1)
            A=M-1
            D=M
            @SP   // set *(SP-2) to *(SP-2) + *(SP-1)
            A=M-1
            A=A-1
            M=D+M
            @SP   // decrement SP
            D=M-1
            @SP
            M=D'''

if __name__ == '__main__':
    import sys
    filein = sys.argv[1]
    fileout = filein.split('.')[0]+'.asm'
    fout = open(fileout, 'w')
    for line in open(filein).readlines():
        parsed = parse(line)
        if parsed is None:
            continue

        asm = code(parsed)
        fout.write(asm + '\n')
