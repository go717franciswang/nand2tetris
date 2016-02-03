import re

lexical_elements = [
        ('comment', re.compile(r'//.*$|/\*[\s\S]*?\*/', re.MULTILINE)),
        ('keyword', re.compile(r'(class|constructor|function|method|field|static|var|int|char|boolean|void|true|false|null|this|let|do|if|else|while|return)\b')),
        ('symbol', re.compile(r'[{}()[\].,;+\-*/&|<>=~]')),
        ('integerConstant', re.compile(r'\d{1,5}')),
        ('stringConstant', re.compile(r'"[^"\n]*"')),
        ('identifier', re.compile(r'[a-zA-Z_][a-zA-Z_0-9]*'))]
xml_special_char = {
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        '&': '&amp;'
        }

def tokenize(filein):
    tokens = []
    with open(filein) as f:
        content = f.read()
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

        fileout = filein.split('.')[0] + '.T.xml'
        fout = open(fileout, 'w')
        fout.write('<tokens>\n')
        for t, e in tokens:
            fout.write('<%s> %s </%s>\n' % (t, xml_special_char.get(e, e), t))
        fout.write('</tokens>\n')
    return tokens

