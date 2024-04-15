from llvmlite import ir
from llvmlite import binding as llvm
import llvmlite
import sys
import re
from config import *
import gen

# Entry point
def error(msg):
    print("\033[91;1merror\033[0;30m LLVM roblox-llvm:\033[0m " + msg)

def main():
    # CLI (extracted from qts)
    args = sys.argv[1:]
    flags = []
    inputf = []
    outputf = None
    lookForOutput = False
    config = Config()
    for arg in args:
        if arg == "-o":
            lookForOutput = True
        elif arg == "-v" or arg == "--version":
            print("\033[1;31mroblox-llvm:\033[0m "+VERSION +" | \033[1;30mllvmlite:\033[0m "+llvmlite.__version__ + " | \033[1;30mcopyright:\033[0m Unexex & Roblox Compilers Collection. All rights reserved.")
            sys.exit(0)
        elif arg.startswith("-"):
            flags.append(arg)
        elif lookForOutput:
            outputf = arg
            lookForOutput = False
        else:
            inputf.append(arg)
    if inputf is []:
        error("no input file")
        sys.exit(1)
    elif len(inputf) > 1:
        error("too many input files")
        sys.exit(1)
    else:
        inputf = inputf[0]
    if outputf is None:
        error("no output file")
        sys.exit(1)

    # Flags
    config.strictOverflowMode = "-s" in flags
    config.useBit32 = "-nb" in flags
    config.customBuffer = "-cbuff" in flags
    config.customBit32 = "-cbit" in flags

    # Generate
    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()
    try:
        llvm_ir_code = open(inputf, "r").read() #IR code
        module = llvm.parse_assembly(llvm_ir_code)
    except UnicodeDecodeError:
        llvm_bitcode = open(inputf, "rb").read() #Bitcode
        module = llvm.parse_bitcode(llvm_bitcode)
    except:
        error("failed to read and parse file.")
        sys.exit(1)

    module.verify()
    if llvm.ModulePassManager().run(module): # info that it has been optimized
        print("\033[1;30mllvm-opt:\033[0m module has been optimized")
    with open(outputf, "w") as f:
        f.write(gen.generateSource(module, config))
        f.close()

if __name__ == "__main__":
    main()