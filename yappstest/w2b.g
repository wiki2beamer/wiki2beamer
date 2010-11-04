#first sketches for a yapps2 LL(1) grammar for wiki2beamer and some LaTeX

parser wiki2beamer:
	token END:		"$"
	token SPACE:		"[ \\t]+"
	token NEWLINE:		"\\r?\\n"
	token PARBREAK:		"(\\r?\\n|^)((\\r?\\n)+)"
	token NUM:		"[0-9]+"
	token WORD:		"[a-zA-Z]+"
	token PUNCTUATION:	"(,|\\.|\\?|:|;|\"|'|`|´|\\\\[|\\\\]|\\\\<|\\\\>)+"
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
	token OVERLAY_SPEC_SIMPLE: "[0-9-, \\t]+"
	token W2B_UL:		"\\*"
	token W2B_OL:		"#"
	token W2B_ESC_EXCLM:	"\\\\!"
	token W2B_ALERT_L:	"!"
	token W2B_ALERT_R:	"!"
	token W2B_ALERT_IN:	"[^!\\r\\n]*"
	token W2B_BOLD_L:	"'''"
	token W2B_BOLD_R:	"'''"
	token W2B_BOLD_IN:	"[^'\\r\\n]*"
	token W2B_ITALIC_L:	"''"
	token W2B_ITALIC_R:	"''"
	token W2B_ITALIC_IN:	"[^'\\r\\n]*"
	token W2B_ESC_AT:	"\\\\@"
	token W2B_TEXTTT_L:	"@"
	token W2B_TEXTTT_R:	"@"
	token W2B_TEXTTT_IN:	"[^@\\r\\n]*"
	token W2B_TEXTCOLOR_L:		"_"
	token W2B_TEXTCOLOR_COLOR:	"[^_\\r\\n]*"
	token W2B_TEXTCOLOR_MID:	"_"
	token W2B_TEXTCOLOR_IN:		"[^_\\r\\n]*"
	token W2B_TEXTCOLOR_R:		"_"

	token W2B_VSPACE_L:	"--"
	token W2B_VSPACE_R:	"--"
	token W2B_VSPACE_IN:	"[^-\\r\\n]*"
	token W2B_VSPACESTAR_L:	"--\\*"

	token W2B_ENV_NAME:	"[a-zA-Z]+"
	token W2B_ENV_OPEN_L:	"<\\["
	token W2B_ENV_OPEN_R:	"\\]"
	token W2B_ENV_CLOSE_L:	"\\["
	token W2B_ENV_CLOSE_R:	"\\]>"

	token W2B_AUTOTEMPLATE_OPEN:	"<\\[[ \\t]*autotemplate[ \\t]*\\]"
	token W2B_AUTOTEMPLATE_CLOSE:	"\\[[ \\t]*autotemplate[ \\t]*\\]>"
	token W2B_AUTOTEMPLATE_IN:	"[\\n\\r\\sa-zA-Z]*" #TODO far from complete

	token W2B_NOWIKI_OPEN:	"<\\[[ \\t]*nowiki[ \\t]*\\]"
	token W2B_NOWIKI_CLOSE:	"\\[[ \\t]*nowiki[ \\t]*\\]>"
	token W2B_NOWIKI_IN:	"(\\\\<|\\\\>|\\\\\\[|\\\\\\]|[^\\[\\]<>])*" #TODO document escaping




	rule document:
		{{ result = [] }}
		#[[(SPACE|NEWLINE)*] w2b_autotemplate {{result.append(w2b_autotemplate)}}]
		(
			PARBREAK	{{result.append(('PARBREAK', PARBREAK))}}
		|	paragraph	{{result.append(paragraph)}}
		)*
		END {{result.append(('END',))}}
		{{return result}}
		
	
	rule paragraph:
		{{result = None}}
		(
			w2b_textblock	{{result = w2b_textblock}}
		|	w2b_listblock	{{result = w2b_listblock}}
		)
		{{return ('PARAGRAPH', result)}}
	
	rule w2b_nowiki:
		W2B_NOWIKI_OPEN W2B_NOWIKI_IN W2B_NOWIKI_CLOSE
		{{return ('W2B_NOWIKI', W2B_NOWIKI_IN)}}

	#TODO replace W2B_AUTOTEMPLATE_IN with a ruleset	
	rule w2b_autotemplate:
		W2B_AUTOTEMPLATE_OPEN W2B_AUTOTEMPLATE_IN W2B_AUTOTEMPLATE_CLOSE
		{{return ('AUTOTEMPLATE', W2B_AUTOTEMPLATE_IN)}}

	rule w2b_textblock:
		{{result = []}}
		(
			w2b_single_line {{result.append(w2b_single_line)}}
			[NEWLINE {{result.append(('NEWLINE', NEWLINE))}}]
		)
		(
			w2b_single_line {{result.append(w2b_single_line)}}
			[NEWLINE {{result.append(('NEWLINE', NEWLINE))}}]
		)*
		{{return ('W2B_TEXTBLOCK', result)}}

	rule w2b_listblock:
		{{ result = [] }}
		(W2B_UL {{result.append(('W2B_UL', W2B_UL))}} | W2B_OL {{result.append(('W2B_OL', W2B_OL))}})
		(
			(W2B_UL {{result.append(('W2B_UL', W2B_UL))}} | W2B_OL {{result.append(('W2B_OL', W2B_OL))}})*
			[overlay_spec {{result.append(overlay_spec)}}]
			SPACE	{{result.append(('SPACE', SPACE))}}
			w2b_single_line {{result.append(w2b_single_line)}}
			[
				NEWLINE {{result.append(('NEWLINE', NEWLINE))}}
				(W2B_UL {{result.append(('W2B_UL', W2B_UL))}}
			|	W2B_OL {{result.append(('W2B_OL', W2B_OL))}})
			]
		)*
		{{ return ('W2B_LIST_BLOCK', result) }}

	rule w2b_single_line:
		{{ result = [] }}
		(
			WORD			{{result.append(('WORD', WORD))}}
		|	NUM			{{result.append(('NUM', NUM))}}
		|	SPACE			{{result.append(('SPACE', SPACE))}}
		|	w2b_escape_seq		{{result.append(w2b_escape_seq)}}
		|	w2b_text_alert		{{result.append(w2b_text_alert)}}
		|	w2b_text_bold		{{result.append(w2b_text_bold)}}
		|	w2b_text_italic		{{result.append(w2b_text_italic)}}
		|	w2b_text_texttt		{{result.append(w2b_text_texttt)}}
		|	w2b_text_textcolor	{{result.append(w2b_text_textcolor)}}
		|	w2b_vspace		{{result.append(w2b_vspace)}}
		|	w2b_vspacestar		{{result.append(w2b_vspacestar)}}
		|	w2b_env_open		{{result.append(w2b_env_open)}}
		|	w2b_env_close		{{result.append(w2b_env_close)}}
		|	w2b_nowiki		{{result.append(w2b_nowiki)}}
		|	PUNCTUATION		{{result.append(('PUNCTUATION', PUNCTUATION))}}
		)
		(
			WORD			{{result.append(('WORD', WORD))}}
		|	NUM			{{result.append(('NUM', NUM))}}
		|	SPACE			{{result.append(('SPACE', SPACE))}}
		|	w2b_escape_seq		{{result.append(w2b_escape_seq)}}
		|	w2b_text_alert		{{result.append(w2b_text_alert)}}
		|	w2b_text_bold		{{result.append(w2b_text_bold)}}
		|	w2b_text_italic		{{result.append(w2b_text_italic)}}
		|	w2b_text_texttt		{{result.append(w2b_text_texttt)}}
		|	w2b_text_textcolor	{{result.append(w2b_text_textcolor)}}
		|	w2b_vspace		{{result.append(w2b_vspace)}}
		|	w2b_vspacestar		{{result.append(w2b_vspacestar)}}
		|	w2b_env_open		{{result.append(w2b_env_open)}}
		|	w2b_env_close		{{result.append(w2b_env_close)}}
		|	w2b_nowiki		{{result.append(w2b_nowiki)}}
		|	PUNCTUATION		{{result.append(('PUNCTUATION', PUNCTUATION))}}
		)*
		{{return ('W2B_SINGLE_LINE', result)}}

	#TODO hack environment open/close matching outside of the grammar (graph-transformation?)
	rule w2b_env_open:
		W2B_ENV_OPEN_L [SPACE] W2B_ENV_NAME [SPACE] W2B_ENV_OPEN_R
		{{return ('W2B_ENV_OPEN', W2B_ENV_NAME) }}
		
	rule w2b_env_close:
		W2B_ENV_CLOSE_L [SPACE] W2B_ENV_NAME [SPACE] W2B_ENV_CLOSE_R
		{{return ('W2B_ENV_CLOSE', W2B_ENV_NAME) }}
	
	rule w2b_escape_seq:
		{{ result = None }}
		(
			W2B_ESC_AT	{{result = ('W2B_ESC_AT', W2B_ESC_AT) }}
		|	W2B_ESC_EXCLM	{{result = ('W2B_ESC_EXCLM', W2B_ESC_EXCLM) }}
		)
		{{ return result }}
	
	#TODO hack parsing of typesetting contents outside of the grammar
	rule w2b_text_alert:
		W2B_ALERT_L W2B_ALERT_IN W2B_ALERT_R
		{{ return ('W2B_ALERT', W2B_ALERT_IN) }}

	rule w2b_text_bold:
		W2B_BOLD_L W2B_BOLD_IN W2B_BOLD_R
		{{ return ('W2B_BOLD', W2B_BOLD_IN) }}

	rule w2b_text_italic:
		W2B_ITALIC_L W2B_ITALIC_IN W2B_ITALIC_R
		{{ return ('W2B_ITALIC', W2B_ITALIC_IN) }}

	rule w2b_text_texttt:
		W2B_TEXTTT_L W2B_TEXTTT_IN W2B_TEXTTT_R
		{{ return ('W2B_TEXTTT', W2B_TEXTTT_IN) }}

	rule w2b_text_textcolor:
		W2B_TEXTCOLOR_L W2B_TEXTCOLOR_COLOR W2B_TEXTCOLOR_MID W2B_TEXTCOLOR_IN W2B_TEXTCOLOR_R
		{{return ('W2B_TEXTCOLOR', W2B_TEXTCOLOR_COLOR, W2B_TEXTCOLOR_IN)}}
	
	rule w2b_vspace:
		W2B_VSPACE_L W2B_VSPACE_IN W2B_VSPACE_R
		{{ return ('W2B_VSPACE', W2B_VSPACE_IN) }}
	
	rule w2b_vspacestar:
		W2B_VSPACESTAR_L W2B_VSPACE_IN W2B_VSPACE_R
		{{ return ('W2B_VSPACESTAR', W2B_VSPACE_IN) }}

	rule overlay_spec:
		BRACKET_ANGLE_L OVERLAY_SPEC_SIMPLE BRACKET_ANGLE_R
		{{return ('OVERLAY_SPEC', OVERLAY_SPEC_SIMPLE)}}
