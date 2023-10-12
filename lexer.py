# Lexerical Scanner for Assembly
import log
try:
    import ply.lex as lex
except:
    log.error("pyl could not be resolved, try 'pip install ply'")

## TOKENS ###
# List of token names
tokens = (
    'SECTION',
    'DOT',
    'DATA',
    'TEXT',
    'GLOBAL',
    'ID',
    'REGISTER',
    'COMMA',
    'NEWLINE',
    'HEX',
    'DECIMAL',
    'LABEL',
    'COLON',
)

# Regular expressions for simple tokens
# List of token names
tokens = (
    'SECTION',
    'DOT',
    'DATA',
    'TEXT',
    'GLOBAL',
    'ID',
    'REGISTER',
    'COMMA',
    'NEWLINE',
    'HEX',
    'DECIMAL',
    'LABEL',
    'COLON',
)

# Regular expressions for simple tokens
t_DOT = r'\.'
t_COMMA = r','
t_NEWLINE = r'\n'
t_COLON = r':'

# Define a regular expression for hexadecimal numbers
def t_HEX(t):
    r'0[xX][0-9a-fA-F]+'
    t.value = int(t.value, 16)
    return t

# Define a regular expression for decimal numbers
def t_DECIMAL(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Define a regular expression for instructions
def t_SECTION(t):
    r'section'
    return t

def t_GLOBAL(t):
    r'global'
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    return t

# Ignore comments starting with ';'
def t_COMMENT(t):
    r';.*'
    pass

# Ignored characters (spaces and tabs)
t_ignore = ' \t'
##############
def t_error(t):
    log.error("illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


lexer = lex.lex()
###################

def render(data):
    lexer.input(data)
    returnval = []
    while True:
        tok = lexer.token()
        if not tok:
            break
        if tok.type == 'NEWLINE' or tok.type == 'COMMENT':
            continue
        returnval.append({
            'type': tok.type,
            'value': tok.value,
        })
        
    return returnval