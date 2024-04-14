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

define i32 @mod(i32 %a, i32 %b) {
    %result = srem i32 %a, %b
    ret i32 %result
}

declare void @print(i32)
define i32 @main() {
    %a = call i32 @add(i32 1, i32 2)
    %b = call i32 @sub(i32 3, i32 4)
    %c = call i32 @mul(i32 5, i32 6)
    %d = call i32 @div(i32 7, i32 8)
    %e = call i32 @mod(i32 9, i32 10)
    call void @print(i32 %a)
    ret i32 0
}