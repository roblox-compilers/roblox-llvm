from config import *

HEADER = f"""--!optimize 2
--!nolint
--!nocheck
--!native
--# selene: allow(global_usage, multiple_statements, incorrect_standard_library_use, unused_variable)

-- Generated by roblox-llvm {VERSION}"""
CLAMP_DEF = """function llvm_overload_clamp(target, range, decimal)
    local x = math.clamp(target, -range, range)
    if decimal == 1 then math.floor(x) end
    return if x == range then -range else x
end"""
BIT32 = """local lshift = bit32.lshift
local rshift = bit32.rshift
local arshift = bit32.arshift
local band = bit32.band
local bor = bit32.bor
local bxor = bit32.bxor"""
CUSTOM_BIT = """local lshift = _G.llvm_lshift or error("roblox-llvm | function 'lshift' not found (disable -cbit flag to use the default implementation)")
local rshift = _G.llvm_rshift or error("roblox-llvm | function 'rshift' not found (disable -cbit flag to use the default implementation)")
local arshift = _G.llvm_arshift or error("roblox-llvm | function 'arshift' not found (disable -cbit flag to use the default implementation)")
local band = _G.llvm_band or error("roblox-llvm | function 'band' not found (disable -cbit flag to use the default implementation)")
local bor = _G.llvm_bor or error("roblox-llvm | function 'bor' not found (disable -cbit flag to use the default implementation)")
local bxor = _G.llvm_bxor or error("roblox-llvm | function 'bxor' not found (disable -cbit flag to use the default implementation)")"""
CUSTOM_BUFFER = 'local buffer = _G.llvm_buffer or error("roblox-llvm | function \'buffer\' not found (disable -cbuff flag to use the default implementation)")'
VARIABLE_DECL = "local {} = {}"
FUNC_START = "function {}({})"
FUNC_END = "end"
RUN = """
if script:IsA("BaseScript") then
    main()
end
"""
EXPORT = "return {{{}}}"
CLAMP = "llvm_overload_clamp({}, {}, {})"
DECLARATION = "\nif not {name} then {name} = _G.llvm_{name} or error(\"roblox-llvm | function '{name}' not found\") end"