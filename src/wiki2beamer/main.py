#!/usr/bin/env python3

# wiki2beamer
#
# (c) 2007-2008 Michael Rentzsch (http://www.repc.de)
# (c) 2009-2011 Michael Rentzsch (http://www.repc.de)
#               Kai Dietrich (mail@cleeus.de)
# (c) 2018      Valentin Haenel (valentin@haenel.co)
#
# Create latex beamer sources for multiple frames from a wiki-like code.
#
#
#     This file is part of wiki2beamer.
# wiki2beamer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# wiki2beamer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with wiki2beamer.  If not, see <http://www.gnu.org/licenses/>.
#
# Additional commits by:
#     Valentin Haenel <valentin.haenel@gmx.de>
#     Julius Plenz <julius@plenz.com>


import codecs
import hashlib
import optparse
import os
import random
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Match, Optional, Pattern, Tuple, Type, TypeVar

VERSIONTAG = "0.10.0"
__version__ = VERSIONTAG
__author__ = "Michael Rentzsch, Kai Dietrich and others"


# python 2.4 compatability
def md5hex(string: str) -> str:
    return hashlib.md5(string.encode("utf-8")).hexdigest()  # noqa: S324


_redirected_stdout: Optional[Any] = None
_redirected_stderr: Optional[Any] = None


def pprint(string: str, file: Any = sys.stdout, eol: bool = True) -> None:  # noqa: FBT001, FBT002 # TODO: Fix this
    """portable version of print which directly writes into the given stream"""
    if file == sys.stdout and _redirected_stdout is not None:
        file = _redirected_stdout
    if file == sys.stderr and _redirected_stderr is not None:
        file = _redirected_stderr

    if file in {sys.stderr, sys.stdout}:
        file.write(string)
    else:
        file.write(string.encode("utf-8"))

    if eol:
        file.write(os.linesep)
    file.flush()


def mydebug(message: str) -> None:
    """print debug message to stderr"""
    pprint(message, file=sys.stderr)


def syntax_error(message: str, code: str) -> None:
    pprint(f"syntax error: {message}", file=sys.stderr)
    pprint(f"\tcode:\n{code}", file=sys.stderr)
    sys.exit(-3)


class IncludeLoopException(Exception):
    pass


