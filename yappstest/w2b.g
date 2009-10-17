#first sketches for a yapps2 LL(1) grammar for wiki2beamer and some LaTeX

parser wiki2beamer:
	token END:		"$"
	token SPACE:		"[ \\t]+"
	token NEWLINE:		"[\\n\\r]+"
	token NUM:		"[0-9]+"
	token WORD:		"[a-zA-Z]+"
	token PUNCTUATION:	"[,\\.\\?!:;\"'`´]+"
	token MINUS:		"-"
	token COMMA:		","
	token LATEX_COMMAND_NAME: "\\\\([a-zA-Z]+)"
	token BRACKET_CURLY_L:	"{"
	token BRACKET_CURLY_R:	"}"
	token BRACKET_ANGLE_L:	"<"
	token BRACKET_ANGLE_R:	">"
	token BRACKET_SQUARE_L:	"\\["
	token BRACKET_SQUARE_R:	"\\]"
	token W2B_H2_L:		"=="
	token W2B_H2_R:		"=="
	token W2B_H3_L:		"==="
	token W2B_H3_R:		"==="
	token W2B_H4_L:		"===="
	token W2B_H4_R:		"===="
	token W2B_ENDFRAME:	"\\[frame\\]>"
	token OVERLAY_SPEC_SIMPLE: "[0-9-,]+"

	rule document:
		{{ prepend = None }}
		[latex {{ prepend = latex }}]
		w2b_docbody
		END
		{{ return (prepend, w2b_docbody, 'END') }}

	rule w2b_docbody:
		{{ result = [] }}
		(
			w2b_section	{{ result.append(w2b_section) }}
		|	w2b_subsection	{{ result.append(w2b_subsection) }}
		|	w2b_frame	{{ result.append(w2b_frame) }}
		|	w2b_nonframe	{{ result.append(w2b_nonframe) }}
		)*
		{{ return ('W2B_DOCBODY', result) }}
	
	rule w2b_section:
		W2B_H2_L w2b_sectionheader_latex W2B_H2_R NEWLINE
			{{ return ('W2B_SECTION', w2b_sectionheader_latex) }}
	

	rule w2b_subsection:
		W2B_H3_L w2b_subsectionheader_latex W2B_H3_R NEWLINE
			{{ return ('W2B_SUBSECTION', w2b_subsectionheader_latex) }}
		
	rule w2b_frame:
		w2b_frameheader
		latex
		{{ return ('W2B_FRAME', w2b_frameheader, latex) }}

	rule w2b_frameheader:
		W2B_H4_L w2b_frameheader_latex W2B_H4_R NEWLINE
			{{return ('W2B_FRAMEHEADER', (W2B_H4_L, w2b_frameheader_latex, W2B_H4_R)) }}

	rule w2b_nonframe:
		W2B_ENDFRAME NEWLINE
		latex {{ return ('W2B_NONFRAME', latex) }}

	rule w2b_sectionheader_latex:
		{{ result = [] }}
		( latex_entity {{ result.append(latex_entity) }} )*
		{{ return ('LATEX', result) }}

	rule w2b_subsectionheader_latex:
		{{ result = [] }}
		( latex_entity {{ result.append(latex_entity) }} )*
		{{ return ('LATEX', result) }}

	rule w2b_frameheader_latex:
		{{ result = [] }}
		( latex_entity {{ result.append(latex_entity) }} )*
		{{ return ('LATEX', result) }}

	rule latex:
		{{ result = [] }}
		( latex_entity {{ result.append(latex_entity) }} )*
		{{ return ('LATEX', result) }}

	rule latex_entity:
			WORD	{{return ('WORD', WORD)}}
		|	SPACE	{{return ('SPACE', SPACE)}}
		|	PUNCTUATION {{return ('PUNCTUATION', PUNCTUATION)}}
		|	latex_command	{{return latex_command}}
		|	NEWLINE	{{return ('NEWLINE', NEWLINE)}}

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
			{{ return ('LATEX_PARAM_CURLY_BRACKETS', latex) }}

	rule latex_param_square_brackets:
		BRACKET_SQUARE_L latex BRACKET_SQUARE_R
			{{ return ('LATEX_PARAM_SQUARE_BRACKETS', latex) }}
	
	rule latex_param_angle_brackets:
		BRACKET_ANGLE_L overlay_spec BRACKET_ANGLE_R
			{{ return ('LATEX_PARAM_ANGLE_BRACKETS', overlay_spec ) }}
	
	rule overlay_spec:
		OVERLAY_SPEC_SIMPLE
		{{ return ('OVERLAY_SPEC', OVERLAY_SPEC_SIMPLE) }}

		
