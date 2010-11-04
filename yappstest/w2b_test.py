#!/usr/bin/env python

import w2b

def ast_print_escape(string):
    string = string.replace('\n', '\\n')
    string = string.replace('\r', '\\r')
    string = string.replace('\t', '\\t')
    return string

def ast_print(ast_node, level):
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
        print '"%s"' % (ast_print_escape(ast_node)) ,
    else:
        print type(ast_node)

    return

if __name__ == '__main__':
    from sys import argv, stdin
    if len(argv) >= 2:
        if len(argv) >= 3:
            f = open(argv[2],'r')
        else:
            f = stdin
        ast_print(w2b.parse(argv[1], f.read()), 0)
    else: print >>sys.stderr, 'Args:  <rule> [<filename>]'

