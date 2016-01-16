#!/usr/bin/env python

def parse(line):
    cmd = line.split('//')[0].strip()
    if cmd == '':
        return None

    tokens = cmd.split(' ')

