#!/usr/bin/env python

def parse(line):
    cmd = line.split('//')[0].strip()
    if cmd == '':
        return None

    tokens = cmd.split(' ')
    if tokens[0] == 'push':
        if tokens[1] == 'constant':
            return {'cmd': 'push constant', 'value': tokens[2]}
    elif len(tokens) == 1:
        return {'cmd': tokens[0]}

snippets = {
        'increment SP': ['@SP', 'D=M+1', '@SP', 'M=D'],
        'decrement SP': ['@SP', 'D=M-1', '@SP', 'M=D'],
        'D = *(SP-1)': ['@SP', 'A=M-1', 'D=M'],
        'M = *(SP-1)': ['@SP', 'A=M-1'],
        'M = *(SP-2)': ['@SP', 'A=M-1', 'A=A-1'],
        }
last_label_id = 0

def get_label_id():
    global last_label_id
    lid = str(last_label_id)
    last_label_id += 1
    return lid

def code(parsed):
    cmd = parsed['cmd']
    codes = []
    if cmd == 'push constant':
        codes += ['@'+parsed['value'], # store value in D
                  'D=A',
                  '@SP',   # access global stack
                  'A=M',
                  'M=D']   # push D onto stack
        codes += snippets['increment SP']
    elif cmd == 'add':
        codes += snippets['D = *(SP-1)']
        codes += snippets['M = *(SP-2)']
        codes.append('M=D+M')
        codes += snippets['decrement SP']
    elif cmd == 'sub':
        codes += snippets['D = *(SP-1)']
        codes += snippets['M = *(SP-2)']
        codes.append('M=M-D')
        codes += snippets['decrement SP']
    elif cmd == 'not':
        codes += snippets['D = *(SP-1)']
        codes += snippets['M = *(SP-1)']
        codes.append('M=!D')
    elif cmd == 'eq' or cmd == 'lt' or cmd == 'gt':
        codes += code({'cmd': 'sub'})
        codes += snippets['D = *(SP-1)']
        label_eq = 'TRUE_'+get_label_id()
        label_end = 'END_'+get_label_id()
        codes.append('@'+label_eq)

        cmd2jmp_type = {'eq': 'JEQ', 'lt': 'JLT', 'gt': 'JGT'}
        codes.append('D;'+cmd2jmp_type[cmd])

        codes += snippets['M = *(SP-1)']
        codes += ['M=0',
                  '@'+label_end,
                  '0;JMP',
                  '('+label_eq+')']
        codes += snippets['M = *(SP-1)']
        codes += ['M=-1',
                  '('+label_end+')']
    elif cmd == 'neg':
        codes += snippets['M = *(SP-1)']
        codes.append('M=-M')
    elif cmd == 'and':
        codes += snippets['D = *(SP-1)']
        codes += snippets['M = *(SP-2)']
        codes.append('M=D&M')
        codes += snippets['decrement SP']
    elif cmd == 'or':
        codes += snippets['D = *(SP-1)']
        codes += snippets['M = *(SP-2)']
        codes.append('M=D|M')
        codes += snippets['decrement SP']

    return codes

    # elif cmd == 'eq':


if __name__ == '__main__':
    import sys
    filein = sys.argv[1]
    fileout = filein.split('.')[0]+'.asm'
    fout = open(fileout, 'w')
    for line in open(filein).readlines():
        parsed = parse(line)
        if parsed is None:
            continue

        codes = code(parsed)
        fout.write('\n'.join(codes)+'\n')
