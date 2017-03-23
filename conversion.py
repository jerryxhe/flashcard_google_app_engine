import re
import cgi


re_string = re.compile(r'(?P<htmlchars>[<&>])|(?P<space>^[ \t]+)|(?P<lineend>\r\n|\r|\n)|(?P<protocal>(^|\s)((http|ftp)://.*?))(\s|$)', re.S|re.M|re.I)
htmltags = "(%s)" % "|".join(['html', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'span', 'i', 'em', 'b', 'p', 'img', 'dt', 'dd', 'dl', 'ul', 'li', 'a', 'sup', 'sub'])
tag_restore = re.compile("&lt;(?P<tag>%s)(?P<affected>.*?)&lt;/(?P=tag)&gt;" % htmltags, re.S | re.M | re.I)

def plaintext2html(text, tabstop=4):
    def do_sub(m):
        c = m.groupdict()
        if c['htmlchars']:
            return cgi.escape(c['htmlchars'])
        if c['lineend']:
            return '<br>'
        elif c['space']:
            t = m.group().replace('\t', '&nbsp;'*tabstop)
            t = t.replace(' ', '&nbsp;')
            return t
        elif c['space'] == '\t':
            return ' '*tabstop;
        else:
            url = m.group('protocal')
            if url is None:
                return ""
            if url.startswith(' '):
                prefix = ' '
                url = url[1:]
            else:
                prefix = ''
            last = m.groups()[-1]
            if last in ['\n', '\r', '\r\n']:
                last = '<br>'
            return '%s<a href="%s">%s</a>%s' % (prefix, url, url, last)
    firstpass = re.sub(re_string, do_sub, text)
    def do_sub2(m):
        c = m.groupdict()
        return "<%s%s</%s>" % (c['tag'], c['affected'].replace(r'&gt;', r'>'), c['tag'])
    
    return re.sub(tag_restore, do_sub2, firstpass)


def tex2html(texHTML):
    sub = {r'\emph':'em', r'\textit':'i', r'\textbf':'b', r'\section':'h2'}
    re_string = re.compile(r'(?P<control>(\\emph|\\textit|\\textbf|\\section))[{](?P<text>.*?)[}]')
    # making 2 passes takes care of nested \emph{\textbf{}} types
    text1 = re.sub(re_string, lambda m: (r'<%s>' + m.group('text') +r'</%s>') % (sub[m.group('control')], sub[m.group('control')]), texHTML)
    return re.sub(re_string, lambda m: (r'<%s>' + m.group('text') +r'</%s>') % (sub[m.group('control')], sub[m.group('control')]), text1)