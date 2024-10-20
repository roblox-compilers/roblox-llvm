from llvmlite import ir
from llvmlite import binding as llvm
import sys
import re
from strings import *


# Visitor functions
def tokenize(text):
    token_pattern = r'c"[^"]*"|\S+'
    tokens = re.findall(token_pattern, text)
    tokens = [token[1:-1] if token[0] == '"' else token for token in tokens]

    return tokens


def globalvar(op):
    definition = str(op)
    definition = "=".join(
        definition.split("=")[1:]
    )  # Seperate by the =, then remove the stuff before the first equals sign

    for defin in tokenize(definition):
        try:
            int(defin)
            return (int(defin), op.type)
        except:
            pass

        if defin.startswith('c"') and defin.endswith('"'):
            return (defin[1:], op.type)

        if defin == "null":
            return ("nil", op.type)


def valueResolver(op):
    if op.value_kind == llvm.ValueKind.global_variable:
        return globalvar(op)
    if op.name != "":
        arg = op.name.replace(".", "_")
        argType = op.type
    else:
        arg = str(op)  # would be: "i32 %0", so remove the type
        argType = arg.split(" ")[0]
        arg = " ".join(arg.split(" ")[1:])
    return arg, argType


def clean(val):
    if len(val.split(" ")) == 1:
        return (
            val.replace(".", "_")
            .replace(",", "")
            .replace(" ", "")
            .replace("%", "pointer_")
            .replace("*", "_ptr")
        )
    else:
        return "--[[Advanced values are not supported yet]] nil"


def cleanObjects(args):
    return [clean(arg) for arg in args]


def createOverload(type: llvm.TypeKind, val, config):
    if not config.strictOverflowMode:
        return val
    # Use (target + range) % 256 range is 2^8-1 for i8: This is for signed values (not decimal)
    # Use llvm_overload_clamp(target, range) for decimal values
    # Use target % range for unsigned values
    range = 0  # for 8 bit it would be 8^2-1, 16 bit would be 16^2-1, etc.
    style = 0  # 0 = Unsigned, 1 = Clamp, 2 = Modulo
    decimal = 0

    type = str(type)
    # print(type, val)
    if type.startswith("u"):
        style = 0
        decimal = 1
        range = type[1:] + "^2-1"
    elif type.startswith("i"):
        style = 2
        decimal = 1
        range = type[1:] + "^2-1"
    else:
        return val

    # if style == 0:
    #    return val+" % "+str(range)
    # elif style == 1 or style == 2:
    return CLAMP.format(val, str(range), str(decimal))
    # elif style == 2:
    #    return "("+val+" + "+str(range)+") % 256"


