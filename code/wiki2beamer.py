#!/usr/bin/env python

###############################################################################
# wiki2beamer                                                                 #
#                                                                             #
# (c) 2007-2008 Michael Rentzsch (http://www.repc.de)                         #
# (c) 2009 Michael Rentzsch (http://www.repc.de)                              #
#          Kai Dietrich (mail@cleeus.de)                                      #
#                                                                             #
# Create latex beamer sources for multiple frames from a wiki-like code.      #
# Warning: This is mostly all-in-one-procedure-code -- but it works ;-)       #
###############################################################################
# This program is licensed under the terms of the GPL (see gpl.txt).          #
#                                                                             #
###############################################################################

import sys
import re
import random
import hashlib
import string

VERSIONTAG = "0.7 alpha 2"
__version__= VERSIONTAG
__author__= "Michael Rentzsch, Kai Dietrich"

def mydebug(message):
    """ print debug message to stderr """
    print >>sys.stderr, message

def syntax_error(message, code):
    print >>sys.stderr, 'syntax error: %s' % message
    print >>sys.stderr, '\tcode:\n%s' % code
    sys.exit(-3)

lstbasicstyle=\
r"""{basic}{
    captionpos=t,%
    basicstyle=\footnotesize\ttfamily,%
    numberstyle=\tiny,%
    numbers=left,%
    stepnumber=1,%
    frame=single,%
    showspaces=false,%
    showstringspaces=false,%
    showtabs=false,%
    %
    keywordstyle=\color{blue},%
    identifierstyle=,%
    commentstyle=\color{gray},%
    stringstyle=\color{magenta}%
}"""

autotemplate = [\
    ('documentclass', '{beamer}'),\
    ('usepackage', '{listings}'),\
    ('usepackage', '{color}'),\
    ('usepackage', '{wasysym}'),\
    ('title', '{}'),\
    ('subtitle', '{}'),\
    ('author', '{}'),\
    ('date', '{\\today}'),\
    ('lstdefinestyle', lstbasicstyle),\
    ('titleframe', 'True')\
]

class w2bstate:
    def __init__(self):
        self.frame_opened = False
        self.enum_item_level = ''
        self.frame_header = ''
        self.frame_footer = ''
        self.next_frame_footer = ''
        self.next_frame_header = ''
        self.current_line = 0
        self.last_code_frame = 0
        self.autotemplate_opened = False
        return

    def switch_to_next_frame(self):
        self.frame_header = self.next_frame_header
        self.frame_footer = self.next_frame_footer

def escape_resub(string):
    p = re.compile(r"\\")
    return p.sub(r"\\\\", string)


def transform_itemenums(string, state):
    """handle itemizations/enumerations"""
    preamble = ""   # for enumeration/itemize environment commands

    # handle itemizing/enumerations
    p = re.compile("^([\*\#]+).*$")
    m = p.match(string)
    if (m == None):
        my_enum_item_level = ""
    else:
        my_enum_item_level = m.group(1)

    # trivial: old level = new level
    if (my_enum_item_level == state.enum_item_level):
        pass
    else:
        # find common part
        common = -1 
        while (len(state.enum_item_level) > common + 1) and \
                (len(my_enum_item_level) > common + 1) and \
                (state.enum_item_level[common+1] == my_enum_item_level[common+1]):
            common = common + 1

        # close enum_item_level environments from back to front
        for i in range(len(state.enum_item_level)-1, common, -1):
            if (state.enum_item_level[i] == "*"):
                preamble = preamble + "\\end{itemize}\n"
            elif (state.enum_item_level[i] == "#"):
                preamble = preamble + "\\end{enumerate}\n"
        
        # open my_enum_item_level environments from front to back
        for i in range(common+1, len(my_enum_item_level)):
            if (my_enum_item_level[i] == "*"):
                preamble = preamble + "\\begin{itemize}\n"
            elif (my_enum_item_level[i] == "#"):
                preamble = preamble + "\\begin{enumerate}\n"
    state.enum_item_level = my_enum_item_level
    
    # now, substitute item markers
    p = re.compile("^([\*\#]+)(.*)$")
    _string = p.sub(r"  \\item\2", string)
    string = preamble + _string
 
    return string

