class NoMatch(Exception):
    pass

operators = {'+','-','*','/','&','|','<','>','='}
keyword_constants = {'true','false','null','this'}

class Parser:
    index = 0

    def __init__(self, tokens):
        self.tokens = tokens

    def parse(self):
        return self.compile_class()

    def advance(self, valid_type, valid_elements=None):
        t, e = self.tokens[self.index]
        if t != valid_type:
            raise NoMatch('Expected type: '+valid_type+', Got type: '+t+' => "'+e+'"')
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
        try:
            elements.append(self.advance('keyword', {'int','char','boolean'}))
        except NoMatch as e:
            elements.append(self.advance('identifier'))
        elements.append(self.advance('identifier'))

        while self.cur_token() == ',':
            elements.append(self.advance('symbol', {','}))
            elements.append(self.advance('identifier'))
        elements.append(self.advance('symbol', {';'}))
        return ('classVarDec', elements)

    def compile_subroutine(self):
        elements = []
        elements.append(self.advance('keyword', {'constructor','function','method'}))
        try:
            elements.append(self.advance('keyword', {'void','int','char','boolean'}))
        except NoMatch as e:
            elements.append(self.advance('identifier'))
        elements.append(self.advance('identifier'))
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
            elements.append(self.advance('identifier'))

            while self.cur_token() == ',':
                elements.append(self.advance('symbol', {','}))
                try:
                    elements.append(self.advance('keyword', {'int','char','boolean'}))
                except NoMatch as e:
                    elements.append(self.advance('identifier'))
                elements.append(self.advance('identifier'))
        return ('parameterList', elements)

    def compile_subroutine_body(self):
        elements = []
        elements.append(self.advance('symbol', {'{'}))
        while self.cur_token() == 'var':
            elements.append(self.compile_var_dec())
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
        elements.append(self.advance('identifier'))
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
        if self.cur_token() == '[':
            elements.append(self.advance('symbol', {'['}))
            elements.append(self.compile_expression())
            elements.append(self.advance('symbol', {']'}))
        elements.append(self.advance('symbol', {'='}))
        elements.append(self.compile_expression())
        elements.append(self.advance('symbol', {';'}))
        return ('letStatement', elements)

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
