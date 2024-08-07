--!optimize 2
--!nolint
--!nocheck
--!native
--# selene: allow(global_usage, multiple_statements, incorrect_standard_library_use, unused_variable)

-- Generated by roblox-llvm 0.0.0 beta

local lshift = bit32.lshift
local rshift = bit32.rshift
local arshift = bit32.arshift
local band = bit32.band
local bor = bit32.bor
local bxor = bit32.bxor

local _hello = "Hello, World!\00"
function add(a, b)
    local result = a + b
    return result
end
function sub(a, b)
    local result = a - b
    return result
end
function mul(a, b)
    local result = a * b
    return result
end
function div(a, b)
    local result = a / b
    return result
end
function mod(a, b)
    local result = a % b
    return result
end
if not print then print = _G.llvm_print or error("roblox-llvm | function 'print' not found") end
function main()
    print()
    return 0
end

return {add, sub, mul, div, mod, main, _hello}