def transform_define_foothead(string, state):
    """ header and footer definitions"""
    p = re.compile("^@FRAMEHEADER=(.*)$", re.VERBOSE)
    m = p.match(string)
    if (m != None):
        #print m.group(1)
        state.next_frame_header = m.group(1)
        string = ""
    p = re.compile("^@FRAMEFOOTER=(.*)$", re.VERBOSE)
    m = p.match(string)
    if (m != None):
        #print m.group(1)
        state.next_frame_footer = m.group(1)
        string = ""
    return string

def transform_detect_manual_frameclose(string, state):
    """ detect manual closing of frames """
    p = re.compile(r"\[\s*frame\s*\]>")
    if state.frame_opened:
        if p.match(string) != None:
            state.frame_opened = False
    return string

def get_frame_closing(state):
    return " %s \n \\end{frame}\n" % state.frame_footer

def transform_codeframe(string, state):
    frame_closing = escape_resub(get_frame_closing(state))

    p = re.compile(r"^<\[codeframe\]>")
    if state.frame_opened:
        _string = p.sub("%s\n" % frame_closing, string)
    else:
        _string = p.sub("\n", string)

    if string != _string:
        state.frame_opened=False
        state.switch_to_next_frame()
        state.last_code_frame = state.current_line

    return _string
 
def transform_h4_to_frame(string, state):
    """headings (3) to frames"""
    frame_opening = r"\\begin{frame}\2\n \\frametitle{\1}\n %s \n" % escape_resub(state.next_frame_header)
    frame_closing = escape_resub(get_frame_closing(state))
    
    p = re.compile("^====\s*(.*?)\s*====(.*)", re.VERBOSE)
    if not state.frame_opened:
        _string = p.sub(frame_opening, string)
    else:
        _string = p.sub(frame_closing + frame_opening, string)

    if (string != _string):
        state.frame_opened = True
        state.switch_to_next_frame()

    return _string

def transform_h3_to_subsec(string, state):
    """ headings (2) to subsections """
    frame_closing = escape_resub(get_frame_closing(state))
    subsec_opening = r"\n\\subsection\2{\1}\n\n"

    p = re.compile("^===\s*(.*?)\s*===(.*)", re.VERBOSE)
    if state.frame_opened:
        _string = p.sub(frame_closing + subsec_opening, string)
    else:
        _string = p.sub(subsec_opening, string)
    if (string != _string):
        state.frame_opened = False
    
    return _string

def transform_h2_to_sec(string, state):
    """ headings (1) to sections """
    frame_closing = escape_resub(get_frame_closing(state))
    sec_opening = r"\n\\section\2{\1}\n\n"
    p = re.compile("^==\s*(.*?)\s*==(.*)", re.VERBOSE)
    if state.frame_opened:
        _string = p.sub(frame_closing + sec_opening, string)
    else:
        _string = p.sub(sec_opening, string)
    if (string != _string):
        state.frame_opened = False

    return _string

def transform_replace_headfoot(string, state):
    string = string.replace("<---FRAMEHEADER--->", state.frame_header)
    string = string.replace("<---FRAMEFOOTER--->", state.frame_footer)
    return string

def transform_environments(string):
    """
    latex environments, the users takes full responsibility
    for closing ALL opened environments
    exampe:
    <[block]{block title}
    message
    [block]>
    """
    # -> open
    p = re.compile("^<\[([^{}]*?)\]", re.VERBOSE)
    string = p.sub(r"\\begin{\1}", string)
    # -> close
    p = re.compile("^\[([^{}]*?)\]>", re.VERBOSE)
    string = p.sub(r"\\end{\1}", string)

    return string

