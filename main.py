from llvmlite import ir
from llvmlite import binding as llvm
import sys
import re

# Parse
try:
    llvm_ir_code = open(sys.argv[1], "r").read() #IR code
except:
    print("Please provide a source file (in LLVM IR, not bitcode).")
    sys.exit(1)

llvm.initialize()
llvm.initialize_native_target()
llvm.initialize_native_asmprinter()
module = llvm.parse_assembly(llvm_ir_code)

# Visitor
class Instructions:
    def add(self, inst):
        line = "local " + inst.name + " = "
        for op in inst.operands:
            line += op.name + " + "
        return line[:-3]
    def sub(self, inst):
        line = "local " + inst.name + " = "
        for op in inst.operands:
            line += op.name + " - "
        return line[:-3]
    def mul(self, inst):
        line = "local " + inst.name + " = "
        for op in inst.operands:
            line += op.name + " * "
        return line[:-3]
    def sdiv(self, inst):
        line = "local " + inst.name + " = "
        for op in inst.operands:
            line += op.name + " / "
        return line[:-3]
    def srem(self, inst):
        line = "local " + inst.name + " = "
        for op in inst.operands:
            line += op.name + " % "
        return line[:-3]
    def ret(self, inst):
        line = "return "
        for op in inst.operands:
            if op.name != "":
                line += op.name
            else:
                arg = str(op)
                arg = arg.split(" ")[1:]
                line += "".join(arg)
            line += ", "
        return line[:-2]
    def call(self, inst):
        fname = ""
        args = []
        for ind, op in enumerate(inst.operands):
            if op.value_kind == llvm.ValueKind.function:
                fname = op.name
            else:
                arg = str(op) # would be: "i32 %0", so remove the type
                arg = arg.split(" ")[1:]
                args.append("".join(arg))

        line = "local " + inst.name + " = " + fname + "(" + ", ".join(args) + ")"
        return line
    def __getattr__(self, name):
        return lambda inst: f"Unknown instruction: {inst.opcode}"
instructions = Instructions()


def createOverload(type: llvm.TypeKind, val):
    # Use (target + range) % 256 range is 2^8-1 for i8: This is for signed values (not decimal)
    # Use llvm_overload_clamp(target, range) for decimal values
    # Use target % range for unsigned values
    range = 0 # for 8 bit it would be 8^2-1, 16 bit would be 16^2-1, etc.
    style = 0 # 0 = Unsigned, 1 = Clamp, 2 = Modulo
    
    if type.startswith("u"):
        style = 0
        range = type[1:]+"^2-1"
    elif type.startswith("i"):
        style = 1
        range = type[1:]+"^2-1"
    else:
        return val


    if style == 0:
        return val+" % "+str(range)
    elif style == 1:
        return "llvm_overload_clamp("+val+", "+str(range)+")"
    elif style == 2:
        return "("+val+" + "+str(range)+") % 256"
# Generate
generatedCode = """--!optimize 2
--!nolint
--!nocheck
--!native

-- Generated by roblox-llvm 1.0.0 Beta.

function llvm_overload_clamp(target, range)
    local x = math.clamp(target, -range, range)
    return if x == range then -range else x
end"""
for func in module.functions:
    if func.name == "main":
        generatedCode += "\ndo -- main"
    else:
        generatedCode += "\nfunction " + func.name + "(" + ", ".join([arg.name for arg in func.arguments]) + ")"
    for block in func.blocks:
        for instruction in block.instructions:
            generatedCode += "\n    " + instructions.__getattribute__(instruction.opcode)(instruction)
    generatedCode += "\nend"
print(generatedCode)