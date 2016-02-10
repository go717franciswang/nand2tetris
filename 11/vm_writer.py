import StringIO

# definitions pg.240
class VmWriter:
    def __init__(self, out_filename=None, temp=False):
        if temp:
            self.out = StringIO.StringIO()
        else:
            self.out = open(out_filename, 'w')

    def write_push(self, segment, index):
        self.out.write('push %s %s\n' % (segment, index))

    def write_pop(self, segment, index):
        self.out.write('pop %s %s\n' % (segment, index))

    def write_arithmetic(self, command):
        self.out.write(command + '\n')

    def write_label(self, label):
        self.out.write('label %s\n' % (label,))

    def write_goto(self, label):
        self.out.write('goto %s\n' % (label,))

    def write_if(self, label):
        self.out.write('if-goto %s\n' % (label,))

    def write_call(self, name, nargs):
        self.out.write('call %s %s\n' % (name, nargs))

    def write_function(self, name, nlocals):
        self.out.write('function %s %s\n' % (name, nlocals))

    def write_return(self):
        self.out.write('return\n')

    def write_content(self, content):
        self.out.write(content)

    def close(self):
        self.out.close()