def transform_columns(string):
    """ columns """
    p = re.compile("^\[\[\[(.*?)\]\]\]", re.VERBOSE)
    string = p.sub(r"\\column{\1}", string)
    return string

def transform_boldfont(string):
    """ bold font """
    p = re.compile("'''(.*?)'''", re.VERBOSE)
    string = p.sub(r"\\textbf{\1}", string)
    return string

def transform_italicfont(string):
    """ italic font """
    p = re.compile("''(.*?)''", re.VERBOSE)
    string = p.sub(r"\\emph{\1}", string) 
    return string

def transform_typewriterfont(string):
    """ typewriter font """
    p = re.compile("@(.*?)@", re.VERBOSE)
    string = p.sub(r"\\texttt{\1}", string) 
    return string

def transform_alerts(string):
    """ alerts """
    p = re.compile("!(.*?)!", re.VERBOSE)
    string = p.sub(r"\\alert{\1}", string) 
    return string

def transform_colors(string):
    """ colors """
    p = re.compile("_([^_\\\\]*?)_([^_]*?[^_\\\\])_", re.VERBOSE)
    string = p.sub(r"\\textcolor{\1}{\2}", string) 
    return string
   
def transform_footnotes(string):
    """ footnotes """
    p = re.compile("\(\(\((.*?)\)\)\)", re.VERBOSE)
    string = p.sub(r"\\footnote{\1}", string) 
    return string

def transform_graphics(string):
    """ figures/images """
    p = re.compile("\<\<\<(.*?),(.*?)\>\>\>", re.VERBOSE)
    string = p.sub(r"\\includegraphics[\2]{\1}", string) 
    p = re.compile("\<\<\<(.*?)\>\>\>", re.VERBOSE)
    string = p.sub(r"\\includegraphics{\1}", string) 
    return string

def transform_substitutions(string):
    """ substitutions """
    p = re.compile("(\s)-->(\s)", re.VERBOSE)
    string = p.sub(r"\1$\\rightarrow$\2", string) 
    p = re.compile("(\s)<--(\s)", re.VERBOSE)
    string = p.sub(r"\1$\\leftarrow$\2", string) 
    p = re.compile("(\s)==>(\s)", re.VERBOSE)
    string = p.sub(r"\1$\\Rightarrow$\2", string) 
    p = re.compile("(\s)<==(\s)", re.VERBOSE)
    string = p.sub(r"\1$\\Leftarrow$\2", string) 
    p = re.compile("(\s):-\)(\s)", re.VERBOSE)
    string = p.sub(r"\1\\smiley\2", string) 
    p = re.compile("(\s):-\((\s)", re.VERBOSE)
    string = p.sub(r"\1\\frownie\2", string)
    return string


def transform(string, state):
    """ convert/transform one line in context of state"""

    string = transform_itemenums(string, state)
    string = transform_define_foothead(string, state)
    string = transform_detect_manual_frameclose(string, state)
    string = transform_codeframe(string, state)
    string = transform_h4_to_frame(string, state)
    string = transform_h3_to_subsec(string, state)
    string = transform_h2_to_sec(string, state)
    string = transform_replace_headfoot(string, state)
    
    string = transform_environments(string)
    string = transform_columns(string)
    string = transform_boldfont(string)
    string = transform_italicfont(string)
    string = transform_typewriterfont(string)
    string = transform_alerts(string)
    string = transform_colors(string)
    string = transform_graphics(string)
    string = transform_substitutions(string)

    return string

def expand_code_make_defverb(content, name):
    return "\\defverbatim[colored]\\%s{\n%s\n}" % (name, content)

def expand_code_make_lstlisting(content, options):
    return "\\begin{lstlisting}%s%s\\end{lstlisting}" % (options, content)

def expand_code_search_escape_sequences(code):
    open = 'khuhusi_foobar_duaijd212'
    close = 'aisdfzgzu_foobar_jjj812'
    while code.find(open) != -1 or code.find(close) != -1:
        open.append(chr(random.randint(48,57)))
        close.append(chr(random.randint(48,57)))

    return (open,close)

