from llvmlite import ir
from llvmlite import binding as llvm
import sys

# Visitor functions
def createOverload(type: llvm.TypeKind, val, config):
    if not config.strictOverflowMode:
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
    def add(self, inst, config):
        line = ""
        for op in inst.operands:
            line += op.name + " + "
        return "local " + inst.name + " = "+createOverload(inst.type, line[:-3], config)
    def sub(self, inst, config):
        line = ""
        for op in inst.operands:
            line += op.name + " - "
        return "local " + inst.name + " = "+createOverload(inst.type, line[:-3], config)
    def mul(self, inst, config):
        line = ""
        for op in inst.operands:
            line += op.name + " * "
        return "local " + inst.name + " = "+createOverload(inst.type, line[:-3], config)
    def div(self, inst, config):
        line = ""
        for op in inst.operands:
            line += op.name + " / "
        return "local " + inst.name + " = "+createOverload(inst.type, line[:-3], config)
    def rem(self, inst, config):
        line = ""
        for op in inst.operands:
            line += op.name + " % "
        return "local " + inst.name + " = "+createOverload(inst.type, line[:-3], config)
   
    # Unary
    def neg(self, inst, config):
        return "local " + inst.name + " = -" + inst.operands[0].name
    
    # Bitwise Shifts
    def shl(self, inst, config):
        if not config.useBit32:
            return "local " + inst.name + " = " + inst.operands[0].name + " << " + inst.operands[1].name
        else:
            return "local " + inst.name + " = lshift(" + inst.operands[0].name + ", " + inst.operands[1].name + ")"
    def lshr(self, inst, config):
        if not config.useBit32:
            return "local " + inst.name + " = " + inst.operands[0].name + " >> " + inst.operands[1].name
        else:
            return "local " + inst.name + " = rshift(" + inst.operands[0].name + ", " + inst.operands[1].name + ")"
    def ashr(self, inst, config):
        if not config.useBit32:
            return "local " + inst.name + " = " + inst.operands[0].name + " >> " + inst.operands[1].name
        else:
            return "local " + inst.name + " = arshift(" + inst.operands[0].name + ", " + inst.operands[1].name + ")"
    
    # Bitwise AND, OR, XOR
    def and_(self, inst, config):
        if not config.useBit32:
            return "local " + inst.name + " = " + inst.operands[0].name + " & " + inst.operands[1].name
        else:
            return "local " + inst.name + " = band(" + inst.operands[0].name + ", " + inst.operands[1].name + ")"
    def or_(self, inst, config):
        if not config.useBit32:
            return "local " + inst.name + " = " + inst.operands[0].name + " | " + inst.operands[1].name
        else:
            return "local " + inst.name + " = bor(" + inst.operands[0].name + ", " + inst.operands[1].name + ")"
    def xor(self, inst, config):
        if not config.useBit32:
            return "local " + inst.name + " = " + inst.operands[0].name + " ^ " + inst.operands[1].name
        else:
            return "local " + inst.name + " = bxor(" + inst.operands[0].name + ", " + inst.operands[1].name + ")"
    
    # Control flow
    def ret(self, inst, config):
        line = "return "
        for op in inst.operands:
            if op.name != "":
                line += op.name
            else:
                arg = str(op)
                argType = arg.split(" ")[0]
                arg = arg.split(" ")[1:]
                line += createOverload(argType, "".join(arg), config)
            line += ", "
        return line[:-2]
    def call(self, inst, config):
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
                args.append(createOverload(argType, "".join(arg), config))
        if inst.name == "":
            line = fname + "(" + ", ".join(args) + ")"
        else:
            line = "local " + inst.name + " = " + fname + "(" + ", ".join(args) + ")"
        return line

    def getinst(self, name): 
        if hasattr(self, name): # Instruction exists
            return getattr(self, name)
        elif (name.startswith("f") or name.startswith("u") or name.startswith("s")) and hasattr(self, name[1:]): # Does the instruction exist, but optimized for a specific type?
            return getattr(self, name[1:])
        elif hasattr(self, name+"_"): # Instruction exists, but with an underscore (to avoid conflicts with Python keywords)
            return getattr(self, name+"_")
        
        sys.stderr.write("\033[91;1merror:\033[0m unknown instruction: '" + name + "'\n")
        sys.exit(1)
instructions = Instructions()
