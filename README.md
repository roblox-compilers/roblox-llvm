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
# Installation:
## Requirements:
- LLVM 14 (not 17!)
- `pip install llvmlite`
- python3
You can install prebuilt binaries from the releases page.