def expand_code_tokenize_anims(code):
    #escape
    (esc_open, esc_close) = expand_code_search_escape_sequences(code)
    code = code.replace('\\[', esc_open)
    code = code.replace('\\]', esc_close)

    p = re.compile(r'\[\[(?:.|\s)*?\]\]|\[(?:.|\s)*?\]')
    non_anim = p.split(code)
    anim = p.findall(code)
    
    #unescape
    anim = map(lambda s: s.replace(esc_open, '\\[').replace(esc_close, '\\]'), anim)
    non_anim = map(lambda s: s.replace(esc_open, '[').replace(esc_close, ']'), non_anim)

    return (anim, non_anim)

def expand_code_parse_overlayspec(overlayspec):
    overlays = []

    groups = overlayspec.split(',')
    for group in groups:
        group = group.strip()
        if group.find('-')!=-1:
            nums = group.split('-')
            if len(nums)<2:
                syntax_error('overlay specs must be of the form <(%d-%d)|(%d), ...>', overlayspec)
            else:
                try:
                    start = int(nums[0])
                    stop = int(nums[1])
                except ValueError:
                    syntax_error('not an int, overlay specs must be of the form <(%d-%d)|(%d), ...>', overlayspec)

                overlays.extend(range(start,stop+1))
        else:
            try:
                num = int(group)
            except ValueError:
                syntax_error('not an int, overlay specs must be of the form <(%d-%d)|(%d), ...>', overlayspec)
            overlays.append(num)
    
    #make unique
    overlays = list(set(overlays))
    return overlays

def expand_code_parse_simpleanimspec(animspec):
    #escape
    (esc_open, esc_close) = expand_code_search_escape_sequences(animspec)
    animspec = animspec.replace('\\[', esc_open)
    animspec = animspec.replace('\\]', esc_close)

    p = re.compile(r'^\[<([0-9,\-]+)>((?:.|\s)*)\]$')
    m = p.match(animspec)
    if m != None:
        overlays = expand_code_parse_overlayspec(m.group(1))
        code = m.group(2)
    else:
        syntax_error('specification does not match [<%d>%s]', animspec)

    #unescape code
    code = code.replace(esc_open, '[').replace(esc_close, ']')
    
    return [(overlay, code) for overlay in overlays]


def expand_code_parse_animspec(animspec):
    if len(animspec)<4 or not animspec.startswith('[['):
        return ('simple', expand_code_parse_simpleanimspec(animspec))
    
    #escape
    (esc_open, esc_close) = expand_code_search_escape_sequences(animspec)
    animspec = animspec.replace('\\[', esc_open)
    animspec = animspec.replace('\\]', esc_close)
    
    p = re.compile(r'\[|\]\[|\]')
    simple_specs = map(lambda s: '[%s]'%s, filter(lambda s: len(s.strip())>0, p.split(animspec)))

    #unescape
    simple_specs = map(lambda s: s.replace(esc_open, '\\[').replace(esc_close, '\\]'), simple_specs)
    parsed_simple_specs = map(expand_code_parse_simpleanimspec, simple_specs)
    #print parsed_simple_specs
    unified_pss = []
    for pss in parsed_simple_specs:
        unified_pss.extend(pss)
    #print unified_pss
    return ('double', unified_pss)
    

def expand_code_getmaxoverlay(parsed_anims):
    max_overlay = 0
    for anim in parsed_anims:
        for spec in anim:
            if spec[0] > max_overlay:
                max_overlay = spec[0]
    return max_overlay

def expand_code_getminoverlay(parsed_anims):
    min_overlay = sys.maxint
    for anim in parsed_anims:
        for spec in anim:
            if spec[0] < min_overlay:
                min_overlay = spec[0]
    if min_overlay == sys.maxint:
        min_overlay = 0
    return min_overlay


