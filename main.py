from llvmlite import ir
from llvmlite import binding as llvm
import llvmlite
import sys
import re

# Flags
def error(msg):
    print("\033[91;1merror:\033[0m " + msg)
VERSION = "0.0.0 beta"

strictOverflowMode = False
useBit32 = True
# Visitor functions
def createOverload(type: llvm.TypeKind, val):
    if not strictOverflowMode:
        return val
    # Use (target + range) % 256 range is 2^8-1 for i8: This is for signed values (not decimal)
    # Use llvm_overload_clamp(target, range) for decimal values
    # Use target % range for unsigned values
    range = 0 # for 8 bit it would be 8^2-1, 16 bit would be 16^2-1, etc.
    style = 0 # 0 = Unsigned, 1 = Clamp, 2 = Modulo
    decimal = 0
    
    type = str(type)
    #print(type, val)
    if type.startswith("u"):
        style = 0
        decimal = 1
        range = type[1:]+"^2-1"
    elif type.startswith("i"):
        style = 2
        decimal = 1
        range = type[1:]+"^2-1"
    else:
        return val


    #if style == 0:
    #    return val+" % "+str(range)
    #elif style == 1 or style == 2:
    return "llvm_overload_clamp("+val+", "+str(range)+", "+str(decimal)+")"
    #elif style == 2:
    #    return "("+val+" + "+str(range)+") % 256"

# Visitor
class Instructions:
    # Arithmetic
    def add(self, inst):
        line = ""
        for op in inst.operands:
            line += op.name + " + "
        return "local " + inst.name + " = "+createOverload(inst.type, line[:-3])
    def sub(self, inst):
        line = ""
        for op in inst.operands:
            line += op.name + " - "
        return "local " + inst.name + " = "+createOverload(inst.type, line[:-3])
    def mul(self, inst):
        line = ""
        for op in inst.operands:
            line += op.name + " * "
        return "local " + inst.name + " = "+createOverload(inst.type, line[:-3])
    def div(self, inst):
        line = ""
        for op in inst.operands:
            line += op.name + " / "
        return "local " + inst.name + " = "+createOverload(inst.type, line[:-3])
    def rem(self, inst):
        line = ""
        for op in inst.operands:
            line += op.name + " % "
        return "local " + inst.name + " = "+createOverload(inst.type, line[:-3])
   
    # Unary
    def neg(self, inst):
        return "local " + inst.name + " = -" + inst.operands[0].name
    
    # Bitwise Shifts
    def shl(self, inst):
        if not useBit32:
            return "local " + inst.name + " = " + inst.operands[0].name + " << " + inst.operands[1].name
        else:
            return "local " + inst.name + " = bit32.lshift(" + inst.operands[0].name + ", " + inst.operands[1].name + ")"
    def lshr(self, inst):
        if not useBit32:
            return "local " + inst.name + " = " + inst.operands[0].name + " >> " + inst.operands[1].name
        else:
            return "local " + inst.name + " = bit32.rshift(" + inst.operands[0].name + ", " + inst.operands[1].name + ")"
    def ashr(self, inst):
        if not useBit32:
            return "local " + inst.name + " = " + inst.operands[0].name + " >> " + inst.operands[1].name
        else:
            return "local " + inst.name + " = bit32.arshift(" + inst.operands[0].name + ", " + inst.operands[1].name + ")"
    
    # Bitwise AND, OR, XOR
    def and_(self, inst):
        if not useBit32:
            return "local " + inst.name + " = " + inst.operands[0].name + " & " + inst.operands[1].name
        else:
            return "local " + inst.name + " = bit32.band(" + inst.operands[0].name + ", " + inst.operands[1].name + ")"
    def or_(self, inst):
        if not useBit32:
            return "local " + inst.name + " = " + inst.operands[0].name + " | " + inst.operands[1].name
        else:
            return "local " + inst.name + " = bit32.bor(" + inst.operands[0].name + ", " + inst.operands[1].name + ")"
    def xor(self, inst):
        if not useBit32:
            return "local " + inst.name + " = " + inst.operands[0].name + " ^ " + inst.operands[1].name
        else:
            return "local " + inst.name + " = bit32.bxor(" + inst.operands[0].name + ", " + inst.operands[1].name + ")"
    
    # Control flow
    def ret(self, inst):
        line = "return "
        for op in inst.operands:
            if op.name != "":
                line += op.name
            else:
                arg = str(op)
                argType = arg.split(" ")[0]
                arg = arg.split(" ")[1:]
                line += createOverload(argType, "".join(arg))
            line += ", "
        return line[:-2]
    def call(self, inst):
        fname = ""
        args = []
        for ind, op in enumerate(inst.operands):
            if op.value_kind == llvm.ValueKind.function:
                fname = op.name
            else:
                if op.name != "":
                    arg = op.name
                    argType = op.type
                else:
                    arg = str(op) # would be: "i32 %0", so remove the type
                    argType = arg.split(" ")[0]
                    arg = arg.split(" ")[1:]
                args.append(createOverload(argType, "".join(arg)))
        if inst.name == "":
            line = fname + "(" + ", ".join(args) + ")"
        else:
            line = "local " + inst.name + " = " + fname + "(" + ", ".join(args) + ")"
        return line

    def __getattr__(self, name): 
        if hasattr(self, name): # Instruction exists
            return getattr(self, name)
        elif (name.startswith("f") or name.startswith("u") or name.startswith("s")) and hasattr(self, name[1:]): # Does the instruction exist, but optimized for a specific type?
            return getattr(self, name[1:])
        elif hasattr(self, name+"_"): # Instruction exists, but with an underscore (to avoid conflicts with Python keywords)
            return getattr(self, name+"_")
        
        sys.stderr.write("\033[91;1merror:\033[0m unknown instruction: '" + name + "'\n")
        sys.exit(1)
