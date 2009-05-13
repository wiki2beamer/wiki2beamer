#!/usr/bin/env python
import sys
import unittest

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

class TestConvert2Beamer(unittest.TestCase):
    def setUp(self):
        return
    
    def tearDown(self):
        return

    def test_nowiki(self):
        lines = ['<[nowiki ]%',\
                '==== foo ====',\
                '[ nowiki]>moo']
        expected = ['%',\
                '==== foo ====',\
                'moo',\
                '']
        out = convert2beamer(lines)
        self.assertEqual(out, expected)
     
    def test_not_nowiki(self):
        lines = [' <[nowiki]', '== foo ==']
        expected = [' <[nowiki]', '\n\section{foo}\n\n', '']
        out = convert2beamer(lines)
        self.assertEqual(out, expected)
    
    def test_frame_open_close(self):
        lines = ['==== foo ====']
        expected = ['\\begin{frame}\n \\frametitle{foo}\n  \n', '', '  \n \\end{frame}\n']
        out = convert2beamer(lines)
        self.assertEqual(out, expected)
    def test_frame_open_close_again(self):
        lines = ['==== foo ====', '==== bar ====']
        expected = ['\\begin{frame}\n \\frametitle{foo}\n  \n', '  \n \\end{frame}\n\\begin{frame}\n \\frametitle{bar}\n  \n', '', '  \n \\end{frame}\n']
        out = convert2beamer(lines)
        self.assertEqual(out, expected)

    def test_frame_close_detect(self):
        lines = ['==== foo ====', '[ frame ]>', '==== bar ====']
        expected = ['\\begin{frame}\n \\frametitle{foo}\n  \n', '\\end{ frame }', '\\begin{frame}\n \\frametitle{bar}\n  \n', '', '  \n \\end{frame}\n']
        out = convert2beamer(lines)
        self.assertEqual(out, expected)


    def test_itemize(self):
        lines = ['* foo', '* bar', '** foobar']
        expected = ['\\begin{itemize}\n  \\item foo', '  \\item bar', '\\begin{itemize}\n  \\item foobar', '\\end{itemize}\n\\end{itemize}\n']
        out = convert2beamer(lines)
        self.assertEqual(out, expected)

    def test_enumerate(self):
        lines = ['# one', '# two', '## onetwo']
        expected = ['\\begin{enumerate}\n  \\item one', '  \\item two', '\\begin{enumerate}\n  \\item onetwo', '\\end{enumerate}\n\\end{enumerate}\n']
        out = convert2beamer(lines)
        self.assertEqual(out,expected)

    def test_itemenum(self):
        lines = ['# one', '#* onefoo', '#* onebar', '## oneone', '#*# onefooone']
        expected = ['\\begin{enumerate}\n  \\item one', '\\begin{itemize}\n  \\item onefoo', '  \\item onebar', '\\end{itemize}\n\\begin{enumerate}\n  \\item oneone', '\\end{enumerate}\n\\begin{itemize}\n\\begin{enumerate}\n  \\item onefooone', '\\end{enumerate}\n\\end{itemize}\n\\end{enumerate}\n']
        out = convert2beamer(lines)
        self.assertEqual(out, expected)

    def test_header(self):
        lines = ['==== foo ====', '@FRAMEHEADER=bar', '==== bar ====']
        expected = ['\\begin{frame}\n \\frametitle{foo}\n  \n', '', '  \n \\end{frame}\n\\begin{frame}\n \\frametitle{bar}\n bar \n', '', '  \n \\end{frame}\n']
        out = convert2beamer(lines)
        self.assertEqual(out,expected)

    def test_footer(self):
        lines = ['==== foo ====', '@FRAMEFOOTER=bar', '==== bar ====']
        expected = ['\\begin{frame}\n \\frametitle{foo}\n  \n', '', '  \n \\end{frame}\n\\begin{frame}\n \\frametitle{bar}\n  \n', '', ' bar \n \\end{frame}\n']
        out = convert2beamer(lines)
        self.assertEqual(out,expected)

    def test_subexp_footer(self):
        lines = ['==== foo ====', '@FRAMEFOOTER=\\buge bar\\3', '==== bar ====']
        expected = ['\\begin{frame}\n \\frametitle{foo}\n  \n', '', '  \n \\end{frame}\n\\begin{frame}\n \\frametitle{bar}\n  \n', '', ' \\buge bar\\3 \n \\end{frame}\n']
        out = convert2beamer(lines)
        self.assertEqual(out,expected)

    def test_section_footer(self):
        lines = ['==== foo ====', '@FRAMEFOOTER=bar', '== foosec ==', '==== bar ====']
        expected = ['\\begin{frame}\n \\frametitle{foo}\n  \n', '', '  \n \\end{frame}\n\n\\section{foosec}\n\n', '\\begin{frame}\n \\frametitle{bar}\n  \n', '', ' bar \n \\end{frame}\n']
        out = convert2beamer(lines)
        self.assertEqual(out,expected)
    
if __name__=="__main__":
    unittest.main()
