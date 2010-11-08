#!/usr/bin/env python

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

import sys
import unittest
import re
import random

sys.path.append('../code')
from wiki2beamer import *

class TestBasics(unittest.TestCase):

    def test_join_lines_standard(self):
        lines = ['', 'foo%', 'bar']
        joined = joinLines(lines)
        self.assertEqual(len(joined), 2)
        self.assertEqual(joined[0], lines[0])
        self.assertEqual(joined[1], 'foobar')

    def test_join_lines_shortlines(self):
        lines = ['%', '%']
        joined = joinLines(lines)
        self.assertEqual(len(joined), 0)

    def test_escape_resub(self):
        string = r"foo \1 bar"
        expected = r"foo \\1 bar"
        out = escape_resub(string)
        self.assertEqual(expected,out)

    def test_escape_resub2(self):
        instr = "abc"
        substr = r'a\1'
        p = re.compile(".*(b).*")
        out = p.sub(escape_resub(substr), instr)
        self.assertEqual(out, substr)


class TestTransform(unittest.TestCase):
    def setUp(self):
        self.state = w2bstate()
        return

    def tearDown(self):
        self.state = None
        return

    def test_substitutions(self):
        self.assertEqual(transform('foo --> bar', self.state), r'foo $\rightarrow$ bar')
        self.assertEqual(transform('foo <-- bar', self.state), r'foo $\leftarrow$ bar')

    def test_section(self):
        self.assertEqual(transform('== foo ==', self.state), '\n\\section{foo}\n\n')
    
    def test_subsection(self):
        self.assertEqual(transform('=== foo ===', self.state), '\n\\subsection{foo}\n\n')

    def test_footnote(self):
        self.assertEqual(transform('(((foo)))', self.state), '\\footnote{foo}')

    def test_columns(self):
        self.assertEqual(transform('[[[6cm]]]', self.state), '\\column{6cm}')

    def test_typewriter(self):
        input_expected = [('@TEST@', '\\texttt{TEST}'),
                          ('@TEST', '@TEST'),
                          ('TEST@', 'TEST@'),
                          ('@TEST@TEST@', '\\texttt{TEST}TEST@'),
                          ('@TEST@ test @TEST@',
                              '\\texttt{TEST} test \\texttt{TEST}'),
                          ('\@TEST\@', '@TEST@'),
                          ('\\TEST', '\\TEST'),
                          ('@TEST\@TEST@', '\\texttt{TEST@TEST}'),
                          ('\@TEST @TEST@ TEST\@',
                              '@TEST \\texttt{TEST} TEST@')]
        for input_, expected in input_expected:
            self.assertEqual(transform(input_, self.state), expected)

    def test_alert(self):
        input_expected = [('!TEST!', '\\alert{TEST}'),
                          ('!TEST', '!TEST'),
                          ('TEST!', 'TEST!'),
                          ('!TEST!TEST!', '\\alert{TEST}TEST!'),
                          ('!TEST! test !TEST!',
                              '\\alert{TEST} test \\alert{TEST}'),
                          ('\!TEST\!', '!TEST!'),
                          ('\\TEST', '\\TEST'),
                          ('!TEST\!TEST!', '\\alert{TEST!TEST}'),
                          ('\!TEST !TEST! TEST\!',
                              '!TEST \\alert{TEST} TEST!')]
        for input_, expected in input_expected:
            self.assertEqual(transform(input_, self.state), expected)

    def test_vspace(self):
        self.assertEqual(transform('--3em--', self.state), '\n\\vspace{3em}\n')
        self.assertEqual(transform('--3em--foo', self.state), '--3em--foo')
        self.assertEqual(transform(' --3em-- ', self.state), '\n\\vspace{3em}\n')

    def test_vspacestar(self):
        self.assertEqual(transform('--*3em--', self.state), '\n\\vspace*{3em}\n')
        self.assertEqual(transform('--*3em--foo', self.state), '--*3em--foo')
        self.assertEqual(transform(' --*3em-- ', self.state), '\n\\vspace*{3em}\n')

    def test_uncover(self):
        self.assertEqual(transform('+<2-> {foo}', self.state), '\uncover<2->{foo}')
        self.assertEqual(transform(' +<2->{\nfoo', self.state), ' \uncover<2->{\nfoo')

    def test_only(self):
        self.assertEqual(transform('-<2-> {foo}', self.state), '\only<2->{foo}')
        self.assertEqual(transform(' -<2->{\nfoo', self.state), ' \only<2->{\nfoo')
    
    def test_uncover_intext(self):
        self.assertEqual(transform('foo +<2->{moo} bar', self.state), 'foo \uncover<2->{moo} bar')
        self.assertEqual(transform(\
            'foo +<2-3>  {\\begin{enumerate} \\end{enumerate}}', self.state),\
            'foo \\uncover<2-3>{\\begin{enumerate} \\end{enumerate}}')


