#first sketches for a yapps2 LL(1) grammar for wiki2beamer and some LaTeX

parser wiki2beamer:
	token END:		"$"
	token SPACE:		"[ \\t]+"
	token NEWLINE:		"[\\n\\r]+"
	token NUM:		"[0-9]+"
	token OVERLAY_SPEC_SEP:	"-"
	token WORD:		"[a-zA-Z]+"
	token PUNCTUATION:	"[,\\.\\?!:;\"'`´]+"
	token LATEX_COMMAND_NAME: "\\\\([a-z]+)"
	token BRACKET_CURLY_L:	"{"
	token BRACKET_CURLY_R:	"}"
	token BRACKET_ANGLE_L:	"<"
	token BRACKET_ANGLE_R:	">"
	token BRACKET_SQUARE_L:	"\\["
	token BRACKET_SQUARE_R:	"\\]"

	token W2B_H4_L:		"===="
	token W2B_H4_R:		"===="
	token W2B_ENDFRAME:	"\\[frame\\]>"

	rule document:
		{{ prepend = None }}
		[latex {{ prepend = latex }}]
		w2b_docbody
		END
		{{ return (prepend, w2b_docbody, 'END') }}

	rule w2b_docbody:
		{{ result = [] }}
		(
			w2b_frame	{{ result.append(w2b_frame) }}
		|	w2b_nonframe	{{ result.append(w2b_nonframe) }}
		)*
		{{ return ('W2B_DOCBODY', result) }}

	rule w2b_frame:
		w2b_frameheader
		latex
		{{ return ('W2B_FRAME', w2b_frameheader, latex) }}

	rule w2b_frameheader:
		W2B_H4_L SPACE WORD SPACE W2B_H4_R NEWLINE
			{{return ('W2B_FRAMEHEADER', (W2B_H4_L, WORD, W2B_H4_R)) }}
	
	rule w2b_nonframe:
		W2B_ENDFRAME NEWLINE
		latex {{ return ('W2B_NONFRAME', latex) }}

	rule latex:
		{{ result = [] }}
		( latex_entity {{ result.append(latex_entity) }} )*
		{{ return ('LATEX', result) }}

	rule latex_entity:
			WORD	{{return ('WORD', WORD)}}
		|	PUNCTUATION {{return ('PUNCTUATION', PUNCTUATION)}}
		|	SPACE	{{return ('SPACE', SPACE)}}
		|	NEWLINE	{{return ('NEWLINE', NEWLINE)}}
		|	latex_command	{{return latex_command}}

	rule latex_command:
		{{ result = [] }}
		LATEX_COMMAND_NAME {{ result.append(('LATEX_COMMAND_NAME', LATEX_COMMAND_NAME)) }}
		( latex_param {{result.append(latex_param) }} )*
		{{ return ('LATEX_COMMAND', result) }}
	rule latex_param:
			latex_param_angle_brackets
				{{ return ('LATEX_PARAM', latex_param_angle_brackets)  }}
		|	latex_param_curly_brackets
				{{ return ('LATEX_PARAM', latex_param_curly_brackets)  }}
		|	latex_param_square_brackets
				{{ return ('LATEX_PARAM', latex_param_square_brackets) }}
	

	rule latex_param_curly_brackets:
		BRACKET_CURLY_L latex BRACKET_CURLY_R
			{{ return ('LATEX_PARAM_CURLY_BRACKETS', (BRACKET_CURLY_L, latex, BRACKET_CURLY_R)) }}

	rule latex_param_square_brackets:
		BRACKET_SQUARE_L latex BRACKET_SQUARE_R
			{{ return ('LATEX_PARAM_SQUARE_BRACKETS', (BRACKET_SQUARE_L, latex, BRACKET_SQUARE_R)) }}
	
	rule latex_param_angle_brackets:
		BRACKET_ANGLE_L overlay_spec BRACKET_ANGLE_R
			{{ return ('LATEX_PARAM_ANGLE_BRACKETS', (BRACKET_ANGLE_L, overlay_spec, BRACKET_ANGLE_R)) }}
	
	rule overlay_spec:
		{{ result = [None,None] }}
		[NUM {{result[0]=int(NUM)}}] OVERLAY_SPEC_SEP [NUM {{result[2]=int(NUM)}}]
		{{ return ('OVERLAY_SPEC', (result[0], result[1])) }}

		
