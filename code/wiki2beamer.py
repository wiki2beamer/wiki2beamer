#!/usr/bin/env python

###############################################################################
# Wiki2Beamer                 Michael Rentzsch (http://www.repc.de)           #
#                                                                             #
# Create latex beamer sources for multiple frames from a wiki-like code.      #
# Warning: This is mostly all-in-one-procedure-code -- but it works ;-)       #
###############################################################################
# This program is licensed under the terms of the GPL (see gpl.txt).          #
#                                                                             #
# Thanks to Kai Dietrich <mail@cleeus.de> for providing his                   #
# frame-close-detection patch.                                                #
###############################################################################

import sys, re

VERSIONTAG = "0.6"


def mydebug(message):
    """ print debug message to stderr """
    print >>sys.stderr, message


def transform(string):
    """ convert/transform one line """
    global frame_opened, enum_item_level    # nasty thing to do
    global frame_header, frame_footer, next_frame_footer

    preamble = ""   # for enumeration/itemize environment commands

    # handle itemizing/enumerations
    p = re.compile("^([\*\#]+).*$")
    m = p.match(string)
    if (m == None):
        my_enum_item_level = ""
    else:
        my_enum_item_level = m.group(1)

    # trivial: old level = new level
    if (my_enum_item_level == enum_item_level):
        pass
    else:
        # find common part
        common = -1 
        while (len(enum_item_level) > common + 1) and \
                (len(my_enum_item_level) > common + 1) and \
                (enum_item_level[common+1] == my_enum_item_level[common+1]):
            common = common + 1

        # close enum_item_level environments from back to front
        for i in range(len(enum_item_level)-1, common, -1):
            if (enum_item_level[i] == "*"):
                preamble = preamble + "\\end{itemize}\n"
            elif (enum_item_level[i] == "#"):
                preamble = preamble + "\\end{enumerate}\n"
        
        # open my_enum_item_level environments from front to back
        for i in range(common+1, len(my_enum_item_level)):
            if (my_enum_item_level[i] == "*"):
                preamble = preamble + "\\begin{itemize}\n"
            elif (my_enum_item_level[i] == "#"):
                preamble = preamble + "\\begin{enumerate}\n"
    enum_item_level = my_enum_item_level


    # now, substitute item markers
    p = re.compile("^([\*\#]+)(.*)$")
    _string = p.sub(r"  \\item\2", string)
    string = _string

    # header and footer definitions
    p = re.compile("^@FRAMEHEADER=(.*)$", re.VERBOSE)
    m = p.match(string)
    if (m != None):
        #print m.group(1)
        frame_header = m.group(1)
        string = ""
    p = re.compile("^@FRAMEFOOTER=(.*)$", re.VERBOSE)
    m = p.match(string)
    if (m != None):
        #print m.group(1)
        next_frame_footer = m.group(1)
        string = ""


    # detect manual closing of frames
    p = re.compile(r"(?:^\s*\\end{\s*frame\s*})|(?:^\[\s*frame\s*\]>)")
    if (frame_opened == 1):
        if (len(p.findall(string)) > 0):
            frame_opened = 0

    # headings (3) to frames
    p = re.compile("^====\s*(.*?)\s*====(.*)", re.VERBOSE)
    if (frame_opened == 0):
        _string = p.sub(r"\\begin{frame}\2\n \\frametitle{\1}\n <---FRAMEHEADER---> \n", string)
    else:
        _string = p.sub(r" <---FRAMEFOOTER---> \n \\end{frame}\n\n\\begin{frame}\2\n \\frametitle{\1}\n <---FRAMEHEADER---> \n", string)
    if (string != _string):
        frame_opened = 1


    # headings (2) to subsections
    string = _string
    p = re.compile("^===\s*(.*?)\s*===(.*)", re.VERBOSE)
    if (frame_opened == 1):
        _string = p.sub(r" <---FRAMEFOOTER---> \n \\end{frame}\n\\subsection\2{\1}\n\n", string)
    else:
        _string = p.sub(r"\n\\subsection\2{\1}\n\n", string)
    if (string != _string):
        frame_opened = 0

    # headings (1) to sections
    string = _string
    p = re.compile("^==\s*(.*?)\s*==(.*)", re.VERBOSE)
    if (frame_opened == 1):
        _string = p.sub(r" <---FRAMEFOOTER---> \n \\end{frame}\n\n\\section\2{\1}\n\n", string)
    else:
        _string = p.sub(r"\n\n\\section\2{\1}\n\n", string)
    if (string != _string):
        frame_opened = 0


    _string = _string.replace("<---FRAMEHEADER--->", frame_header)
    _string = _string.replace("<---FRAMEFOOTER--->", frame_footer)


    if (_string.find("\\end{frame}") != -1):
        frame_footer = next_frame_footer

    # latex environments, the users takes full responsibility
    # for closing ALL opened environments
    # exampe:
    # <[block]{block title}
    # message
    # [block]>

    # -> open
    p = re.compile("^<\[([^{}]*?)\]", re.VERBOSE)
    _string = p.sub(r"\\begin{\1}", _string)
    # -> close
    p = re.compile("^\[([^{}]*?)\]>", re.VERBOSE)
    _string = p.sub(r"\\end{\1}", _string)

    # columns
    p = re.compile("^\[\[\[(.*?)\]\]\]", re.VERBOSE)
    _string = p.sub(r"\\column{\1}", _string)

    # bold font
    p = re.compile("'''(.*?)'''", re.VERBOSE)
    _string = p.sub(r"\\textbf{\1}", _string) 

    # italic font
    p = re.compile("''(.*?)''", re.VERBOSE)
    _string = p.sub(r"\\emph{\1}", _string) 

    # typewriter font
    p = re.compile("@(.*?)@", re.VERBOSE)
    _string = p.sub(r"\\texttt{\1}", _string) 

    # alerts
    p = re.compile("!(.*?)!", re.VERBOSE)
    _string = p.sub(r"\\alert{\1}", _string) 

    # colors
    p = re.compile("_([^_\\\\]*?)_([^_]*?[^_\\\\])_", re.VERBOSE)
    _string = p.sub(r"\\textcolor{\1}{\2}", _string) 

    # footnotes
    p = re.compile("\(\(\((.*?)\)\)\)", re.VERBOSE)
    _string = p.sub(r"\\footnote{\1}", _string) 

    # figures/images
    p = re.compile("\<\<\<(.*?),(.*?)\>\>\>", re.VERBOSE)
    _string = p.sub(r"\\includegraphics[\2]{\1}", _string) 
    p = re.compile("\<\<\<(.*?)\>\>\>", re.VERBOSE)
    _string = p.sub(r"\\includegraphics{\1}", _string) 


    # substitutions
    p = re.compile("(\s)-->(\s)", re.VERBOSE)
    _string = p.sub(r"\1$\\rightarrow$\2", _string) 
    p = re.compile("(\s)<--(\s)", re.VERBOSE)
    _string = p.sub(r"\1$\\leftarrow$\2", _string) 
    p = re.compile("(\s)==>(\s)", re.VERBOSE)
    _string = p.sub(r"\1$\\Rightarrow$\2", _string) 
    p = re.compile("(\s)<==(\s)", re.VERBOSE)
    _string = p.sub(r"\1$\\Leftarrow$\2", _string) 
    p = re.compile("(\s):-\)(\s)", re.VERBOSE)
    _string = p.sub(r"\1\\smiley\2", _string) 
    p = re.compile("(\s):-\((\s)", re.VERBOSE)
    _string = p.sub(r"\1\\frownie\2", _string)


  
    # to be continued ...

   
    return preamble + _string


