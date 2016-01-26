import re

lexical_elements = [
        ('comment', re.compile('//.*$|/\*.*\*/', re.MULTILINE)),
        ('keyword', re.compile('class|constructor|function|method|field|static|var|int|char|boolean|void|true|false|null|this|let|do|if|else|while|return')),
        ('symbol', re.compile('[{}()[\].,;+\-*/&|<>=~]')),
        ('integerConstant', re.compile('\d{1,5}')),
        ('stringConstant', re.compile('"[^"\n]*"')),
        ('identifier', re.compile('[a-zA-Z_][a-zA-Z_0-9]*'))]

def tokenize(filein):
    with open(filein) as f:
        content = f.read()
        tokens = []
        while content != '':
            content = content.strip()

            for element, regex in lexical_elements:
                m = regex.match(content)
                if m:
                    match = m.group()
                    content = content[len(match):]

                    if element == 'comment':
                        pass
                    elif element == 'stringConstant':
                        tokens.append((element, match[1:-1]))
                    else:
                        tokens.append((element, match))
                    break

        print tokens



