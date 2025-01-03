from instructions import *
from config import *
from strings import *


def generateSource(module, config):
    generatedCode = HEADER

    if config.strictOverflowMode:
        generatedCode += CLAMP_DEF
    if not config.customBit32:
        generatedCode += "\n" + BIT32 + "\n\n"
    else:
        generatedCode += "\n" + CUSTOM_BIT + "\n\n"

    if config.customBuffer:
        generatedCode += CUSTOM_BUFFER + "\n\n"
    else:
        generatedCode += BUFFER + "\n\n"
    for var in module.global_variables:
        generatedCode += VARIABLE_DECL.format(
            clean(var.name, raw=True), valueResolver(var)[0]
        )
    for func in module.functions:
        if func.is_declaration:
            generatedCode += DECLARATION.format(name=func.name)
        else:
            args = ", ".join([valueResolver(arg)[0] for arg in func.arguments])
            generatedCode += "\n" + FUNC_START.format(clean(func.name, raw=True), args)
            for block in func.blocks:
                for instruction in block.instructions:
                    generatedCode += "\n    " + instructions.getinst(
                        instruction.opcode
                    )(instruction, config)
            generatedCode += "\n" + FUNC_END

    functions = [
        clean(func.name, raw=True)
        for func in module.functions
        if not func.is_declaration
    ]
    variables = [
        clean(var.name, raw=True)
        for var in module.global_variables
        if not var.is_declaration
    ]

    exports = ", ".join([f'["{name}"] = {name}' for name in functions + variables])

    for func in module.functions:
        if not func.is_declaration and func.name == "main":
            generatedCode += RUN
            break
    generatedCode += "\n" + EXPORT.format(exports)
    return generatedCode