def expand_code_genanims(parsed_animspec, minoverlay, maxoverlay, type):
    #get maximum length of code
    maxlen=0
    if type=='double':
        for simple_animspec in parsed_animspec:
            if maxlen < len(simple_animspec[1]):
                maxlen = len(simple_animspec[1])
    
    out = []
    fill = ''.join([' ' for i in xrange(0, maxlen)])
    for x in xrange(minoverlay,maxoverlay+1):
        out.append(fill[:])

    for simple_animspec in parsed_animspec:
        out[simple_animspec[0]-minoverlay] = simple_animspec[1]

    return out

def expand_code_getname(code):
    asciihextable = string.maketrans('0123456789abcdef',\
                                     'abcdefghijklmnop')
    d = hashlib.md5(code).hexdigest().translate(asciihextable)
    return d

def expand_code_makeoverprint(names, minoverlay):
    out = ['\\begin{overprint}\n']
    for (index, name) in enumerate(names):
        out.append('  \\onslide<%d>\\%s\n' % (index+minoverlay, name))
    out.append('\\end{overprint}\n')

    return ''.join(out)

def expand_code_segment(result, codebuffer, state):
    #treat first line as params for lstlistings
    lstparams = codebuffer[0]
    codebuffer[0] = ''
 
    #join lines into one string
    code = ''.join(codebuffer)
    #print code

    #tokenize code into anim and non_anim parts
    (anim, non_anim) = expand_code_tokenize_anims(code)
    #print anim
    #print non_anim
    if len(anim)>0:
        #generate multiple versions of the anim parts
        parsed_anims = map(expand_code_parse_animspec, anim)
        #print parsed_anims
        max_overlay = expand_code_getmaxoverlay(map(lambda x: x[1], parsed_anims))
        #if there is unanimated code, use 0 as the starting overlay
        if len(non_anim)>0:
            min_overlay = 1
        else:
            min_overlay = expand_code_getminoverlay(map(lambda x: x[1], parsed_anims))
        #print min_overlay
        #print max_overlay
        gen_anims = map(lambda x: expand_code_genanims(x[1], min_overlay, max_overlay, x[0]), parsed_anims)
        #print gen_anims
        anim_map = {}
        for i in xrange(0,max_overlay-min_overlay+1):
            anim_map[i+min_overlay] = map(lambda x: x[i], gen_anims)
        #print anim_map
    
        defverbs = {}
        names = []
        for overlay in sorted(anim_map.keys()):
            #combine non_anim and anim parts
            anim_map[overlay].append('')
            zipped = zip(non_anim, anim_map[overlay])
            mapped = map(lambda x: x[0] + x[1], zipped)
            code = ''.join(mapped)
            name = expand_code_getname(code)
            names.append(name)
            #generate code for lstlistings
            defverbs[name]=expand_code_make_defverb(expand_code_make_lstlisting(code, lstparams), name)
        
        #insert the defverb block into result afte the last code-frame marker
        result[state.last_code_frame] = result[state.last_code_frame] + '\n'.join(defverbs.values()) + '\n'

        #append overprint area to result
        overprint = expand_code_makeoverprint(names, min_overlay)
        result.append(overprint)
    else:
        #we have no animations and can just put the defverbatim in
        #remove escapings
        code = code.replace('\\[', '[').replace('\\]', ']')
        name = expand_code_getname(code)
        defverb = expand_code_make_defverb(expand_code_make_lstlisting(code, lstparams), name)
        result[state.last_code_frame] = result[state.last_code_frame] + '\n' + defverb
        result.append('\n\\%s\n' % name)

    #print '----'
    return

def get_autotemplate_closing(state):
    if state.autotemplate_opened:
        return '\n\end{document}\n'
    else:
        return ''
def parse_bool(string):
    boolean = False

    if string == 'True' or string == 'true' or string == '1':
        boolean = True
    elif string == 'False' or string == 'false' or string =='0':
        boolean = False
    else:
        syntax_error('Boolean expected (True/true/1 or False/false/0)', string)

    return boolean