instructions = Instructions()


# Entry point
def generateSource(module):
    generatedCode = f"""--!optimize 2
--!nolint
--!nocheck
--!native
--# selene: allow(global_usage, multiple_statements, incorrect_standard_library_use, unused_variable)

-- Generated by roblox-llvm {VERSION}\n"""

    if strictOverflowMode:
        generatedCode += """
function llvm_overload_clamp(target, range, decimal)
    local x = math.clamp(target, -range, range)
    if decimal == 1 then math.floor(x) end
    return if x == range then -range else x
end"""
    for func in module.functions:
        if func.is_declaration:
            generatedCode += "\nif not " + func.name + " then " + func.name + " = _G.llvm_" + func.name + " or error(\"roblox-llvm | function '" + func.name + "' not found\") end"
        else:
            generatedCode += "\nfunction " + func.name + "(" + ", ".join([arg.name for arg in func.arguments]) + ")"
            for block in func.blocks:
                for instruction in block.instructions:
                    generatedCode += "\n    " + instructions.__getattr__(instruction.opcode)(instruction)
            generatedCode += "\nend"
    
    generatedCode += """

return {"""+", ".join([func.name for func in module.functions if not func.is_declaration])  +"}"
    return (generatedCode)

def main():
    # CLI (extracted from qts)
    args = sys.argv[1:]
    flags = []
    inputf = []
    outputf = None
    lookForOutput = False
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
    global strictOverflowMode, useBit32
    strictOverflowMode = "-s" in flags
    useBit32 = "-nb" in flags

    # Generate
    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()
    try:
        llvm_ir_code = open(inputf, "r").read() #IR code
        module = llvm.parse_assembly(llvm_ir_code)
    except:
        llvm_bitcode = open(inputf, "rb").read() #Bitcode
        module = llvm.parse_bitcode(llvm_bitcode)

    with open(outputf, "w") as f:
        f.write(generateSource(module))
        f.close()

if __name__ == "__main__":
    main()