class TestExpandCode(unittest.TestCase):
    def test_search_escape_sequences_basic(self):
        code = "System435.out.println(\"foo\");123System.ou12t.println234(\"foo\");System.23out.23456println(\"foo\");S237yst28em.out.pr18intln(\"foo\");"
        (open, close) = expand_code_search_escape_sequences(code)
        self.assertEqual(code.find(open), -1)
        self.assertEqual(code.find(close), -1)

    def test_search_escape_sequences_short(self):
        code = "12"
        (open, close) = expand_code_search_escape_sequences(code)
        self.assertEqual(code.find(open), -1)
        self.assertEqual(code.find(close), -1)

    def test_search_escape_sequences_veryshort(self):
        code = ""
        (open, close) = expand_code_search_escape_sequences(code)
        self.assertEqual(code.find(open), -1)
        self.assertEqual(code.find(close), -1)

    def test_search_escape_sequences_large(self):
        code = []
        for i in xrange(0, 10000):
            code.append(chr(random.randint(48,57)))
        code = ''.join(code)

        (open, close) = expand_code_search_escape_sequences(code)
        self.assertEqual(code.find(open), -1)
        self.assertEqual(code.find(close), -1)

    def test_expand_code_tokenize_anims(self):
        items = ['1', '2', '3', '-', ',', '[', ']', '<', '>', 'a', 'b', 'c', 'd', 'e', '}', '{']
        code = []
        for i in xrange(0, 100):
            code.extend(items)
            random.shuffle(items)
        
        out = expand_code_tokenize_anims(''.join(code))
        self.assert_(len(out[0])>0)
        self.assert_(len(out[1])>0)
        for item in out[0]: #anims
            self.assert_(item.startswith('[') and item.endswith(']'))
        for item in out[1]: #non-anims
            self.assert_(not (item.startswith('[') and item.endswith(']')))
    
    def test_expand_code_tokenize_anims_empty(self):
        out = expand_code_tokenize_anims('')
        self.assertEqual(out[0], [])
        self.assertEqual(out[1], [''])