def parse_autotemplate(autotemplatebuffer):
    """
    @param autotemplatebuffer (list)
        a list of lines found in the autotemplate section
    @return (list)
        a list of tuples of the form (string, string) with \command.parameters pairs
    """
    autotemplate = []

    for line in autotemplatebuffer:
        if len(line.lstrip())==0: #ignore empty lines
            continue
        if len(line.lstrip())>0 and line.lstrip().startswith('%'): #ignore lines starting with % as comments
            continue

        tokens = line.split('=', 1)
        if len(tokens)<2:
            syntax_error('lines in the autotemplate section have to be of the form key=value', line)

        autotemplate.append((tokens[0], tokens[1]))

    return autotemplate

def parse_usepackage(usepackage):
    """
    @param usepackage (str)
        the unparsed usepackage string in the form [options]{name}
    @return (tuple)
        (name(str), options(str))
    """
    
    p = re.compile(r'^\s*(\[.*\])?\s*\{(.*)\}\s*$')
    m = p.match(usepackage)
    g = m.groups()
    if len(g)<2 or len(g)>2:
        syntax_error('usepackage specifications have to be of the form [%s]{%s}', usepackage)
    elif g[1]==None and g[1].strip()!='':
        syntax_error('usepackage specifications have to be of the form [%s]{%s}', usepackage)
    else:
        options = g[0]
        name = g[1].strip()
        return (name, options)


def unify_autotemplates(autotemplates):
    usepackages = {} #packagename : options
    documentclass = ''
    titleframe = False

    merged = []
    for template in autotemplates:
        for command in template:
            if command[0] == 'usepackage':
                (name, options) = parse_usepackage(command[1])
                usepackages[name] = options
            elif command[0] == 'titleframe':
                titleframe = command[1]
            elif command[0] == 'documentclass':
                documentclass = command[1]
            else:
                merged.append(command)
    
    autotemplate = []
    autotemplate.append(('documentclass', documentclass))
    for (name, options) in usepackages.items():
        if options != None and options.strip() != '':
            string = '%s{%s}' % (options, name)
        else:
            string = '{%s}' % name
        autotemplate.append(('usepackage', string))
    autotemplate.append(('titleframe', titleframe))

    autotemplate.extend(merged)

    return autotemplate

def expand_autotemplate_gen_opening(autotemplate):
    """
    @param autotemplate (list)
        the specification of the autotemplate in the form of a list of tuples
    @return (string)
        the string the with generated latex code
    """
    titleframe = False
    out = []
    for item in autotemplate:
        if item[0]!='titleframe':
            out.append('\\%s%s' % item)
        else:
            titleframe = parse_bool(item[1])

    out.append('\n\\begin{document}\n')
    if titleframe:
        out.append('\n\\frame{\\titlepage}\n')

    return '\n'.join(out)


def expand_autotemplate_opening(result, templatebuffer, state):
    my_autotemplate = parse_autotemplate(templatebuffer)
    the_autotemplate = unify_autotemplates([autotemplate, my_autotemplate])

    opening = expand_autotemplate_gen_opening(the_autotemplate)

    result.append(opening)
    state.autotemplate_opened = True
    return

def expand_autotemplate_closing(result, state):
    closing = get_autotemplate_closing(state)
    result.append(closing)
    state.autotemplate_opened=False
    return

def get_autotemplatemode(line, autotemplatemode):
    autotemplatestart = re.compile(r'^<\[\s*autotemplate\s*\]')
    autotemplateend = re.compile(r'^\[\s*autotemplate\s*\]>')
    if not autotemplatemode and autotemplatestart.match(line)!=None:
        line = autotemplatestart.sub('', line)
        return (line, True)
    elif autotemplatemode and autotemplateend.match(line)!=None:
        line = autotemplateend.sub('', line)
        return (line, False)
    else:
        return (line, autotemplatemode)

