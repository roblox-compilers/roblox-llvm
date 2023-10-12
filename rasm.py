import log, sys, lexer

# read args
args = sys.argv[1:]
flags = []
inputf = None
outputf = None

lookForOutput = False

if args == []:
    log.error("no arguments")
    sys.exit(1)
    
for arg in args:
    if arg == "-o":
        lookForOutput = True
    elif arg.startswith("-"):
        flags.append(arg)
    elif inputf is None:
        inputf = arg
    elif lookForOutput:
        outputf = arg
        lookForOutput = False
    else:
        log.error("too many arguments")
        sys.exit(1)

if inputf == None:
    log.error("no input file")
    sys.exit(1)
if outputf == None:
    log.error("no output file")
    sys.exit(1)

contents = open(inputf).read()
tree = lexer.render(contents)
del contents
for tok in tree:
    print (tok)
    