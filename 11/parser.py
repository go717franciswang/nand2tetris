import symbol_table
import vm_writer

class NoMatch(Exception):
    pass

operators = {'+','-','*','/','&','|','<','>','='}
keyword_constants = {'true','false','null','this'}
type2segment = {
        'static': 'static',
        'field': 'this',
        'arg': 'argument',
        'var': 'local'
        }

class Parser:
    index = 0
    cur_func_name = None

    def __init__(self, tokens, writer, module_name):
        self.tokens = tokens
        self.symbols = symbol_table.SymbolTable()
        self.writer = writer
        self.module_name = module_name

    def parse(self):
        return self.compile_class()

    def advance(self, valid_type, valid_elements=None):
        t, e = self.tokens[self.index]
        if t != valid_type:
            info = ' '.join([x[1] for x in self.tokens[self.index-5:self.index+2]])
            raise NoMatch('Expected type: '+valid_type+', Got type: '+t+' => "'+e+'", '+info)
        if valid_elements is not None and e not in valid_elements:
            raise NoMatch('Expected token: '+' | '.join(valid_elements)+', Got: '+e)
        self.index += 1
        return (t, e)

    def cur_token(self):
        return self.tokens[self.index][1]

    def cur_type(self):
        return self.tokens[self.index][0]

    def compile_class(self):
        elements = []
        elements.append(self.advance('keyword', {'class'}))
        elements.append(self.advance('identifier'))
        elements.append(self.advance('symbol', {'{'}))

        while self.cur_token() in {'static','field'}:
            elements.append(self.compile_class_var_dec())

        while self.cur_token() in {'constructor','function','method'}:
            elements.append(self.compile_subroutine())

        elements.append(self.advance('symbol', {'}'}))
        return ('class', elements)

    def compile_class_var_dec(self):
        elements = []
        elements.append(self.advance('keyword', {'static','field'}))
        kind = elements[-1][1]
        try:
            elements.append(self.advance('keyword', {'int','char','boolean'}))
        except NoMatch as e:
            elements.append(self.advance('identifier'))
        type = elements[-1][1]
        elements.append(self.advance('identifier'))
        name = elements[-1][1]
        self.symbols.define(name, type, kind)

        while self.cur_token() == ',':
            elements.append(self.advance('symbol', {','}))
            elements.append(self.advance('identifier'))
            name = elements[-1][1]
            self.symbols.define(name, type, kind)
        elements.append(self.advance('symbol', {';'}))
            
        return ('classVarDec', elements)

    def compile_subroutine(self):
        self.symbols.start_subroutine()
        elements = []
        elements.append(self.advance('keyword', {'constructor','function','method'}))
        try:
            elements.append(self.advance('keyword', {'void','int','char','boolean'}))
        except NoMatch as e:
            elements.append(self.advance('identifier'))
        elements.append(self.advance('identifier'))
        self.cur_func_name = elements[-1][1]

        elements.append(self.advance('symbol', {'('}))
        elements.append(self.compile_parameter_list())
        elements.append(self.advance('symbol', {')'}))
        elements.append(self.compile_subroutine_body())

        return ('subroutineDec', elements)

    def compile_parameter_list(self):
        elements = []
        if self.cur_token() != ')':
            try:
                elements.append(self.advance('keyword', {'int','char','boolean'}))
            except NoMatch as e:
                elements.append(self.advance('identifier'))
            type = elements[-1][1]
            elements.append(self.advance('identifier'))
            name = elements[-1][1]
            self.symbols.define(name, type, 'arg')

            while self.cur_token() == ',':
                elements.append(self.advance('symbol', {','}))
                try:
                    elements.append(self.advance('keyword', {'int','char','boolean'}))
                except NoMatch as e:
                    elements.append(self.advance('identifier'))
                type = elements[-1][1]
                elements.append(self.advance('identifier'))
                name = elements[-1][1]
                self.symbols.define(name, type, 'arg')
        return ('parameterList', elements)

    def compile_subroutine_body(self):
        elements = []
        elements.append(self.advance('symbol', {'{'}))
        nlocals = 0
        while self.cur_token() == 'var':
            nlocals += 1
            elements.append(self.compile_var_dec())
        self.writer.write_function(self.cur_func_name, nlocals)
        elements.append(self.compile_statements())
        elements.append(self.advance('symbol', {'}'}))
        return ('subroutineBody', elements)

    def compile_statements(self):
        elements = []
        while True:
            e = self.cur_token()
            if e == 'let':
                elements.append(self.compile_let())
            elif e == 'do':
                elements.append(self.compile_do())
            elif e == 'if':
                elements.append(self.compile_if())
            elif e == 'while':
                elements.append(self.compile_while())
            elif e == 'return':
                elements.append(self.compile_return())
                break
            else:
                break
        return ('statements', elements)

    def compile_var_dec(self):
        elements = []
        elements.append(self.advance('keyword', {'var'}))
        try:
            elements.append(self.advance('keyword', {'int','char','boolean'}))
        except NoMatch as e:
            elements.append(self.advance('identifier'))
        type = elements[-1][1]
        elements.append(self.advance('identifier'))
        name = elements[-1][1]
        self.symbols.define(name, type, 'var')

        while self.cur_token() == ',':
            elements.append(self.advance('symbol', {','}))
            elements.append(self.advance('identifier'))
            name = elements[-1][1]
            self.symbols.define(name, type, 'var')

        elements.append(self.advance('symbol', {';'}))
        return ('varDec', elements)

    def compile_do(self):
        elements = []
        elements.append(self.advance('keyword', {'do'}))
        elements.append(self.advance('identifier'))
        if self.cur_token() == '.':
            elements.append(self.advance('symbol', {'.'}))
            elements.append(self.advance('identifier'))
        elements.append(self.advance('symbol', {'('}))
        elements.append(self.compile_expression_list())
        elements.append(self.advance('symbol', {')'}))
        elements.append(self.advance('symbol', {';'}))
        return ('doStatement', elements)

    def compile_let(self):
        elements = []
        elements.append(self.advance('keyword', {'let'}))
        elements.append(self.advance('identifier'))
        name = elements[-1][1]

        self._use_temp_writer()
        if self.cur_token() == '[':
            elements.append(self.advance('symbol', {'['}))
            elements.append(self.compile_expression())
            elements.append(self.advance('symbol', {']'}))
        stack = self.writer.getvalue()
        self._use_orig_writer()

        elements.append(self.advance('symbol', {'='}))
        elements.append(self.compile_expression())
        elements.append(self.advance('symbol', {';'}))

        type = self.symbols.type_of(name)
        segment = type2segment[type]
        index = self.symbols.index_of(name)
        if stack == '': # not an array, direct assignment
            self.writer.write_pop(segment, index)
        else:           # array, push index expression, array pointer, compute offset pointer, assign
            self.writer.write_content(stack)
            self.writer.write_push(segment, index)
            self.writer.write_arithmetic('add')
            self.writer.write_pop('pointer', 1)
            self.writer.write_pop('that', 0)

        return ('letStatement', elements)

    def _use_temp_writer(self):
        self.orig_writer = self.writer
        self.writer = vm_writer.VmWriter(temp=True)

    def _use_orig_writer(self):
        self.writer.close()
        self.writer = self.orig_writer

    def compile_while(self):
        elements = []
        elements.append(self.advance('keyword', {'while'}))
        elements.append(self.advance('symbol', {'('}))
        elements.append(self.compile_expression())
        elements.append(self.advance('symbol', {')'}))
        elements.append(self.advance('symbol', {'{'}))
        elements.append(self.compile_statements())
        elements.append(self.advance('symbol', {'}'}))
        return ('whileStatement', elements)

    def compile_return(self):
        elements = []
        elements.append(self.advance('keyword', {'return'}))
        if self.cur_token() != ';':
            elements.append(self.compile_expression())
        elements.append(self.advance('symbol', {';'}))
        return ('returnStatement', elements)

    def compile_if(self):
        elements = []
        elements.append(self.advance('keyword', {'if'}))
        elements.append(self.advance('symbol', {'('}))
        elements.append(self.compile_expression())
        elements.append(self.advance('symbol', {')'}))
        elements.append(self.advance('symbol', {'{'}))
        elements.append(self.compile_statements())
        elements.append(self.advance('symbol', {'}'}))
        if self.cur_token() == 'else':
            elements.append(self.advance('keyword', {'else'}))
            elements.append(self.advance('symbol', {'{'}))
            elements.append(self.compile_statements())
            elements.append(self.advance('symbol', {'}'}))
        return ('ifStatement', elements)

    def compile_expression(self):
        elements = []
        elements.append(self.compile_term())
        while self.cur_token() in operators:
            elements.append(self.advance('symbol', operators))
            elements.append(self.compile_term())

        return ('expression', elements)

    def compile_term(self):
        elements = []
        if self.cur_type() == 'integerConstant':
            elements.append(self.advance('integerConstant'))
        elif self.cur_type() == 'stringConstant':
            elements.append(self.advance('stringConstant'))
        elif self.cur_token() in keyword_constants:
            elements.append(self.advance('keyword', keyword_constants))
        elif self.cur_type() == 'identifier':
            elements.append(self.advance('identifier'))
            if self.cur_token() == '[':
                elements.append(self.advance('symbol',{'['}))
                elements.append(self.compile_expression())
                elements.append(self.advance('symbol',{']'}))
            elif self.cur_token() == '(':
                elements.append(self.advance('symbol',{'('}))
                elements.append(self.compile_expression_list())
                elements.append(self.advance('symbol',{')'}))
            elif self.cur_token() == '.':
                elements.append(self.advance('symbol',{'.'}))
                elements.append(self.advance('identifier'))
                elements.append(self.advance('symbol',{'('}))
                elements.append(self.compile_expression_list())
                elements.append(self.advance('symbol',{')'}))
        elif self.cur_token() == '(':
            elements.append(self.advance('symbol',{'('}))
            elements.append(self.compile_expression())
            elements.append(self.advance('symbol',{')'}))
        elif self.cur_token() in {'-','~'}:
            elements.append(self.advance('symbol',{'-','~'}))
            elements.append(self.compile_term())
        else:
            raise NoMatch()
            # raise Exception(self.tokens[self.index-5:self.index+1])

        return ('term', elements)

    def compile_expression_list(self):
        elements = []
        while True:
            save_index = self.index
            try:
                elements.append(self.compile_expression())
                save_index = self.index
                elements.append(self.advance('symbol', {','}))
            except NoMatch as e:
                self.index = save_index
                break
        return ('expressionList', elements)