def get_nowikimode(line, nowikimode):
    nowikistartre = re.compile(r'^<\[\s*nowiki\s*\]')
    nowikiendre = re.compile(r'^\[\s*nowiki\s*\]>')
    
    if not nowikimode and nowikistartre.match(line)!=None:
        line = nowikistartre.sub('', line)
        return (line, True)
    elif nowikimode and nowikiendre.match(line)!=None:
        line = nowikiendre.sub('', line)
        return (line, False)
    else:
        return (line, nowikimode)

def get_codemode(line, codemode):
    codestartre = re.compile(r'^<\[\s*code\s*\]')
    codeendre = re.compile(r'^\[\s*code\s*\]>')

    if not codemode and codestartre.match(line)!=None:
        line = codestartre.sub('', line)
        return (line, True)
    elif codemode and codeendre.match(line)!=None:
        line = codeendre.sub('', line)
        return (line, False)
    else:
        return (line, codemode)

def joinLines(lines):
    """ join lines ending with unescaped percent signs, unless inside codemode or nowiki mode """
    nowikimode = False
    codemode = False
    r = []  # result array
    s = ''  # new line
    for _l in lines:
        (_,nowikimode) = get_nowikimode(_l, nowikimode)
        if not nowikimode:
            (_,codemode) = get_codemode(_l, codemode)

        if not codemode:
            l = _l.rstrip()
        else:
            l = _l

        if not (nowikimode or codemode) and (len(l) > 1) and (l[-1] == "%") and (l[-2] != "\\"):
            s = s + l[:-1]
        elif not (nowikimode or codemode) and (len(l) == 1) and (l[-1] == "%"):
            s = s + l[:-1]
        else:
            s = s + l
            r.append(s)
            s = ''

    return r

def read_file_to_lines(filename):
    """ read file """
    try:
        f = open(filename, "r")
        lines = joinLines(f.readlines())
        f.close()
    except:
        print >>sys.stdout, "Cannot read file: " + filename
        sys.exit(-2)

    return lines

   

def convert2beamer(lines):
    """ convert to LaTeX """
    state = w2bstate()
    result = []
    codebuffer = []
    autotemplatebuffer = []
    
    nowikimode = False
    codemode = False
    autotemplatemode = False
    for line in lines:
        (line, nowikimode) = get_nowikimode(line, nowikimode)
        if nowikimode:
            result.append(line)
        else:
            (line, _codemode) = get_codemode(line, codemode)
            if _codemode and not codemode: #code mode was turned on
                codebuffer = []
            elif not _codemode and codemode: #code mode was turned off
                expand_code_segment(result, codebuffer, state)
            codemode = _codemode

            if codemode:
                codebuffer.append(line)
            else:
                (line, _autotemplatemode) = get_autotemplatemode(line, autotemplatemode)
                if _autotemplatemode and not autotemplatemode: #autotemplate mode was turned on
                    autotemplatebuffer = []
                elif not _autotemplatemode and autotemplatemode: #autotemplate mode was turned off
                    expand_autotemplate_opening(result, autotemplatebuffer, state)
                autotemplatemode = _autotemplatemode
                
                if autotemplatemode:
                    autotemplatebuffer.append(line)
                else:
                    state.current_line = len(result)
                    result.append(transform(line, state))

    result.append(transform("", state))   # close open environments

    if state.frame_opened:
        result.append(get_frame_closing(state))
    expand_autotemplate_closing(result, state)
   
    return result

def print_result(lines):
    """ print result to stdout """
    for l in lines:
        print >>sys.stdout, l
    return

def main(argv):
    """ check parameters, start file processing """
    try:
        filename = argv[1]
    except IndexError:
        print >>sys.stderr, "usage: wiki2beamer.py input.txt > output.tex"
        sys.exit(-1)

    if filename == '--version':
        print >>sys.stdout, "wiki2beamer (http://wiki2beamer.sf.net), version " + VERSIONTAG
        sys.exit(0)

    lines = read_file_to_lines(filename)
    lines = convert2beamer(lines)
    print_result(lines)

    
if (__name__ == "__main__"):
    main(sys.argv)
