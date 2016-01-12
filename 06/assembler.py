#!/usr/bin/env python

def parse(line):
    cmd = line.split('//')[0].strip()
    if cmd == '':
        return None

    if cmd[0] == '@':
        return {'type': 'A', 'address': cmd[1:]}
    elif cmd[0] == '(':
        return {'type': 'pseudo', 'label': cmd[1:-1]}
    else:
        jmp = None
        if ';' in cmd:
            cmd,jmp = cmd.split(';')

        if '=' in cmd:
            dest,comp = cmd.split('=')
        else:
            dest,comp = None,cmd

        return {'type': 'C', 
                'comp': comp, 
                'dest': dest, 
                'jump': jmp}

comp2abin = {
        '0':   '0101010',
        '1':   '0111111',
        '-1':  '0111010',
        'D':   '0001100',
        'A':   '0110000',
        '!D':  '0001101',
        '!A':  '0110001',
        '-D':  '0001111',
        '-A':  '0110011',
        'D+1': '0011111',
        'A+1': '0110111',
        'D-1': '0001110',
        'A-1': '0110010',
        'D+A': '0000010',
        'D-A': '0010011',
        'A-D': '0000111',
        'D&A': '0000000',
        'D|A': '0010101',
        'M':   '1110000',
        '!M':  '1110001',
        '-M':  '1110011',
        'M+1': '1110111',
        'M-1': '1110010',
        'D+M': '1000010',
        'D-M': '1010011',
        'M-D': '1000111',
        'D&M': '1000000',
        'D|M': '1010101'}

dest2bin = {
        None:  '000',
        'M':   '001',
        'D':   '010',
        'MD':  '011',
        'A':   '100',
        'AM':  '101',
        'AD':  '110',
        'AMD': '111'}

jump2bin = {
        None:  '000',
        'JGT': '001',
        'JEQ': '010',
        'JGE': '011',
        'JLT': '100',
        'JNE': '101',
        'JLE': '110',
        'JMP': '111'}

def code(parsed):
    t = parsed['type']
    if t == 'A':
        return '0' + "{0:015b}".format(parsed['address'])
    elif t == 'C':
        return '111' + comp2abin[parsed['comp']] + dest2bin[parsed['dest']] + jump2bin[parsed['jump']]

if __name__ == '__main__':
    import sys
    filein = sys.argv[1]
    fileout = filein.split('.')[0] + '.hack'
    lines = open(filein).readlines()
    fout = open(fileout, 'w')
    parsed = []

    symbols = {
            'SP': 0,
            'LCL': 1,
            'ARG': 2,
            'THIS': 3,
            'THAT': 4,
            'SCREEN': 16384,
            'KBD': 24576}
    for i in xrange(16):
        symbols['R'+str(i)] = i
    new_var_index = 16

    address = 0
    for line in lines:
        p = parse(line)
        if p is None:
            continue
        elif p['type'] == 'pseudo':
            symbols[p['label']] = address
        else:
            parsed.append(p)
            address += 1

    for p in parsed:
        if p['type'] == 'A':
            addr = p['address']
            if addr.isdigit():
                p['address'] = int(addr)
            else:
                if addr not in symbols:
                    symbols[addr] = new_var_index
                    new_var_index += 1
                p['address'] = symbols[addr]
        fout.write(code(p)+"\n")