class TestConvert2Beamer(unittest.TestCase):
    def setUp(self):
        return
    
    def tearDown(self):
        return

    def test_nowiki(self):
        lines = ['<[nowiki ]%',\
                '==== foo ====',\
                '[ nowiki]>moo']
        expected = ['\n', '%',\
                '==== foo ====',\
                'moo',\
                '']
        out = convert2beamer(lines)
        self.assertEqual(out, expected)
     
    def test_not_nowiki(self):
        lines = [' <[nowiki]', '== foo ==']
        expected = ['\n', ' <[nowiki]', '\n\section{foo}\n\n', '']
        out = convert2beamer(lines)
        self.assertEqual(out, expected)
    
    def test_frame_open_close(self):
        lines = ['==== foo ====']
        expected = ['\n', '\\begin{frame}\n \\frametitle{foo}\n  \n', '', '  \n \\end{frame}\n']
        out = convert2beamer(lines)
        self.assertEqual(out, expected)
    def test_frame_open_close_again(self):
        lines = ['==== foo ====', '==== bar ====']
        expected = ['\n', '\\begin{frame}\n \\frametitle{foo}\n  \n', '  \n \\end{frame}\n\\begin{frame}\n \\frametitle{bar}\n  \n', '', '  \n \\end{frame}\n']
        out = convert2beamer(lines)
        self.assertEqual(out, expected)

    def test_frame_close_detect(self):
        lines = ['==== foo ====', '[ frame ]>', '==== bar ====']
        expected = ['\n', '\\begin{frame}\n \\frametitle{foo}\n  \n', '\\end{ frame }', '\\begin{frame}\n \\frametitle{bar}\n  \n', '', '  \n \\end{frame}\n']
        out = convert2beamer(lines)
        self.assertEqual(out, expected)


    def test_itemize(self):
        lines = ['* foo', '* bar', '** foobar']
        expected = ['\n', '\\begin{itemize}\n  \\item foo', '  \\item bar', '\\begin{itemize}\n  \\item foobar', '\\end{itemize}\n\\end{itemize}\n']
        out = convert2beamer(lines)
        self.assertEqual(out, expected)

    def test_enumerate(self):
        lines = ['# one', '# two', '## onetwo']
        expected = ['\n', '\\begin{enumerate}\n  \\item one', '  \\item two', '\\begin{enumerate}\n  \\item onetwo', '\\end{enumerate}\n\\end{enumerate}\n']
        out = convert2beamer(lines)
        self.assertEqual(out,expected)

    def test_itemenum(self):
        lines = ['# one', '#* onefoo', '#* onebar', '## oneone', '#*# onefooone']
        expected = ['\n', '\\begin{enumerate}\n  \\item one', '\\begin{itemize}\n  \\item onefoo', '  \\item onebar', '\\end{itemize}\n\\begin{enumerate}\n  \\item oneone', '\\end{enumerate}\n\\begin{itemize}\n\\begin{enumerate}\n  \\item onefooone', '\\end{enumerate}\n\\end{itemize}\n\\end{enumerate}\n']
        out = convert2beamer(lines)
        self.assertEqual(out, expected)

    def test_header(self):
        lines = ['==== foo ====', '@FRAMEHEADER=bar', '==== bar ====']
        expected = ['\n', '\\begin{frame}\n \\frametitle{foo}\n  \n', '', '  \n \\end{frame}\n\\begin{frame}\n \\frametitle{bar}\n bar \n', '', '  \n \\end{frame}\n']
        out = convert2beamer(lines)
        self.assertEqual(out,expected)

    def test_footer(self):
        lines = ['==== foo ====', '@FRAMEFOOTER=bar', '==== bar ====']
        expected = ['\n', '\\begin{frame}\n \\frametitle{foo}\n  \n', '', '  \n \\end{frame}\n\\begin{frame}\n \\frametitle{bar}\n  \n', '', ' bar \n \\end{frame}\n']
        out = convert2beamer(lines)
        self.assertEqual(out,expected)

    def test_subexp_footer(self):
        lines = ['==== foo ====', '@FRAMEFOOTER=\\buge bar\\3', '==== bar ====']
        expected = ['\n', '\\begin{frame}\n \\frametitle{foo}\n  \n', '', '  \n \\end{frame}\n\\begin{frame}\n \\frametitle{bar}\n  \n', '', ' \\buge bar\\3 \n \\end{frame}\n']
        out = convert2beamer(lines)
        self.assertEqual(out,expected)

    def test_section_footer(self):
        lines = ['==== foo ====', '@FRAMEFOOTER=bar', '== foosec ==', '==== bar ====']
        expected = ['\n', '\\begin{frame}\n \\frametitle{foo}\n  \n', '', '  \n \\end{frame}\n\n\\section{foosec}\n\n', '\\begin{frame}\n \\frametitle{bar}\n  \n', '', ' bar \n \\end{frame}\n']
        out = convert2beamer(lines)
        self.assertEqual(out,expected)
    
    def test_itemizeclose_column(self):
        lines = ['* foo', '[[[6cm]]]']
        expected = ['\n', '\\begin{itemize}\n  \\item foo', '\\end{itemize}\n\\column{6cm}', '']
        out = convert2beamer(lines)
        self.assertEqual(out,expected)
    


