

" Syntax file for Carbon Script

if exists("b:current_syntax")
  finish
endif

" Keyword groups
syntax keyword carbonKeyword end func set const let fi elsefi default repeat do return iteration RULE
syntax keyword carbonBuiltin varlist funclist clear 
syntax keyword carbonFunction increm decrem rand numceil stdout stdin
syntax keyword carbonPredefined errorlevel uname version pi eu 

" Highlight variables prefixed with "?"
syntax match carbonVariable /?[_a-zA-Z][_a-zA-Z0-9]*/

" Highlight semicolons (without worrying about what follows)
syntax match carbonSemicolon /;/

" Type definitions
syntax match carbonType /;\(int\|str\|flt\|arr\|void\|bool\)/ contains=carbonTypeDelimiter
syntax match carbonTypeDelimiter /;/ contained

" In your highlight group section:
hi def link carbonType Type
hi def link carbonTypeDelimiter Delimiter

" Numbers
syntax match carbonNumber /\<\d\+\>/

" Strings
syntax region carbonString start=+"+ skip=+\\"+ end=+"+

" Operators
syntax match carbonOperator /[+*\/-]/
syntax match carbonComparison /[<>!=]=\|[<>]/

" Comments
syntax match carbonComment /\/\/.*/

" Braces, brackets, parentheses
syntax match carbonBraces /[{}]/
syntax match carbonBrackets /[\[\]]/
syntax match carbonParens /[()]/

" Add to your highlight group section:
hi def link carbonBraces Delimiter
hi def link carbonBrackets Delimiter
hi def link carbonParens Delimiter

" Function variables with types
syntax match carbonFuncVar /\$[_a-zA-Z][_a-zA-Z0-9]*\(;int\|;str\|;flt\|;arr\|;void\)\?/ contains=carbonTypeDelimiter,carbonType

" Function calls starting with @
syntax match carbonFunctionCall /@[_a-zA-Z][_a-zA-Z0-9]*/

" Highlighting True and False as green and red
syntax keyword carbonTrue True
syntax keyword carbonFalse False

" Highlight groups
hi def link carbonKeyword Keyword
hi def link carbonBuiltin Constant
hi def link carbonFunction Function
hi def link carbonPredefined Identifier
hi def link carbonVariable Identifier
hi def link carbonNumber Number
hi def link carbonString String
hi def link carbonOperator Operator
hi def link carbonComparison Operator
hi def link carbonComment Comment
hi def link carbonSemicolon Statement
hi def link carbonBraces Special
hi def link carbonBrackets Structure
hi def link carbonParens Delimiter
hi def link carbonFuncVar Identifier
hi def link carbonFunctionCall Function
hi def link carbonTrue Constant
hi def link carbonFalse Constant




let b:current_syntax = "carbon"

