# roblox-llvm
This is a project to compile LLVM IR to Roblox Luau. 

# Example:
## Usage:
```bash
$ rbxllc <input.ll> -o <output.lua>
```
## Flags:
- `-o <output.lua>`: Output file
- `-v` or `--version`: Print version information
- `-s`: generate code that is buffer-overflow strict. <sub>This will make the generated code slower, larger, and less readable but can fix programs that depend on buffer overflow behavior.</sub>
- `-nb`: do not use the `bit32` library. <sub>Reccomended for non-luau ecosystems.</sub>
- `-cbuf`: generated code will declare functions from the Luau `buffer` library to be resolved. <sub>Reccomended for non-luau ecosystems.</sub>
- `-cbit`: generated code will declare functions from the Luau `bit32` library to be resolved. <sub>Reccomended for non-luau ecosystems.</sub>
# Installation:
## Requirements:
- LLVM 14 (not 17!)
- `pip install llvmlite`
- python3
You can install prebuilt binaries from the releases page.

# Using the example:
1. Compile test.c to test.ll using clang:
```bash
$ clang -S -emit-llvm test/test.c -o test/test.ll
```
2. Compile test.ll to test.lua using rbxllc:
```bash
$ rbxllc test/test.ll -o test/test.lua
```
3. Run test.lua using luau:
```bash
$ luau test.lua
Hello, World!
```