lstbasicstyle: str = r"""{basic}{
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

autotemplate: List[Tuple[str, str]] = [
    ("documentclass", "{beamer}"),
    ("usepackage", "{listings}"),
    ("usepackage", "{wasysym}"),
    ("usepackage", "{graphicx}"),
    ("date", "{\\today}"),
    ("lstdefinestyle", lstbasicstyle),
    ("titleframe", "True"),
]

nowikistartre: Pattern[str] = re.compile(r"^<\[\s*nowiki\s*\]")
nowikiendre: Pattern[str] = re.compile(r"^\[\s*nowiki\s*\]>")
codestartre: Pattern[str] = re.compile(r"^<\[\s*code\s*\]")
codeendre: Pattern[str] = re.compile(r"^\[\s*code\s*\]>")

# lazy initialisation cache for file content
_file_cache: Dict[str, List[str]] = {}


def add_lines_to_cache(filename: str, lines: List[str]) -> None:
    if filename not in _file_cache:
        _file_cache[filename] = lines


def get_nowikimode(line: str, nowikimode: bool) -> Tuple[str, bool]:  # noqa: FBT001 # TODO: Fix this
    if not nowikimode and nowikistartre.match(line) is not None:
        line = nowikistartre.sub("", line)
        return (line, True)
    if nowikimode and nowikiendre.match(line) is not None:
        line = nowikiendre.sub("", line)
        return (line, False)
    return (line, nowikimode)


def get_codemode(line: str, codemode: bool) -> Tuple[str, bool]:  # noqa: FBT001 # TODO: Fix this
    if not codemode and codestartre.match(line) is not None:
        line = codestartre.sub("", line)
        return (line, True)
    if codemode and codeendre.match(line) is not None:
        line = codeendre.sub("", line)
        return (line, False)
    return (line, codemode)


def joinLines(lines: List[str]) -> List[str]:  # noqa: N802 # TODO: Fix this
    """join lines ending with unescaped percent signs, unless inside codemode or nowiki mode"""
    nowikimode = False
    codemode = False
    r = []  # result array
    s = ""  # new line
    for _l in lines:
        (_, nowikimode) = get_nowikimode(_l, nowikimode)
        if not nowikimode:
            (_, codemode) = get_codemode(_l, codemode)

        l = _l.rstrip() if not codemode else _l

        if (
            not (nowikimode or codemode) and (len(l) > 1) and (l[-1] == "%") and (l[-2] != "\\")
        ) or (not (nowikimode or codemode) and (len(l) == 1) and (l[-1] == "%")):
            s += l[:-1]
        else:
            s += l
            r.append(s)
            s = ""

    return r


def read_file_to_lines(filename: str) -> List[str]:
    """read file"""
    try:
        f = codecs.open(filename, "r", encoding="UTF-8")
        lines = joinLines(f.readlines())
        f.close()
    except Exception:  # noqa: BLE001 # TODO: Fix this
        pprint(f"Cannot read file: {filename}", sys.stderr)
        sys.exit(-2)

    return lines


def get_lines_from_cache(filename: str) -> List[str]:
    if filename in _file_cache:
        return _file_cache[filename]
    lines = read_file_to_lines(filename)
    _file_cache[filename] = lines
    return lines


def clear_file_cache() -> None:
    _file_cache.clear()


try:
    from collections import OrderedDict

    maybe_odict: Type[Dict[str, str]] = OrderedDict
except ImportError:
    maybe_odict = dict


class w2bstate:  # noqa: N801 # TODO: Fix this
    def __init__(self) -> None:
        self.frame_opened = False
        self.enum_item_level = ""
        self.frame_header = ""
        self.frame_footer = ""
        self.next_frame_footer = ""
        self.next_frame_header = ""
        self.current_line = 0
        self.autotemplate_opened = False
        self.defverbs: Dict[str, str] = maybe_odict()
        self.code_pos = 0
        self.active_envs: Dict[str, int] = dict()

    def switch_to_next_frame(self) -> None:
        self.frame_header = self.next_frame_header
        self.frame_footer = self.next_frame_footer


def escape_resub(string: str) -> str:
    p = re.compile(r"\\")
    return p.sub(r"\\\\", string)


def transform_itemenums(string: str, state: w2bstate) -> str:
    """handle itemizations/enumerations"""
    preamble = ""  # for enumeration/itemize environment commands

    # handle itemizing/enumerations
    p = re.compile(r"^([\*\#]+).*$")
    m = p.match(string)
    my_enum_item_level = "" if m is None else m.group(1)

    # trivial: old level = new level
    if my_enum_item_level == state.enum_item_level:
        pass
    else:
        # find common part
        common = -1
        while (
            (len(state.enum_item_level) > common + 1)
            and (len(my_enum_item_level) > common + 1)
            and (state.enum_item_level[common + 1] == my_enum_item_level[common + 1])
        ):
            common += 1

        # close enum_item_level environments from back to front
        for i in range(len(state.enum_item_level) - 1, common, -1):
            if state.enum_item_level[i] == "*":
                preamble += "\\end{itemize}\n"
            elif state.enum_item_level[i] == "#":
                preamble += "\\end{enumerate}\n"

        # open my_enum_item_level environments from front to back
        for i in range(common + 1, len(my_enum_item_level)):
            if my_enum_item_level[i] == "*":
                preamble += "\\begin{itemize}\n"
            elif my_enum_item_level[i] == "#":
                preamble += "\\begin{enumerate}\n"
    state.enum_item_level = my_enum_item_level

    # now, substitute item markers
    p = re.compile(r"^([\*\#]+)((?:\[[^\]*]\])?)\s*(.*)$")
    _string = p.sub(r"  \\item\2 \3", string)
    return preamble + _string


def transform_define_foothead(string: str, state: w2bstate) -> str:
    """header and footer definitions"""
    p = re.compile("^@FRAMEHEADER=(.*)$", re.VERBOSE)
    m = p.match(string)
    if m is not None:
        state.next_frame_header = m.group(1)
        string = ""
    p = re.compile("^@FRAMEFOOTER=(.*)$", re.VERBOSE)
    m = p.match(string)
    if m is not None:
        state.next_frame_footer = m.group(1)
        string = ""
    return string


def transform_detect_manual_frameclose(string: str, state: w2bstate) -> str:
    """detect manual closing of frames"""
    p = re.compile(r"\[\s*frame\s*\]>")
    if state.frame_opened and p.match(string) is not None:
        state.frame_opened = False
    return string


def get_frame_closing(state: w2bstate) -> str:
    return f" {state.frame_footer} \n\\end{{frame}}\n"


def transform_spec_to_title_slide(string: str, state: w2bstate) -> str:
    frame_opening = (
        r"\n\\begin{frame}\n\\frametitle{}\n\\begin{center}\n{\\Huge \1}\n\\end{center}\n"
    )
    frame_closing = escape_resub(get_frame_closing(state))

    p = re.compile(r"^=!\s*(.*?)\s*!=(.*)", re.VERBOSE)

    if not state.frame_opened:
        _string = p.sub(frame_opening, string)
    else:
        _string = p.sub(frame_closing + frame_opening, string)

    if string != _string:
        state.frame_opened = True
        state.switch_to_next_frame()

    return _string


def transform_h4_to_frame(string: str, state: w2bstate) -> str:
    """headings (3) to frames"""
    frame_opening = (
        rf"\\begin{{frame}}\2\n \\frametitle{{\1}}\n {escape_resub(state.next_frame_header)} \n"
    )
    frame_closing = escape_resub(get_frame_closing(state))

    p = re.compile(r"^!?====\s*(.*?)\s*====(.*)", re.VERBOSE)
    if not state.frame_opened:
        _string = p.sub(frame_opening, string)
    else:
        _string = p.sub(frame_closing + frame_opening, string)

    if string != _string:
        state.frame_opened = True
        state.switch_to_next_frame()

    return _string


def transform_h3_to_subsec(string: str, state: w2bstate) -> str:
    """headings (2) to subsections"""
    frame_closing = escape_resub(get_frame_closing(state))
    subsec_opening = r"\n\\subsection\2{\1}\n\n"

    p = re.compile(r"^===\s*(.*?)\s*===(.*)", re.VERBOSE)
    if state.frame_opened:
        _string = p.sub(frame_closing + subsec_opening, string)
    else:
        _string = p.sub(subsec_opening, string)
    if string != _string:
        state.frame_opened = False

    return _string


def transform_h2_to_sec(string: str, state: w2bstate) -> str:
    """headings (1) to sections"""
    frame_closing = escape_resub(get_frame_closing(state))
    sec_opening = r"\n\\section\2{\1}\n\n"
    p = re.compile(r"^==\s*(.*?)\s*==(.*)", re.VERBOSE)
    if state.frame_opened:
        _string = p.sub(frame_closing + sec_opening, string)
    else:
        _string = p.sub(sec_opening, string)
    if string != _string:
        state.frame_opened = False

    return _string


def transform_replace_headfoot(string: str, state: w2bstate) -> str:
    string = string.replace("<---FRAMEHEADER--->", state.frame_header)
    return string.replace("<---FRAMEFOOTER--->", state.frame_footer)


def transform_environments(string: str, state: w2bstate) -> str:
    """
    latex environments, the users takes full responsibility
    for closing ALL opened environments
    exampe:
    <[block]{block title}
    message
    [block]>
    """
    # -> open
    p = re.compile(r"^<\[([^{}]*?)\]", re.VERBOSE)
    m = re.match(p, string)
    if m is not None and m.group(1).strip() != "frame":
        state.active_envs[m.group(1).strip()] = 1
    string = p.sub(r"\\begin{\1}", string)

    # -> close
    p = re.compile(r"^\[([^{}]*?)\]>", re.VERBOSE)
    m = re.match(p, string)
    if m is not None and m.group(1).strip() != "frame":
        del state.active_envs[m.group(1).strip()]
    return p.sub(r"\\end{\1}", string)


def transform_columns(string: str) -> str:
    """columns"""
    p = re.compile(r"^\[\[\[(.*?)\]\]\]", re.VERBOSE)
    return p.sub(r"\\column{\1}", string)


def transform_boldfont(string: str) -> str:
    """bold font"""
    p = re.compile("'''(.*?)'''", re.VERBOSE)
    return p.sub(r"\\textbf{\1}", string)


def transform_italicfont(string: str) -> str:
    """italic font"""
    p = re.compile("''(.*?)''", re.VERBOSE)
    return p.sub(r"\\emph{\1}", string)


def _transform_mini_parser(character: str, replacement: str, string: str) -> str:
    # implemented as a state-machine
    output: List[str] = []
    typewriter: List[str] = []
    seen_at, seen_escape = False, False
    for char in string:
        if seen_escape:
            if char == character:
                output.append(character)
            else:
                output.append("\\" + char)
            seen_escape = False
        elif char == "\\":
            seen_escape = True
        elif char == character:
            if seen_at:
                seen_at = False
                output, typewriter = typewriter, output
                output.append("\\" + replacement + "{")
                output += typewriter
                output.append("}")
                typewriter = []
            else:
                seen_at = True
                output, typewriter = typewriter, output
        else:
            output.append(char)
    if seen_at:
        output, typewriter = typewriter, output
        output.append(character)
        output += typewriter
    return "".join(output)


def transform_typewriterfont(string: str) -> str:
    """typewriter font"""
    return _transform_mini_parser("@", "texttt", string)


def transform_alerts(string: str) -> str:
    """alerts"""
    return _transform_mini_parser("!", "alert", string)


def transform_colors(string: str, state: w2bstate) -> str:
    """colors"""

    def maybe_replace(m: Match[str]) -> str:
        """only replace if we are not within <<< >>>"""
        for g in graphics:
            # found color is within a graphics token
            if m.start() >= g.start() and m.end() <= g.end():
                return m.string[m.start() : m.end()]

        return "\\textcolor{" + m.group(1) + "}{" + m.group(2) + "}"

    if "equation" in state.active_envs:
        return string

    p = re.compile(r"(\<\<\<)(.*?)\>\>\>", re.VERBOSE)
    graphics = list(p.finditer(string))
    p = re.compile("_([^_\\\\{}]*?)_([^_]*?[^_\\\\{}])_", re.VERBOSE)
    return p.sub(maybe_replace, string)


def transform_footnotes(string: str) -> str:
    """footnotes"""
    p = re.compile(r"\(\(\((.*?)\)\)\)", re.VERBOSE)
    return p.sub(r"\\footnote{\1}", string)


def transform_graphics(string: str) -> str:
    """figures/images"""
    p = re.compile(r"\<\<\<(.*?),(.*?)\>\>\>", re.VERBOSE)
    string = p.sub(r"\\includegraphics[\2]{\1}", string)
    p = re.compile(r"\<\<\<(.*?)\>\>\>", re.VERBOSE)
    return p.sub(r"\\includegraphics{\1}", string)


def transform_substitutions(string: str) -> str:
    """substitutions"""
    p = re.compile(r"(\s)-->(\s)", re.VERBOSE)
    string = p.sub(r"\1$\\rightarrow$\2", string)
    p = re.compile(r"(\s)<--(\s)", re.VERBOSE)
    string = p.sub(r"\1$\\leftarrow$\2", string)
    p = re.compile(r"(\s)==>(\s)", re.VERBOSE)
    string = p.sub(r"\1$\\Rightarrow$\2", string)
    p = re.compile(r"(\s)<==(\s)", re.VERBOSE)
    string = p.sub(r"\1$\\Leftarrow$\2", string)
    p = re.compile(r"(\s):-\)(\s)", re.VERBOSE)
    string = p.sub(r"\1\\smiley\2", string)
    p = re.compile(r"(\s):-\((\s)", re.VERBOSE)
    return p.sub(r"\1\\frownie\2", string)


def transform_vspace(string: str) -> str:
    """vspace"""
    p = re.compile(r"^\s*--(.*)--\s*$")
    return p.sub(r"\n\\vspace{\1}\n", string)


def transform_vspacestar(string: str) -> str:
    """vspace*"""
    p = re.compile(r"^\s*--\*(.*)--\s*$")
    return p.sub(r"\n\\vspace*{\1}\n", string)


def transform_uncover(string: str) -> str:
    """uncover"""
    p = re.compile(r"\+<(.*)>\s*{(.*)")  # +<1-2>{.... -> \uncover<1-2>{....
    return p.sub(r"\\uncover<\1>{\2", string)


def transform_only(string: str) -> str:
    """only"""
    p = re.compile(r"-<(.*)>\s*{(.*)")  # -<1-2>{.... -> \only<1-2>{....
    return p.sub(r"\\only<\1>{\2", string)


def transform(string: str, state: w2bstate) -> str:
    """convert/transform one line in context of state"""

    # string = transform_itemenums(string, state)
    string = transform_define_foothead(string, state)
    string = transform_detect_manual_frameclose(string, state)
    string = transform_spec_to_title_slide(string, state)
    string = transform_h4_to_frame(string, state)
    string = transform_h3_to_subsec(string, state)
    string = transform_h2_to_sec(string, state)
    string = transform_replace_headfoot(string, state)

    string = transform_environments(string, state)
    string = transform_columns(string)
    string = transform_boldfont(string)
    string = transform_italicfont(string)
    string = transform_typewriterfont(string)
    string = transform_alerts(string)
    string = transform_colors(string, state)
    string = transform_footnotes(string)
    string = transform_graphics(string)
    string = transform_substitutions(string)
    string = transform_vspacestar(string)
    string = transform_vspace(string)
    string = transform_uncover(string)
    string = transform_only(string)

    return transform_itemenums(string, state)


def expand_code_make_defverb(content: str, name: str) -> str:
    return f"\\defverbatim[colored]\\{name}{{\n{content}\n}}"


def expand_code_make_lstlisting(content: str, options: str) -> str:
    return f"\\begin{{lstlisting}}{options}{content}\\end{{lstlisting}}"


def expand_code_search_escape_sequences(code: str) -> Tuple[str, str]:
    esc_open = "1"
    esc_close = "2"
    while code.find(esc_open) != -1 or code.find(esc_close) != -1:
        esc_open += chr(random.randint(48, 57))
        esc_close += chr(random.randint(48, 57))

    return (esc_open, esc_close)


def expand_code_tokenize_anims(code: str) -> Tuple[List[str], List[str]]:
    # escape
    (esc_open, esc_close) = expand_code_search_escape_sequences(code)
    code = code.replace("\\[", esc_open)
    code = code.replace("\\]", esc_close)

    p = re.compile(r"\[\[(?:.|\s)*?\]\]|\[(?:.|\s)*?\]")
    non_anim = p.split(code)
    anim = p.findall(code)

    # unescape
    anim = [s.replace(esc_open, "\\[").replace(esc_close, "\\]") for s in anim]
    non_anim = [s.replace(esc_open, "[").replace(esc_close, "]") for s in non_anim]

    return (anim, non_anim)


T = TypeVar("T")


def make_unique(seq: List[T]) -> List[T]:
    """remove duplicate elements in a list, does not preserve order"""
    keys: Dict[T, int] = {}
    for elem in seq:
        keys[elem] = 1
    return list(keys.keys())


def expand_code_parse_overlayspec(overlayspec: str) -> List[int]:
    overlays: List[int] = []

    groups = overlayspec.split(",")
    for group in groups:
        group = group.strip()
        if group.find("-") != -1:
            nums = group.split("-")
            if len(nums) < 2:
                syntax_error("overlay specs must be of the form <(%d-%d)|(%d), ...>", overlayspec)
            else:
                try:
                    start = int(nums[0])
                    stop = int(nums[1])
                except ValueError:
                    syntax_error(
                        "not an int, overlay specs must be of the form <(%d-%d)|(%d), ...>",
                        overlayspec,
                    )

                overlays.extend(list(range(start, stop + 1)))
        else:
            try:
                num = int(group)
            except ValueError:
                syntax_error(
                    "not an int, overlay specs must be of the form <(%d-%d)|(%d), ...>", overlayspec
                )
            overlays.append(num)

    # make unique
    return make_unique(overlays)


def expand_code_parse_simpleanimspec(animspec: str) -> List[Tuple[int, str]]:
    # escape
    (esc_open, esc_close) = expand_code_search_escape_sequences(animspec)
    animspec = animspec.replace("\\[", esc_open)
    animspec = animspec.replace("\\]", esc_close)

    p = re.compile(r"^\[<([0-9,\-]+)>((?:.|\s)*)\]$")
    m = p.match(animspec)
    if m is not None:
        overlays = expand_code_parse_overlayspec(m.group(1))
        code = m.group(2)
    else:
        syntax_error("specification does not match [<%d>%s]", animspec)

    # unescape code
    code = code.replace(esc_open, "[").replace(esc_close, "]")

    return [(overlay, code) for overlay in overlays]


def expand_code_parse_animspec(animspec: str) -> Tuple[str, List[Tuple[int, str]]]:
    if len(animspec) < 4 or not animspec.startswith("[["):
        return ("simple", expand_code_parse_simpleanimspec(animspec))

    # escape
    (esc_open, esc_close) = expand_code_search_escape_sequences(animspec)
    animspec = animspec.replace("\\[", esc_open)
    animspec = animspec.replace("\\]", esc_close)

    p = re.compile(r"\[|\]\[|\]")
    simple_specs = [f"[{s}]" for s in [s for s in p.split(animspec) if len(s.strip()) > 0]]

    # unescape
    simple_specs = [s.replace(esc_open, "\\[").replace(esc_close, "\\]") for s in simple_specs]
    parsed_simple_specs = list(map(expand_code_parse_simpleanimspec, simple_specs))
    unified_pss = []
    for pss in parsed_simple_specs:
        unified_pss.extend(pss)
    return ("double", unified_pss)


def expand_code_getmaxoverlay(parsed_anims: List[List[Tuple[int, str]]]) -> int:
    max_overlay = 0
    for anim in parsed_anims:
        for spec in anim:
            max_overlay = max(spec[0], max_overlay)
    return max_overlay


def expand_code_getminoverlay(parsed_anims: List[List[Tuple[int, str]]]) -> int:
    min_overlay = sys.maxsize
    for anim in parsed_anims:
        for spec in anim:
            min_overlay = min(spec[0], min_overlay)
    if min_overlay == sys.maxsize:
        min_overlay = 0
    return min_overlay


def expand_code_genanims(
    parsed_animspec: List[Tuple[int, str]], minoverlay: int, maxoverlay: int, type: str
) -> List[str]:
    # get maximum length of code
    maxlen = 0
    if type == "double":
        for simple_animspec in parsed_animspec:
            maxlen = max(maxlen, len(simple_animspec[1]))

    out: List[str] = []
    fill = "".join([" " for i in range(maxlen)])
    out = [fill[:] for x in range(minoverlay, maxoverlay + 1)]

    for simple_animspec in parsed_animspec:
        out[simple_animspec[0] - minoverlay] = simple_animspec[1]

    return out


def expand_code_getname(code: str) -> str:
    hex2alpha_table = {
        "0": "a",
        "1": "b",
        "2": "c",
        "3": "d",
        "4": "e",
        "5": "f",
        "6": "g",
        "7": "h",
        "8": "i",
        "9": "j",
        "a": "k",
        "b": "l",
        "c": "m",
        "d": "n",
        "e": "o",
        "f": "p",
    }
    hexhash = md5hex(code)
    return "".join(hex2alpha_table[x] for x in hexhash)


def expand_code_makeoverprint(names: List[str], minoverlay: int) -> str:
    out = ["\\begin{overprint}\n"]
    for index, name in enumerate(names):
        out.append("  \\onslide<%d>\\%s\n" % (index + minoverlay, name))
    out.append("\\end{overprint}\n")

    return "".join(out)


def expand_code_get_unique_name(
    defverbs: Dict[str, str], code: str, lstparams: str
) -> Tuple[str, str]:
    """generate a collision free entry in the defverbs-map and names-list"""
    name = expand_code_getname(code)
    expanded_code = expand_code_make_defverb(expand_code_make_lstlisting(code, lstparams), name)
    rehash = ""
    while name in defverbs and defverbs[name] != expanded_code:
        rehash += chr(random.randint(65, 90))  # append a character from A-Z to rehash value
        name = expand_code_getname(code + rehash)
        expanded_code = expand_code_make_defverb(expand_code_make_lstlisting(code, lstparams), name)

    return (name, expanded_code)


def make_sorted(seq: Any) -> List[Any]:
    """replacement for sorted built-in"""
    l = list(seq)
    l.sort()
    return l


def expand_code_segment(result: List[str], codebuffer: List[str], state: w2bstate) -> None:
    # treat first line as params for lstlistings
    lstparams = codebuffer[0]
    codebuffer[0] = ""

    # join lines into one string
    code = "".join(codebuffer)

    # tokenize code into anim and non_anim parts
    (anim, non_anim) = expand_code_tokenize_anims(code)
    if len(anim) > 0:
        # generate multiple versions of the anim parts
        parsed_anims = list(map(expand_code_parse_animspec, anim))
        parsed_anim_lists = [x[1] for x in parsed_anims]
        max_overlay = expand_code_getmaxoverlay(parsed_anim_lists)
        # if there is unanimated code, use 0 as the starting overlay
        min_overlay = 1 if len(list(non_anim)) > 0 else expand_code_getminoverlay(parsed_anim_lists)
        gen_anims = [
            expand_code_genanims(x[1], min_overlay, max_overlay, x[0]) for x in parsed_anims
        ]
        anim_map: Dict[int, List[str]] = {}
        for i in range(max_overlay - min_overlay + 1):
            anim_map[i + min_overlay] = [x[i] for x in gen_anims]

        names: List[str] = []
        for overlay in make_sorted(anim_map.keys()):
            # combine non_anim and anim parts
            anim_map[overlay].append("")
            zipped = zip(non_anim, anim_map[overlay])
            code = "".join(x[0] + x[1] for x in zipped)

            # generate a collision free entry in the defverbs-map and names-list
            (name, expanded_code) = expand_code_get_unique_name(state.defverbs, code, lstparams)

            # now we have a collision free entry, append it
            names.append(name)
            state.defverbs[name] = expanded_code

        # append overprint area to result
        overprint = expand_code_makeoverprint(names, min_overlay)
        result.append(overprint)
    else:
        # we have no animations and can just put the defverbatim in
        # remove escapings
        code = code.replace("\\[", "[").replace("\\]", "]")
        (name, expanded_code) = expand_code_get_unique_name(state.defverbs, code, lstparams)
        state.defverbs[name] = expanded_code
        result.append(f"\n\\{name}\n")


def expand_code_defverbs(result: List[str], state: w2bstate) -> None:
    result[state.code_pos] = (
        result[state.code_pos] + "\n".join(list(state.defverbs.values())) + "\n"
    )
    state.defverbs.clear()


def get_autotemplate_closing() -> str:
    return "\n\\end{document}\n"


def parse_bool(string: str) -> bool:
    boolean = False

    if string in {"True", "true", "1"}:
        boolean = True
    elif string in {"False", "false", "0"}:
        boolean = False
    else:
        syntax_error("Boolean expected (True/true/1 or False/false/0)", string)

    return boolean


def parse_autotemplate(autotemplatebuffer: List[str]) -> List[Tuple[str, str]]:
    r"""
    @param autotemplatebuffer (list)
        a list of lines found in the autotemplate section
    @return (list)
        a list of tuples of the form (string, string) with \command.parameters pairs
    """
    autotemplate: List[Tuple[str, str]] = []

    for line in autotemplatebuffer:
        if len(line.lstrip()) == 0:  # ignore empty lines
            continue
        if len(line.lstrip()) > 0 and line.lstrip().startswith(
            "%"
        ):  # ignore lines starting with % as comments
            continue

        tokens = line.split("=", 1)
        if len(tokens) < 2:
            syntax_error("lines in the autotemplate section have to be of the form key=value", line)

        autotemplate.append((tokens[0], tokens[1]))

    return autotemplate


def parse_usepackage(usepackage: str) -> Tuple[str, Optional[str]]:
    """
    @param usepackage (str)
        the unparsed usepackage string in the form [options]{name}
    @return (tuple)
        (name(str), options(str))
    """

    p = re.compile(r"^\s*(\[.*\])?\s*\{(.*)\}\s*$")
    m = p.match(usepackage)
    if m is None:
        syntax_error("usepackage specifications have to be of the form [%s]{%s}", usepackage)
        return (
            "",
            None,
        )  # This line is never reached due to syntax_error, but needed for type checking

    g = m.groups()
    if len(g) < 2 or len(g) > 2 or (g[1] == None and g[1].strip() != ""):  # noqa: E711, PLC1901 # TODO: Fix this
        syntax_error("usepackage specifications have to be of the form [%s]{%s}", usepackage)
        return (
            "",
            None,
        )  # This line is never reached due to syntax_error, but needed for type checking
    options = g[0]
    name = g[1].strip()
    return (name, options)


def unify_autotemplates(autotemplates: List[List[Tuple[str, str]]]) -> List[Tuple[str, str]]:
    usepackages: Dict[str, Optional[str]] = {}  # packagename : options
    documentclass = ""
    titleframe = False

    merged: List[Tuple[str, str]] = []
    for template in autotemplates:
        for command in template:
            if command[0] == "usepackage":
                (name, options) = parse_usepackage(command[1])
                usepackages[name] = options
            elif command[0] == "titleframe":
                titleframe = parse_bool(command[1])
            elif command[0] == "documentclass":
                documentclass = command[1]
            else:
                merged.append(command)

    autotemplate: List[Tuple[str, str]] = []
    autotemplate.append(("documentclass", documentclass))
    for name, options in usepackages.items():
        string = (
            f"{options}{{{name}}}" if options is not None and options.strip() else f"{{{name}}}"
        )
        autotemplate.append(("usepackage", string))
    autotemplate.append(("titleframe", str(titleframe)))

    autotemplate.extend(merged)

    return autotemplate


def expand_autotemplate_gen_opening(autotemplate: List[Tuple[str, str]]) -> str:
    """
    @param autotemplate (list)
        the specification of the autotemplate in the form of a list of tuples
    @return (string)
        the string the with generated latex code
    """
    titleframe = False
    titleframeopts = ""
    out: List[str] = []
    for item in autotemplate:
        if item[0] == "titleframe":
            titleframe = parse_bool(item[1])
        elif item[0] == "titleframeopts":
            titleframeopts = item[1]
        else:
            out.append("\\{}{}".format(*item))

    out.append("\n\\begin{document}\n")
    if titleframe:
        out.append(f"\n\\frame{titleframeopts}{{\\titlepage}}\n")

    return "\n".join(out)


def expand_autotemplate_opening(
    result: List[str], templatebuffer: List[str], state: w2bstate
) -> None:
    my_autotemplate = parse_autotemplate(templatebuffer)
    the_autotemplate = unify_autotemplates([autotemplate, my_autotemplate])

    opening = expand_autotemplate_gen_opening(the_autotemplate)
    result.extend([opening, ""])
    state.code_pos = len(result)
    state.autotemplate_opened = True


def get_autotemplatemode(line: str, autotemplatemode: bool) -> Tuple[str, bool]:  # noqa: FBT001
    autotemplatestart = re.compile(r"^<\[\s*autotemplate\s*\]")
    autotemplateend = re.compile(r"^\[\s*autotemplate\s*\]>")
    if not autotemplatemode and autotemplatestart.match(line) is not None:
        line = autotemplatestart.sub("", line)
        return (line, True)
    if autotemplatemode and autotemplateend.match(line) is not None:
        line = autotemplateend.sub("", line)
        return (line, False)
    return (line, autotemplatemode)


def scan_for_selected_frames(lines: List[str]) -> bool:
    """scans for frames that should be rendered exclusively, returns true if such frames have been found"""
    p = re.compile(r"^!====\s*(.*?)\s*====(.*)", re.VERBOSE)
    for line in lines:
        mo = p.match(line)
        if mo is not None:
            return True
    return False


def line_opens_unselected_frame(line: str) -> bool:
    p = re.compile(r"^====\s*(.*?)\s*====(.*)", re.VERBOSE)
    return p.match(line) is not None


def line_opens_selected_frame(line: str) -> bool:
    p = re.compile(r"^!====\s*(.*?)\s*====(.*)", re.VERBOSE)
    return p.match(line) is not None


def line_closes_frame(line: str) -> bool:
    p = re.compile(r"^\s*\[\s*frame\s*\]>", re.VERBOSE)
    return p.match(line) is not None


def filter_selected_lines(lines: List[str]) -> List[str]:
    selected_lines: List[str] = []

    selected_frame_opened = False
    frame_closed = True
    frame_manually_closed = False
    for line in lines:
        if line_opens_selected_frame(line):
            selected_frame_opened = True
            frame_closed = False

        if line_opens_unselected_frame(line):
            selected_frame_opened = False
            frame_closed = False

        if line_closes_frame(line):
            selected_frame_opened = False
            frame_closed = True
            frame_manually_closed = True

        if selected_frame_opened or (frame_closed and not frame_manually_closed):
            selected_lines.append(line)

    return selected_lines


def convert2beamer(lines: List[str]) -> List[str]:
    selectedframemode = scan_for_selected_frames(lines)
    return convert2beamer_selected(lines) if selectedframemode else convert2beamer_full(lines)


def convert2beamer_selected(lines: List[str]) -> List[str]:
    selected_lines = filter_selected_lines(lines)
    return convert2beamer_full(selected_lines)


def include_file(line: str) -> Optional[str]:
    """Extract filename to include.

    @param line string
        a line that might include an inclusion
    @return string or None
        if the line contains an inclusion, return the filename,
        otherwise return None
    """
    p = re.compile(r"\>\>\>(.*?)\<\<\<", re.VERBOSE)
    if p.match(line):
        return p.sub(r"\1", line)
    return None


def include_file_recursive(base: str) -> List[str]:
    stack: List[str] = []
    output: List[str] = []

    def recurse(file_: str) -> None:
        stack.append(file_)
        nowikimode = False
        codemode = False
        for line in get_lines_from_cache(file_):
            if nowikimode or codemode:
                if nowikiendre.match(line):
                    nowikimode = False
                elif codeendre.match(line):
                    codemode = False
                output.append(line)
            elif nowikistartre.match(line):
                output.append(line)
                nowikimode = True
            elif codestartre.match(line):
                output.append(line)
                codemode = True
            else:
                include = include_file(line)
                if include is not None:
                    if include in stack:
                        raise IncludeLoopException(
                            "Loop detected while trying "
                            f"to include: '{include}'.\n" + "Stack: " + "->".join(stack)
                        )
                    recurse(include)
                else:
                    output.append(line)
        stack.pop()

    recurse(base)
    return output


def munge_input_lines(lines: List[str]) -> List[str]:
    # join lines if they end with single \
    munge = False
    new_lines: List[str] = []
    for line in lines:
        if munge is True:
            if not line.endswith("\\") and not line.endswith("\\\\"):
                munge = False
            else:
                line = line[:-1]
            new_lines[-1] += line
        else:
            if line.endswith("\\") and not line.endswith("\\\\"):
                munge = True
                line = line[:-1]
            new_lines.append(line)
    return new_lines


def convert2beamer_full(lines: List[str]) -> List[str]:
    """convert to LaTeX beamer"""
    state = w2bstate()
    result: List[str] = [""]  # start with one empty line as line 0
    codebuffer: List[str] = []
    autotemplatebuffer: List[str] = []

    nowikimode = False
    codemode = False
    autotemplatemode = False

    for line in lines:
        (line, nowikimode) = get_nowikimode(line, nowikimode)
        if nowikimode:
            result.append(line)
        else:
            (line, _codemode) = get_codemode(line, codemode)
            if _codemode and not codemode:  # code mode was turned on
                codebuffer = []
            elif not _codemode and codemode:  # code mode was turned off
                expand_code_segment(result, codebuffer, state)

            if codemode or _codemode:
                codebuffer.append(line)
                codemode = _codemode
            else:
                (line, _autotemplatemode) = get_autotemplatemode(line, autotemplatemode)
                if _autotemplatemode and not autotemplatemode:  # autotemplate mode was turned on
                    autotemplatebuffer = []
                elif not _autotemplatemode and autotemplatemode:  # autotemplate mode was turned off
                    expand_autotemplate_opening(result, autotemplatebuffer, state)
                autotemplatemode = _autotemplatemode

                if autotemplatemode:
                    autotemplatebuffer.append(line)
                else:
                    state.current_line = len(result)
                    result.append(transform(line, state))

    result.append(transform("", state))  # close open environments

    if state.frame_opened:
        result.append(get_frame_closing(state))
    if state.autotemplate_opened:
        result.append(get_autotemplate_closing())

    # insert defverbs somewhere at the beginning
    expand_code_defverbs(result, state)

    return result


def print_result(lines: List[str]) -> None:
    """print result to stdout"""
    for line in lines:
        pprint(line, file=sys.stdout)


def redirect_stdout(outfilename: str) -> None:
    global _redirected_stdout  # noqa: PLW0603
    outfile = Path(outfilename).open("w", encoding="utf-8")  # noqa: SIM115
    _redirected_stdout = outfile


def main(argv: List[str]) -> None:  # noqa: ARG001
    """check parameters, start file processing"""
    usage = "%prog [options] [input1.txt [input2.txt ...]] > output.tex"
    version = "%prog (http://wiki2beamer.sf.net), version: " + VERSIONTAG

    parser = optparse.OptionParser(usage="\n  " + usage, version=version)
    parser.add_option(
        "-o",
        "--output",
        dest="output",
        metavar="FILE",
        help="write output to FILE instead of stdout",
    )
    opts, args = parser.parse_args()

    if opts.output is not None:
        redirect_stdout(opts.output)

    input_files: List[str] = []
    if not sys.stdin.isatty():
        _file_cache["stdin"] = joinLines(sys.stdin.readlines())
        input_files.append("stdin")
    elif len(args) == 0:
        parser.error("You supplied no files to convert!")

    input_files += args
    lines: List[str] = []
    for file_ in input_files:
        lines += include_file_recursive(file_)

    lines = munge_input_lines(lines)

    lines = convert2beamer(lines)
    print_result(lines)


if __name__ == "__main__":
    main(sys.argv)
