#first sketches for a yapps2 LL(1) grammar for wiki2beamer and some LaTeX

#The resulting syntax tree is supposed to be a lossless representation of the parsing paths.
#Every production rule is supposed to return with a tuple ('name_of_rule', [ contents ] ).
#Every token is supposed to return as a tuple ('TOKEN_NAME', token_content).
#It should be possible to reconstruct the original parser input from the syntax tree.
#The parser/scanner is supposed to work on unicode input, not in str input. Thus all
#tokens should be unicode regular expressions (starting with "(?u)"). 

#DONE:
# - lists
# - environment matching

#TODO:
# - utf8 input / unicode parsing
# - environment options
# - escaping
# - nowiki
# - code
# - typesetting
# - autotemplate
# - frames
# - sectioning

def match_env(tokenname, env_in, env_body, env_out):
	if env_in[1][1] != env_out[1][1]:
		raise SyntaxError('Opened environment %s doesn\'t match closed environment %s.' % (env_in[1][1], env_out[1][1]))
		return None
	
	return (tokenname, [env_in, env_body, env_out])

%%

parser wiki2beamer:
	token END:		"$"
	token SPACE:		"(?u)[ \\t]+"
	token NEWLINE:		"(?u)\\r?\\n"
	token PARBREAK:		"(?u)\\r?\\n\\r?\\n"
	token NUM:		"(?u)[0-9]+"
	token WORD:		"(?u)\\w+"
	token PUNCT:		"(?u)(,|\\.|\\?|:|;|\"|'|`|´)+"
	token PUNCT_SPECIAL:	"(?u)[*#<>\\-]"
	token MINUS:		"(?u)-"
	token COMMA:		"(?u),"
	token LATEX_COMMAND_NAME: "(?u)\\\\([a-zA-Z]+)"
	token BRACKET_CURLY_L:	"(?u){"
	token BRACKET_CURLY_R:	"(?u)}"
	token BRACKET_ANGLE_L:	"(?u)<"
	token BRACKET_ANGLE_R:	"(?u)>"
	token BRACKET_SQUARE_L:	"(?u)\\["
	token BRACKET_SQUARE_R:	"(?u)\\]"
	token W2B_H2_L:		"(?u)=="
	token W2B_H2_R:		"(?u)=="
	token W2B_H3_L:		"(?u)==="
	token W2B_H3_R:		"(?u)==="
	token W2B_H4_L:		"(?u)===="
	token W2B_H4_R:		"(?u)===="
	token W2B_ENDFRAME:	"(?u)\\[frame\\]>"
	token OVERLAY_SPEC_SIMPLE: "(?u)[0-9-, \\t]+"
	token W2B_LISTBLOCK_BEGIN: "(?u)\\r?\\n?[\\*#]+"
	token W2B_ESC_EXCLM:	"(?u)\\\\!"
	token W2B_ALERT_L:	"(?u)!"
	token W2B_ALERT_R:	"(?u)!"
	token W2B_ALERT_IN:	"(?u)[^!\\r\\n]*"
	token W2B_BOLD_L:	"(?u)'''"
	token W2B_BOLD_R:	"(?u)'''"
	token W2B_BOLD_IN:	"(?u)[^'\\r\\n]*"
	token W2B_ITALIC_L:	"(?u)''"
	token W2B_ITALIC_R:	"(?u)''"
	token W2B_ITALIC_IN:	"(?u)[^'\\r\\n]*"
	token W2B_ESC_AT:	"(?u)\\\\@"
	token W2B_TEXTTT_L:	"(?u)@"
	token W2B_TEXTTT_R:	"(?u)@"
	token W2B_TEXTTT_IN:	"(?u)[^@\\r\\n]*"
	token W2B_TEXTCOLOR_L:		"(?u)_"
	token W2B_TEXTCOLOR_COLOR:	"(?u)[^_\\r\\n]*"
	token W2B_TEXTCOLOR_MID:	"(?u)_"
	token W2B_TEXTCOLOR_IN:		"(?u)[^_\\r\\n]*"
	token W2B_TEXTCOLOR_R:		"(?u)_"

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
		par_set {{ result.append(par_set) }}
		END {{result.append(('END',))}}
		{{return result}}
		
	rule par_set:
		{{ result = [] }}
		[ NEWLINE {{ result.append(('NEWLINE', NEWLINE)) }} ]
		(
			par_break	{{ result.append(par_break) }}
		|	par		{{ result.append(par) }}
		|	w2b_env_multi_line {{ result.append(w2b_env_multi_line) }}
		)+
		[ NEWLINE {{ result.append(('NEWLINE', NEWLINE)) }} ]
		{{ return ('par_set', result) }}
	
	rule par_break:
		{{ result = [] }}
		PARBREAK {{ result.append(('PARBREAK', PARBREAK)) }}
		(
			NEWLINE {{ result.append(('NEWLINE', NEWLINE)) }}
		)*
		{{ return ('par_break', result) }}
		
	rule par:
		{{result = None}}
		(
			w2b_textblock	  {{ result = w2b_textblock }}
		|	w2b_listblock	  {{ result = w2b_listblock }}
		)
		{{return ('par', result)}}
	
	rule w2b_env_multi_line:
		{{ env_params = [] }}
		w2b_env_open  {{ env_params.append(w2b_env_open)  }}
		par_set       {{ env_params.append(par_set) }}
		w2b_env_close {{ env_params.append(w2b_env_close) }}
		{{ return match_env('w2b_env_multi_line', env_params[0], env_params[1], env_params[2]) }}

	rule w2b_env_open:
		W2B_ENV_OPEN_L W2B_ENV_NAME W2B_ENV_OPEN_R
		{{return ('w2b_env_open', [W2B_ENV_OPEN_L, W2B_ENV_NAME, W2B_ENV_OPEN_R] ) }}
		
	rule w2b_env_close:
		W2B_ENV_CLOSE_L W2B_ENV_NAME W2B_ENV_CLOSE_R
		{{return ('w2b_env_close', [W2B_ENV_CLOSE_L, W2B_ENV_NAME, W2B_ENV_CLOSE_R] ) }}
	
	rule w2b_nowiki:
		W2B_NOWIKI_OPEN W2B_NOWIKI_IN W2B_NOWIKI_CLOSE
		{{return ('W2B_NOWIKI', W2B_NOWIKI_IN)}}

	#TODO replace W2B_AUTOTEMPLATE_IN with a production rule
	rule w2b_autotemplate:
		W2B_AUTOTEMPLATE_OPEN W2B_AUTOTEMPLATE_IN W2B_AUTOTEMPLATE_CLOSE
		{{return ('AUTOTEMPLATE', W2B_AUTOTEMPLATE_IN)}}

	rule w2b_textblock:
		{{result = []}}
		(
			w2b_single_line {{result.append(w2b_single_line)}}
			[NEWLINE {{result.append(('NEWLINE', NEWLINE))}}]
		)+
		{{return ('w2b_textblock', result)}}

	rule w2b_listblock:
		{{ result = [] }}
		(
			w2b_listitem {{ result.append(w2b_listitem) }}
		)+
		{{ return ('w2b_listblock', result) }}
	
	rule w2b_listitem:
		{{ result = [] }}
		(
			W2B_LISTBLOCK_BEGIN {{ result.append(('W2B_LISTBLOCK_BEGIN', W2B_LISTBLOCK_BEGIN)) }}
			[ overlay_spec {{ result.append(overlay_spec) }} ]
			[ SPACE {{ result.append(('SPACE', SPACE)) }} ]
			[ w2b_single_line_with_env {{ result.append( w2b_single_line_with_env ) }} ]
		)
		{{ return ('w2b_listitem', result) }}
		
	rule w2b_single_line:
		{{ result = [] }}
		(
			w2b_single_line_simple {{ result.append(w2b_single_line_simple) }}
			[ PUNCT_SPECIAL {{ result.append(('PUNCT_SPECIAL', PUNCT_SPECIAL)) }} ]
		)+

		{{return ('w2b_single_line', result)}}
	
	rule w2b_single_line_simple:
		{{ result = [] }}
		(
			WORD			{{ result.append(('WORD', WORD)) }}
		|	NUM			{{ result.append(('NUM', NUM)) }}
		|	SPACE			{{ result.append(('SPACE', SPACE)) }}
		|	w2b_escape_seq		{{ result.append(w2b_escape_seq) }}
		|	w2b_text_alert		{{ result.append(w2b_text_alert) }}
		|	w2b_text_bold		{{ result.append(w2b_text_bold) }}
		|	w2b_text_italic		{{ result.append(w2b_text_italic) }}
		|	w2b_text_texttt		{{ result.append(w2b_text_texttt) }}
		|	w2b_text_textcolor	{{ result.append(w2b_text_textcolor) }}
		|	w2b_vspace		{{ result.append(w2b_vspace) }}
		|	w2b_vspacestar		{{ result.append(w2b_vspacestar) }}
		|	PUNCT			{{ result.append(('PUNCT', PUNCT)) }}
		)+
		{{return ('w2b_single_line_simple', result)}}
	
	rule w2b_single_line_with_env:
		{{ result = [] }}
		(
			w2b_single_line     {{ result.append(w2b_single_line) }}
		|	w2b_env_single_line {{ result.append(w2b_env_single_line) }}
		)+
		{{ return ('w2b_single_line_with_env', result) }}

	rule w2b_env_single_line:
		{{ env_params = [] }}
		w2b_env_open  {{ env_params.append(w2b_env_open)  }}
		w2b_single_line  {{ env_params.append(w2b_single_line) }}
		w2b_env_close {{ env_params.append(w2b_env_close) }}
		{{ return match_env('w2b_env_single_line', env_params[0], env_params[1], env_params[2]) }}

	rule w2b_escape_seq:
		{{ result = None }}
		(
			W2B_ESC_AT	{{result = ('W2B_ESC_AT', W2B_ESC_AT) }}
		|	W2B_ESC_EXCLM	{{result = ('W2B_ESC_EXCLM', W2B_ESC_EXCLM) }}
		)
		{{ return result }}
	
	#TODO parsing of typesetting contents
	rule w2b_text_alert:
		W2B_ALERT_L W2B_ALERT_IN W2B_ALERT_R
		{{ return ('w2b_text_alert', W2B_ALERT_IN) }}

	rule w2b_text_bold:
		W2B_BOLD_L W2B_BOLD_IN W2B_BOLD_R
		{{ return ('w2b_text_bold', W2B_BOLD_IN) }}

	rule w2b_text_italic:
		W2B_ITALIC_L W2B_ITALIC_IN W2B_ITALIC_R
		{{ return ('w2b_text_italic', W2B_ITALIC_IN) }}

	rule w2b_text_texttt:
		W2B_TEXTTT_L W2B_TEXTTT_IN W2B_TEXTTT_R
		{{ return ('w2b_text_texttt', W2B_TEXTTT_IN) }}

	rule w2b_text_textcolor:
		W2B_TEXTCOLOR_L W2B_TEXTCOLOR_COLOR W2B_TEXTCOLOR_MID W2B_TEXTCOLOR_IN W2B_TEXTCOLOR_R
		{{return ('w2b_text_textcolor', W2B_TEXTCOLOR_COLOR, W2B_TEXTCOLOR_IN)}}
	
	rule w2b_vspace:
		W2B_VSPACE_L W2B_VSPACE_IN W2B_VSPACE_R
		{{ return ('w2b_vspace', W2B_VSPACE_IN) }}
	
	rule w2b_vspacestar:
		W2B_VSPACESTAR_L W2B_VSPACE_IN W2B_VSPACE_R
		{{ return ('w2b_vspacestar', W2B_VSPACE_IN) }}

	rule overlay_spec:
		BRACKET_ANGLE_L OVERLAY_SPEC_SIMPLE BRACKET_ANGLE_R
		{{return ('overlay_spec', [BRACKET_ANGLE_L, OVERLAY_SPEC_SIMPLE, BRACKET_ANGLE_R] ) }}
