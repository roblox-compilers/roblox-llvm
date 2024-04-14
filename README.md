# roblox-llvm
This is a project to compile LLVM IR to Roblox Luau. 

## Usage:
```bash
$ rbxllc <input.ll> -o <output.lua>
```
## Flags:
- `-o <output.lua>`: Output file
- `-v` or `--version`: Print version information
- `-s`: generate code that is buffer-overflow strict. <sub>This will make the generated code slower, larger, and less readable but can fix programs that depend on buffer overflow behavior.</sub>