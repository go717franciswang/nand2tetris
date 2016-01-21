#!/usr/bin/env python

def parse(line):
    cmd = line.split('//')[0].strip()
    if cmd == '':
        return None

    tokens = cmd.split(' ')
    rs = {'cmd': tokens[0]}
    if tokens[0] in ('push', 'pop'):
        rs['segment'] = tokens[1]
        rs['value'] = tokens[2]
    elif tokens[0] in ('label', 'if-goto', 'goto'):
        rs['label'] = tokens[1]
    elif tokens[0] == 'function':
        rs['name'] = tokens[1]
        rs['lcl_count'] = tokens[2]
    elif tokens[0] == 'call':
        rs['name'] = tokens[1]
        rs['argc'] = tokens[2]

    return rs

snippets = {
        'increment SP': ['@SP', 'D=M+1', '@SP', 'M=D'],
        'decrement SP': ['@SP', 'D=M-1', '@SP', 'M=D'],
        'D = *(SP-1)': ['@SP', 'A=M-1', 'D=M'],
        'M = *(SP-1)': ['@SP', 'A=M-1'],
        'M = *(SP-2)': ['@SP', 'A=M-1', 'A=A-1'],
        '*SP = D': ['@SP', 'A=M', 'M=D'],
        }
last_label_id = 0

def get_label_id():
    global last_label_id
    lid = str(last_label_id)
    last_label_id += 1
    return lid

segment2label = {
        'local': 'LCL',
        'argument': 'ARG',
        'this': 'THIS',
        'that': 'THAT',
        }

def get_mem_offset(segment, offset):
    label = segment2label[segment]
    return ['@'+str(offset), 'D=A', '@'+label, 'A=M+D']

def get_temp_label(value):
    return 'R'+str(int(parsed['value'])+5)

def get_pointer_label(value):
    value = int(value)
    if value == 0:
        return 'THIS'
    elif value == 1:
        return 'THAT'

def get_static_label(value):
    return str(int(value)+16)

def code(parsed):
    cmd = parsed['cmd']
    codes = []
    if cmd == 'push':
        if parsed['segment'] == 'constant':
            codes += ['@'+parsed['value'], 'D=A']
        elif parsed['segment'] == 'temp':
            label = get_temp_label(parsed['value'])
            codes += ['@'+label, 'D=M']
        elif parsed['segment'] == 'pointer':
            label = get_pointer_label(parsed['value'])
            codes += ['@'+label, 'D=M']
        elif parsed['segment'] == 'static':
            label = get_static_label(parsed['value'])
            codes += ['@'+label, 'D=M']
        else:
            codes += get_mem_offset(parsed['segment'], parsed['value'])
            codes.append('D=M')
        codes += snippets['*SP = D']
        codes += snippets['increment SP']
    elif cmd == 'pop':
        if parsed['segment'] == 'temp':
            label = get_temp_label(parsed['value'])
            codes += ['@SP', 'A=M-1', 'D=M', '@'+label, 'M=D']
        elif parsed['segment'] == 'pointer':
            label = get_pointer_label(parsed['value'])
            codes += ['@SP', 'A=M-1', 'D=M', '@'+label, 'M=D']
        elif parsed['segment'] == 'static':
            label = get_static_label(parsed['value'])
            codes += ['@SP', 'A=M-1', 'D=M', '@'+label, 'M=D']
        else:
            codes += get_mem_offset(parsed['segment'], parsed['value'])
            codes += ['D=A', '@R13', 'M=D'] # store segment offset address at R13
            codes += ['@SP', 'A=M-1', 'D=M', '@R13', 'A=M', 'M=D']
        codes += snippets['decrement SP']
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
    elif cmd == 'label':
        codes.append('('+parsed['label']+')')
    elif cmd == 'if-goto':
        codes += snippets['D = *(SP-1)']
        codes += ['@R13', 'M=D']
        codes += snippets['decrement SP']
        codes += ['@R13', 'D=M']
        codes.append('@'+parsed['label'])
        codes.append('D;JNE')
    elif cmd == 'goto':
        codes += ['@'+parsed['label'], '0;JMP']
    elif cmd == 'function':
        codes.append('('+parsed['name']+')')
        for i in xrange(int(parsed['lcl_count'])):
            codes.append('D=0')
            codes += snippets['*SP = D']
            codes += snippets['increment SP']
    elif cmd == 'return':
        codes += ['@LCL', 'D=M', '@R13', 'M=D'] # FRAME = LCL
        codes += ['@5', 'D=A', '@R13', 'A=M-D', 'D=M', '@R14', 'M=D'] # RET = *(FRAME-5)
        codes += snippets['D = *(SP-1)'] + ['@ARG', 'A=M', 'M=D'] # *ARG = pop()
        codes += ['@ARG', 'D=M+1', '@SP', 'M=D'] # SP = ARG+1
        codes += ['@1', 'D=A', '@R13', 'A=M-D', 'D=M', '@THAT', 'M=D'] # THAT = *(FRAME-1)
        codes += ['@2', 'D=A', '@R13', 'A=M-D', 'D=M', '@THIS', 'M=D'] # THIS = *(FRAME-2)
        codes += ['@3', 'D=A', '@R13', 'A=M-D', 'D=M', '@ARG', 'M=D'] # ARG = *(FRAME-3)
        codes += ['@4', 'D=A', '@R13', 'A=M-D', 'D=M', '@LCL', 'M=D'] # LCL = *(FRAME-4)
        codes += ['@R14', 'A=M', '0;JMP'] # goto RET
    elif cmd == 'call':
        ret_label = 'RET'+str(get_label_id())
        codes += ['@'+ret_label, 'D=A']
        codes += snippets['*SP = D']
        codes += snippets['increment SP']
        codes += ['@LCL', 'D=M'] # push LCL
        codes += snippets['*SP = D']
        codes += snippets['increment SP']
        codes += ['@ARG', 'D=M'] # push ARG
        codes += snippets['*SP = D']
        codes += snippets['increment SP']
        codes += ['@THIS', 'D=M'] # push THIS
        codes += snippets['*SP = D']
        codes += snippets['increment SP']
        codes += ['@THAT', 'D=M'] # push THAT
        codes += snippets['*SP = D']
        codes += snippets['increment SP']
        nplus5 = str(int(parsed['argc'])+5)
        codes += ['@'+nplus5, 'D=A', '@SP', 'D=M-D', '@ARG', 'M=D'] # ARG = SP-n-5
        codes += ['@SP', 'D=M', '@LCL', 'M=D'] # LCL = SP
        codes += ['@'+parsed['name'], '0;JMP'] # goto f
        codes.append('('+ret_label+')')

    return codes

if __name__ == '__main__':
    import sys
    import os
    import glob

    filein = sys.argv[1]

    if os.path.isdir(filein):
        fileout = os.path.join(filein, filein.strip('/') + '.asm')
        fileins = glob.glob(os.path.join(filein, '*.vm'))
    else:
        fileout = filein.split('.')[0]+'.asm'
        fileins = [filein]
    fout = open(fileout, 'w')

    for f in fileins:
        for line in open(f).readlines():
            parsed = parse(line)
            if parsed is None:
                continue

            codes = code(parsed)
            fout.write('\n'.join(codes)+'\n')
