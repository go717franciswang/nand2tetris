class Parser:
    index = 0

    def __init__(self, tokens):
        self.tokens = tokens

    def parse(self):
        return self.compile_class()

    def advance(self, t, e=None):
        t2, e2 = self.tokens[self.index]
        assert(t == t2)
        assert(e is None or e == e2)
        self.index += 1
        return (t2, e2)

    def compile_class(self):
        elements = []
        elements.append(advance(tokens, 'keyword', 'class'))
        elements.append(advance(tokens, 'identifier'))
        elements.append(advance(tokens, 'symbol'))
        elements.append(('symbol', tokens[index+2]))

    def compile_class_var_dec(self):
        """docstring for compile_class_var_dec"""
        pass

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