def joinLines(lines):
    """ join lines ending with unescaped percent signs """
    r = []  # result array
    s = ''  # new line
    for _l in lines:
        l = _l.rstrip()
        if (len(l) > 1) and (l[-1] == "%") and (l[-2] != "\\"):
            s = s + l[:-1]
        elif (len(l) == 1) and (l[-1] == "%"):
            s = s + l[:-1]
        else:
            s = s + l
            r.append(s)
            s = ''

    return r


def convert2beamer(filename):
    """ read file, convert to LaTeX, print result """
    global frame_opened, enum_item_level    # nasty thing to do
    global frame_header, frame_footer, next_frame_footer

    frame_opened = 0
    enum_item_level = ""
    result = []

    try:
        f = open(filename, "r")
        lines = joinLines(f.readlines())
        f.close()
    except:
        print >>sys.stdout, "Cannot read file: " + filename
        sys.exit(-2)

    frame_header = ""
    frame_footer = ""
    next_frame_footer = ""
       
    for line in lines:
        result.append(transform(line))
    result.append(transform(""))   # close open environments

    if (frame_opened == 1):
        _string = "<---FRAMEFOOTER---> \n \\end{frame}\n"
        _string = _string.replace("<---FRAMEFOOTER--->", frame_footer)
        result.append(_string)

    for r in result:
        print >>sys.stdout, r

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

    convert2beamer(filename)
    

if (__name__ == "__main__"):
    main(sys.argv)
