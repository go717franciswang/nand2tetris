from lxml import etree

def tree2xml(node):
    t,es = node
    xml = etree.Element(t)
    if isinstance(es, basestring):
        xml.text = ' '+es+' '
    else:
        for e in es:
            xml.append(tree2xml(e))
    return xml

