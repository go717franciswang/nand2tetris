class VmWriter:
    def __init__(self, out_filename):
        self.out = open(out_filename, 'w')

    def write_push(self, segment, index):
        """docstring for write_push"""
        pass

    def write_pop(self, segment, index):
        """docstring for write_pop"""
        pass

    def write_arithmetic(self, command):
        """docstring for write_arithmetic"""
        pass

    def write_label(self, label):
        """docstring for write_labelfname"""
        pass

    def write_goto(self, label):
        """docstring for write_goto"""
        pass

    def write_if(self, label):
        """docstring for write_if"""
        pass

    def write_call(self, name, nargs):
        """docstring for write_call"""
        pass

    def write_function(self, name, nlocals):
        """docstring for write_function"""
        pass

    def write_return(self):
        """docstring for write_return"""
        pass

    def close(self):
        self.out.close()
