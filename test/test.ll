@.hello = constant [14 x i8] c"Hello, World!\00"

define i32 @add(i32 %a, i32 %b) {
    %result = add i32 %a, %b
    ret i32 %result
}

define i32 @sub(i32 %a, i32 %b) {
    %result = sub i32 %a, %b
    ret i32 %result
}

define i32 @mul(i32 %a, i32 %b) {
    %result = mul i32 %a, %b
    ret i32 %result
}

define i32 @div(i32 %a, i32 %b) {
    %result = sdiv i32 %a, %b
    ret i32 %result
}

define external i32 @mod(i32 %a, i32 %b) {
    %result = srem i32 %a, %b
    ret i32 %result
}

declare void @print()
define i32 @main() {
    call void @print()
    ret i32 0
}