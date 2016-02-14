import symbol_table
import vm_writer

class NoMatch(Exception):
    pass

operators = {'+','-','*','/','&','|','<','>','=','~'}
keyword_constants = {'true','false','null','this'}
kind2segment = {
        'static': 'static',
        'field': 'this',
        'arg': 'argument',
        'var': 'local'
        }
operator2arith = {
        '+': 'add',
        '-': 'sub',
        '&': 'and',
        '|': 'or',
        '<': 'lt',
        '>': 'gt',
        '=': 'eq',
        '~': 'not'
        }
operator2func = {
        '*': 'Math.multiply',
        '/': 'Math.divide'
        }

# Jack OS spec: pg. 266

class Parser:
    index = 0
    cur_func_name = None
    label_counter = 0

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
        function_type = elements[-1][1]
        if function_type == 'constructor':
            self.writer.write_push('constant', self.symbols.var_count('field'))
            self.writer.write_call('Memory.alloca', 1)
            self.writer.write_pop('pointer', 0)
        elif function_type == 'method':
            self.writer.write_push('argument', 0)
            self.writer.write_pop('pointer', 0)

        try:
            elements.append(self.advance('keyword', {'void','int','char','boolean'}))
        except NoMatch as e:
            elements.append(self.advance('identifier'))
        return_type = elements[-1][1]
        elements.append(self.advance('identifier'))
        self.cur_func_name = elements[-1][1]

        elements.append(self.advance('symbol', {'('}))
        elements.append(self.compile_parameter_list())
        elements.append(self.advance('symbol', {')'}))
        elements.append(self.compile_subroutine_body())

        if return_type == 'void':
            self.writer.write_push('constant', 0)

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
        func_or_module_name = elements[-1][1]
        is_method = True

        if self.cur_token() == '.':
            elements.append(self.advance('symbol', {'.'}))
            elements.append(self.advance('identifier'))
            # pg.189: function calls always use full name (i.e. classname.function_name)
            # we can use this fact to distinguish function and method
            if func_or_module_name[0].islower():
                instance_name = func_or_module_name
                module_name = self.symbols.type_of(instance_name)
                index = self.symbols.index_of(instance_name)
                kind = self.symbols.kind_of(instance_name)
                segment = kind2segment[kind]
                self.writer.write_push(segment, index)
            else:
                module_name = func_or_module_name
                is_method = False
            func_name = elements[-1][1]
        else:
            module_name = self.module_name
            func_name = func_or_module_name
            self.writer.write_push('pointer', 0)

        elements.append(self.advance('symbol', {'('}))
        elements.append(self.compile_expression_list())
        elements.append(self.advance('symbol', {')'}))
        elements.append(self.advance('symbol', {';'}))

        name = '%s.%s' % (module_name, func_name)
        nargs = self.cur_nargs
        if is_method:
            nargs += 1

        self.writer.write_call(name, nargs)
        self.writer.write_pop('temp', 0)
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
        stack = self.writer.out.getvalue()
        self._use_orig_writer()

        elements.append(self.advance('symbol', {'='}))
        elements.append(self.compile_expression())
        elements.append(self.advance('symbol', {';'}))

        kind = self.symbols.kind_of(name)
        segment = kind2segment[kind]
        index = self.symbols.index_of(name)
        # book (pg. 229) actually didn't defer stack
        # but don't think it will work for situations like let x[0] = x[1]
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

        begin_label = self._gen_label()
        end_label = self._gen_label()
        self.writer.write_label(begin_label)

        elements.append(self.advance('symbol', {'('}))
        elements.append(self.compile_expression())
        elements.append(self.advance('symbol', {')'}))

        self.writer.write_arithmetic('not')
        self.writer.write_if(end_label)

        elements.append(self.advance('symbol', {'{'}))
        elements.append(self.compile_statements())
        elements.append(self.advance('symbol', {'}'}))

        self.writer.write_goto(begin_label)
        self.writer.write_label(end_label)
        return ('whileStatement', elements)

    def compile_return(self):
        elements = []
        elements.append(self.advance('keyword', {'return'}))
        if self.cur_token() != ';':
            elements.append(self.compile_expression())
        elements.append(self.advance('symbol', {';'}))
        self.writer.write_return()
        return ('returnStatement', elements)

    def compile_if(self):
        elements = []
        elements.append(self.advance('keyword', {'if'}))
        elements.append(self.advance('symbol', {'('}))
        elements.append(self.compile_expression())

        
        self.writer.write_arithmetic('not')
        label = self._gen_label()
        self.writer.write_if(label)

        elements.append(self.advance('symbol', {')'}))
        elements.append(self.advance('symbol', {'{'}))
        elements.append(self.compile_statements())
        elements.append(self.advance('symbol', {'}'}))
        if self.cur_token() == 'else':
            elements.append(self.advance('keyword', {'else'}))
            elements.append(self.advance('symbol', {'{'}))
            elements.append(self.compile_statements())
            elements.append(self.advance('symbol', {'}'}))
        self.writer.write_label(label)
        return ('ifStatement', elements)

    def _gen_label(self):
        label = 'LABEL_%s' % (self.label_counter,)
        self.label_counter += 1
        return label

    def compile_expression(self):
        elements = []
        elements.append(self.compile_term())
        while self.cur_token() in operators:
            elements.append(self.advance('symbol', operators))
            op = elements[-1][1]
            elements.append(self.compile_term())
            if op in operator2arith:
                self.writer.write_arithmetic(operator2arith[op])
            else:
                self.writer.write_call(operator2func[op], 2)

        return ('expression', elements)

    # pg.209
    def compile_term(self):
        elements = []
        if self.cur_type() == 'integerConstant':
            elements.append(self.advance('integerConstant'))
            self.writer.write_push('constant', elements[-1][1])
        elif self.cur_type() == 'stringConstant':
            elements.append(self.advance('stringConstant'))
            self.writer.write_push('constant', 3)
            # note that both new and appendChar return the string
            # so we don't need to save the instance onto temp variable
            self.writer.write_call('String.new', 1)
            for char in elements[-1][1]:
                self.writer.write_push('constant', ord(char))
                self.writer.write_call('String.appendChar', 2)
        elif self.cur_token() in keyword_constants:
            elements.append(self.advance('keyword', keyword_constants))
            constant = elements[-1][1]
            if constant == 'true':
                self.writer.write_push('constant', -1)
            elif constant in {'false', 'null'}:
                self.writer.write_push('constant', 0)
            else:
                self.writer.write_push('this', 0)
        elif self.cur_type() == 'identifier':
            elements.append(self.advance('identifier'))
            name = elements[-1][1]

            if self.cur_token() == '[':
                segment = kind2segment[self.symbols.kind_of(name)]
                index = self.symbols.index_of(name)
                self.writer.write_push(segment, index)

                elements.append(self.advance('symbol',{'['}))
                elements.append(self.compile_expression())
                elements.append(self.advance('symbol',{']'}))

                self.writer.write_arithmetic('add')
                self.writer.write_pop('pointer', 1)
                self.writer.write_pop('that', 0)
            elif self.cur_token() == '(':
                self.writer.write_push('pointer', 0)
                elements.append(self.advance('symbol',{'('}))
                elements.append(self.compile_expression_list())
                elements.append(self.advance('symbol',{')'}))

                func_name = '%s.%s' % (self.module_name, name)
                self.writer.write_call(func_name, self.cur_nargs+1)
            elif self.cur_token() == '.':
                elements.append(self.advance('symbol',{'.'}))
                elements.append(self.advance('identifier'))
                is_method = True
                if name[0].islower():
                    module_name = self.symbols.type_of(name)
                    index = self.symbols.index_of(name)
                    kind = self.symbols.kind_of(name)
                    segment = kind2segment[kind]
                    self.writer.write_push(segment, index)
                else:
                    module_name = name
                    is_method = False
                    
                func_name = '%s.%s' % (module_name, elements[-1][1])
                elements.append(self.advance('symbol',{'('}))
                elements.append(self.compile_expression_list())
                elements.append(self.advance('symbol',{')'}))

                nargs = self.cur_nargs
                if is_method:
                    nargs += 1
                self.writer.write_call(func_name, nargs)
            else:
                segment = kind2segment[self.symbols.kind_of(name)]
                index = self.symbols.index_of(name)
                self.writer.write_push(segment, index)
        elif self.cur_token() == '(':
            elements.append(self.advance('symbol',{'('}))
            elements.append(self.compile_expression())
            elements.append(self.advance('symbol',{')'}))
        elif self.cur_token() in {'-','~'}:
            elements.append(self.advance('symbol',{'-','~'}))
            symbol = elements[-1][1]
            elements.append(self.compile_term())
            if symbol == '-':
                self.writer.write_arithmetic('neg')
            else:
                self.writer.write_arithmetic('not')
        else:
            raise NoMatch()
            # raise Exception(self.tokens[self.index-5:self.index+1])

        return ('term', elements)

    def compile_expression_list(self):
        elements = []
        # set up local variable for nargs instead of using self.cur_nargs
        # because inner expression might change self.cur_nargs
        nargs = 0 
        if self.cur_token() != ')':
            elements.append(self.compile_expression())
            nargs += 1
            while self.cur_token() == ',':
                elements.append(self.advance('symbol', {','}))
                elements.append(self.compile_expression())
                nargs += 1
        self.cur_nargs = nargs
        return ('expressionList', elements)
