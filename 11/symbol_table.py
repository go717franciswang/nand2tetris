CLASS_KINDS = {'static', 'field'}
SUBROUTINE_KINDS = {'arg', 'var'}

class SymbolTable:
    def __init__(self):
        self.class_table = {}
        self.type_count = {'static': 0, 'field': 0}
        self.start_subroutine()

    def start_subroutine(self):
        self.subroutine_table = {}
        self.type_count['arg'] = 0
        self.type_count['var'] = 0

    def define(self, name, type, kind):
        index = self.type_count[kind]
        tag = {'index': index, 'type': type, 'kind': kind}
        if kind in CLASS_KINDS:
            self.class_table[name] = tag
        elif kind in SUBROUTINE_KINDS:
            self.subroutine_table[name] = tag
        self.type_count[kind] += 1

    def var_count(self, kind):
        return self.type_count[kind]+1

    def kind_of(self, name):
        return self.subroutine_table.get(name, self.class_table.get(name))['kind']

    def type_of(self, name):
        return self.subroutine_table.get(name, self.class_table.get(name))['type']

    def index_of(self, name):
        return self.subroutine_table.get(name, self.class_table.get(name))['index']
