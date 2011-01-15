#!/usr/bin/env python

import w2b
from yapps import yappsrt
import traceback
import sys


def ast_print_escape(ustring):
    string = ustring.encode("utf8")
    string = string.replace('\n', '\\n')
    string = string.replace('\r', '\\r')
    string = string.replace('\t', '\\t')
    return string

def ast_print(ast_node, level=0):
    space_prefix = level * ' '
    if type(ast_node) == list:
        print '\n%s[' % space_prefix ,
        for node in ast_node:
            ast_print(node, level+1)
        print '\n%s]' % space_prefix ,

    elif type(ast_node) == tuple:
        if len(ast_node) > 1:
            print '\n%s%s(' % (space_prefix, ast_node[0]) ,
            ast_print(ast_node[1], level+1)
            if type(ast_node[1]) == str:
                print ')' ,
            else:
                print '\n%s)' % (space_prefix) ,
        else:
            print '\n%s%s()' % (space_prefix, ast_node[0]) ,

    elif type(ast_node) == str:
        print 'WARNING -- str found, fix parser!!!: "%s"' % (ast_print_escape(ast_node)) ,
    elif type(ast_node) == unicode:
        print '"%s"' % (ast_print_escape(ast_node)) ,
    else:
        print type(ast_node)

    return

if __name__ == '__main__':
    from sys import argv, stdin
    if len(argv) >= 1:
        if len(argv) >= 2:
            f = open(argv[1],'r')
        else:
            f = stdin
        
        text = f.read()
        text = text.decode("utf8")
        scanner = w2b.wiki2beamerScanner(text)
        parser = w2b.wiki2beamer(scanner)
        ast = None
        try:
            ast = parser.document()
        except yappsrt.SyntaxError, e:
            traceback.print_exc()
            print >>sys.stderr, ""
            input = scanner.input
            yappsrt.print_error(input, e, scanner)
        except yappsrt.NoMoreTokens:
            traceback.print_exc()
            print >>sys.stderr, ""
            print >>sys.stderr, "Could not complete parsing; stopped around here:"
            print >>sys.stderr, scanner
        
        if ast != None:
            ast_print(ast)
        
    else: print >>sys.stderr, 'Args: [<filename>]'