class TestFileInclusion(unittest.TestCase):
    def setUp(self):
        files = {'test_file': ['test file content'],
                 'test_file2':['content from test_file2',
                               '>>>test_file<<<'],
                 'test_file3':['content from test_file3',
                               '<[nowiki]',
                               '>>>test_file<<<',
                               '[nowiki]>'],
                 'test_file_loop':['test_file_loop content',
                               '>>>test_file_loop<<<'],
                 'test_file_code':['<[code]',
                                   '>>>test_file<<<',
                                   '[code]>'],
                 'test_file_code_nowiki':['<[code]',
                                          '<[nowiki]',
                                          '>>>test_file<<<',
                                          '[nowiki]>',
                                          '[code]>']

                }
        for file_, lines in files.items():
            add_lines_to_cache(file_, lines)
        return
    
    def tearDown(self):
        clear_file_cache()
        return

    def test_include_file_works(self):
        expected = 'test_file'
        line = ">>>test_file<<<"
        out = include_file(line)
        self.assertEqual(expected, out)

    def test_include_file_recursive_works(self):
        expected = ['content from test_file2',
                  'test file content']
        out = include_file_recursive('test_file2')
        self.assertEqual(expected, out)

    def test_include_file_recursive_honors_nowiki(self):
        expected = ['content from test_file3', '<[nowiki]', '>>>test_file<<<', '[nowiki]>']
        out = include_file_recursive('test_file3')
        self.assertEqual(expected, out)

    def test_include_file_recursive_detects_loop(self):
        expected = ["test_file_loop content"]
        self.assertRaises(Exception, include_file_recursive, 'test_file_loop')

    def test_include_file_disabled_inside_code(self):
        expected = ['\\defverbatim[colored]\\mfkjiamnpineejahopjoapckhioohfpa{\n\\begin{lstlisting}>>>test_file<<<\\end{lstlisting}\n}\n', '\n\\mfkjiamnpineejahopjoapckhioohfpa\n', '', '']
        out = include_file_recursive('test_file_code')
        out = convert2beamer(out)
        self.assertEqual(out,expected)

def test_include_file_inside_code_inside_nowiki(self):
        expected = ['\\defverbatim[colored]\\nebnimnjipaalcaeojiaajjiompiecho{\n\\begin{lstlisting}\\end{lstlisting}\n}\n', '', '>>>test_file<<<', '\n\\nebnimnjipaalcaeojiaajjiompiecho\n', '', '']
        out = include_file_recursive('test_file_code_nowiki')
        out = convert2beamer(out)
        self.assertEqual(out,expected)

class TestSelectedFramesMode(unittest.TestCase):
    def setUp(self):
        return

    def tearDown(self):
        return
    
    def test_selected_frames_simple(self):
        lines = ['!==== foo ====', 'mooo']
        expected = ['!==== foo ====', 'mooo']
        out = filter_selected_lines(lines)
        self.assertEqual(out,expected)
    
    def test_unselected_frames_simple(self):
        lines = ['==== foo ====', 'moo']
        expected = []
        out = filter_selected_lines(lines)
        self.assertEqual(out,expected)

    def test_selected_frames_mixed(self):
        lines = ['==== unselected ====', 'foo', '', '!==== selected ====', 'moo', '==== unselected2 ====', 'moo', '!==== selected2 ====', 'moo']
        expected = ['!==== selected ====', 'moo', '!==== selected2 ====', 'moo']
        out = filter_selected_lines(lines)
        self.assertEqual(out,expected)

    def test_selected_frames_autotemplate(self):
        lines = ['<[autotemplate]', '[autotemplate]>', '!==== selected ====', 'foo', '', '==== unselected ====']
        expected = ['<[autotemplate]', '[autotemplate]>', '!==== selected ====', 'foo', '']
        out = filter_selected_lines(lines)
        self.assertEqual(out,expected)

if __name__=="__main__":
    print "Testing wiki2beamer version %s" % (VERSIONTAG)
    unittest.main()