# Visitor
class Instructions:
    # Arithmetic
    def add(self, inst, config):
        line = ""
        for op in inst.operands:
            line += valueResolver(op)[0] + " + "
        return VARIABLE_DECL.format(
            valueResolver(inst)[0], createOverload(inst.type, line[:-3], config)
        )

    def sub(self, inst, config):
        line = ""
        for op in inst.operands:
            line += valueResolver(op)[0] + " - "
        return VARIABLE_DECL.format(
            valueResolver(inst)[0], createOverload(inst.type, line[:-3], config)
        )

    def mul(self, inst, config):
        line = ""
        for op in inst.operands:
            line += valueResolver(op)[0] + " * "
        return VARIABLE_DECL.format(
            valueResolver(inst)[0], createOverload(inst.type, line[:-3], config)
        )

    def div(self, inst, config):
        line = ""
        for op in inst.operands:
            line += valueResolver(op)[0] + " / "
        return VARIABLE_DECL.format(
            valueResolver(inst)[0], createOverload(inst.type, line[:-3], config)
        )

    def rem(self, inst, config):
        line = ""
        for op in inst.operands:
            line += valueResolver(op)[0] + " % "
        return VARIABLE_DECL.format(
            valueResolver(inst)[0], createOverload(inst.type, line[:-3], config)
        )

    # Unary
    def neg(self, inst, config):
        return VARIABLE_DECL.format(
            valueResolver(inst)[0], "-" + valueResolver(inst.operands[0])[0]
        )

    # Bitwise Shifts
    def shl(self, inst, config):
        if not config.useBit32:
            return VARIABLE_DECL.format(
                valueResolver(inst)[0],
                valueResolver(inst.operands[0])[0]
                + " << "
                + valueResolver(inst.operands[1])[0],
            )
        else:
            return VARIABLE_DECL.format(
                valueResolver(inst)[0],
                "lshift("
                + valueResolver(inst.operands[0])[0]
                + ", "
                + valueResolver(inst.operands[1])[0]
                + ")",
            )

    def lshr(self, inst, config):
        if not config.useBit32:
            return VARIABLE_DECL.format(
                valueResolver(inst)[0],
                valueResolver(inst.operands[0])[0]
                + " >> "
                + valueResolver(inst.operands[1])[0],
            )
        else:
            return VARIABLE_DECL.format(
                valueResolver(inst)[0],
                "rshift("
                + valueResolver(inst.operands[0])[0]
                + ", "
                + valueResolver(inst.operands[1])[0]
                + ")",
            )

    def ashr(self, inst, config):
        if not config.useBit32:
            return VARIABLE_DECL.format(
                valueResolver(inst)[0],
                valueResolver(inst.operands[0])[0]
                + " >> "
                + valueResolver(inst.operands[1])[0],
            )
        else:
            return VARIABLE_DECL.format(
                valueResolver(inst)[0],
                "arshift("
                + valueResolver(inst.operands[0])[0]
                + ", "
                + valueResolver(inst.operands[1])[0]
                + ")",
            )

    # Bitwise AND, OR, XOR
    def and_(self, inst, config):
        if not config.useBit32:
            return VARIABLE_DECL.format(
                valueResolver(inst)[0],
                valueResolver(inst.operands[0])[0]
                + " & "
                + valueResolver(inst.operands[1])[0],
            )
        else:
            return VARIABLE_DECL.format(
                valueResolver(inst)[0],
                "band("
                + valueResolver(inst.operands[0])[0]
                + ", "
                + valueResolver(inst.operands[1])[0]
                + ")",
            )

    def or_(self, inst, config):
        if not config.useBit32:
            return VARIABLE_DECL.format(
                valueResolver(inst)[0],
                valueResolver(inst.operands[0])[0]
                + " | "
                + valueResolver(inst.operands[1])[0],
            )
        else:
            return VARIABLE_DECL.format(
                valueResolver(inst)[0],
                "bor("
                + valueResolver(inst.operands[0])[0]
                + ", "
                + valueResolver(inst.operands[1])[0]
                + ")",
            )

    def xor(self, inst, config):
        if not config.useBit32:
            return VARIABLE_DECL.format(
                valueResolver(inst)[0],
                valueResolver(inst.operands[0])[0]
                + " ^ "
                + valueResolver(inst.operands[1])[0],
            )
        else:
            return VARIABLE_DECL.format(
                valueResolver(inst)[0],
                "bxor("
                + valueResolver(inst.operands[0])[0]
                + ", "
                + valueResolver(inst.operands[1])[0]
                + ")",
            )

    # Memory
    def alloca(self, inst, config):
        vals = tokenize(valueResolver(inst)[0])
        ptr = clean(vals[0])
        type = clean(vals[3])
        alignment = "nil"
        if len(vals) > 4:
            alignment = clean(vals[5])

        return ALLOC.format(ptr, type, alignment)

    def store(self, inst, config):
        vals = tokenize(valueResolver(inst)[0])
        type = clean(vals[2])
        value = clean(vals[3])
        ptr = clean(vals[4])
        alignment = "nil"
        if len(vals) > 5:
            alignment = clean(vals[6])

        return STORE.format(ptr, value, type, alignment)

    # Control flow
    def ret(self, inst, config):
        line = "return "
        for op in inst.operands:
            arg, argType = valueResolver(op)
            line += createOverload(argType, "".join(arg), config)
            line += ", "
        return line[:-2]

    def call(self, inst, config):
        fname = ""
        args = []
        for ind, op in enumerate(inst.operands):
            if op.value_kind == llvm.ValueKind.function:
                fname = valueResolver(op)[0]
            else:
                arg, argType = valueResolver(op)
                args.append(createOverload(argType, "".join(arg), config))
        if inst.name == "":
            line = fname + "(" + ", ".join(cleanObjects(args)) + ")"
        else:
            line = VARIABLE_DECL.format(
                inst.name.replace(".", "_"),
                fname + "(" + ", ".join(cleanObjects(args)) + ")",
            )
        return line

    def getinst(self, name):
        if hasattr(self, name):  # Instruction exists
            return getattr(self, name)
        elif (
            name.startswith("f") or name.startswith("u") or name.startswith("s")
        ) and hasattr(
            self, name[1:]
        ):  # Does the instruction exist, but optimized for a specific type?
            return getattr(self, name[1:])
        elif hasattr(
            self, name + "_"
        ):  # Instruction exists, but with an underscore (to avoid conflicts with Python keywords)
            return getattr(self, name + "_")

        sys.stderr.write(
            "\033[91;1merror:\033[0m unknown instruction: '" + name + "'\n"
        )
        sys.exit(1)


instructions = Instructions()
