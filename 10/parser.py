class NoMatch(Exception):
    pass

class Parser:
    index = 0

    def __init__(self, tokens):
        self.tokens = tokens

    def parse(self):
        return self.compile_class()

    def advance(self, valid_type, valid_elements=None):
        t, e = self.tokens[self.index]
        if t != valid_type:
            raise NoMatch('Expected type: '+valid_type+', Got type: '+t)
        if valid_elements is not None and e not in valid_elements:
            raise NoMatch('Expected token: '+' | '.join(valid_elements)+', Got: '+e)
        self.index += 1
        return (t, e)

    def compile_class(self):
        elements = []
        elements.append(advance('keyword', {'class'}))
        elements.append(advance('identifier'))
        elements.append(advance('symbol', {'{'}))

        while True:
            try:
                class_var_dec = compile_class_var_dec()
                elements += ('classVarDec', class_var_dec)
            except NoMatch as e:
                break

        while True:
            try:
                subroutine_dec = compile_subroutine()
                elements += ('subroutineDec', subroutine_dec)
            except NoMatch as e:
                break

        elements.append(advance('symbol', {'}'}))
        return ('class', elements)

    def compile_class_var_dec(self):
        elements = []
        elements.append(advance('keyword', {'static','field'}))
        try:
            elements.append(advance('keyword', {'int','char','boolean'}))
        except NoMatch:
            elements.append(advance('identifier'))
        elements.advance('identifier')

        while True:
            try:
                elements.append(advance('symbol', {','}))
                elements.advance('identifier')
            except:
                break
        elements.advance('symbol', {';'})

    def compile_subroutine(self):
        """docstring for compile_subroutine"""
        pass

    def compile_parameter_list(self):
        """docstring for comp"""
        pass

    def compile_var_dec(self):
        """docstring for compile_var_dec"""
        pass

    def compile_statements(self):
        """docstring for compile_statemetns"""
        pass

    def compile_do(self):
        """docstring for compile_do"""
        pass

    def compile_let(self):
        """docstring for compile_let"""
        pass

    def compile_while(self):
        """docstring for compile_while"""
        pass

    def compile_return(self):
        """docstring for compile_return"""
        pass

    def compile_if(self):
        """docstring for compile_if"""
        pass

    def compile_expression(self):
        """docstring for compile_expression"""
        pass

    def compile_term(self):
        """docstring for compile_term"""
        pass

    def compile_expression_list(self):
        """docstring for compile_expression_list"""
        pass
