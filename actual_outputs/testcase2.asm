.section
.data
__main__data0:
	.asciz "Enter your name: "
__main__data1:
	.asciz "Hello! Enter temperature in Celsius: "
.section
.text
jal x30,main
main:
lui x5,2
addi x5,x5,10
addi x5,x5,10
addi x5,x5,10
addi x5,x5,2
lui x6,2
addi x6,x6,1
addi x6,x6,1
addi x6,x6,1
addi x6,x6,1
add x6,x8,x6
sw x5,0(x6)
lui x5,2
addi x5,x5,181
addi x5,x5,181
addi x5,x5,181
addi x5,x5,1
lui x6,2
addi x6,x6,2
addi x6,x6,2
addi x6,x6,2
addi x6,x6,2
add x6,x8,x6
sw x5,0(x6)
lui x5,2
addi x5,x5,192
addi x5,x5,192
addi x5,x5,192
addi x5,x5,0
lui x6,2
addi x6,x6,4
addi x6,x6,4
addi x6,x6,4
addi x6,x6,0
add x6,x8,x6
sw x5,0(x6)
lui x5,2
addi x5,x5,362
addi x5,x5,362
addi x5,x5,362
addi x5,x5,2
lui x6,2
addi x6,x6,0
addi x6,x6,0
addi x6,x6,0
addi x6,x6,0
add x6,x8,x6
sw x5,0(x6)
lui x5,64
addi x5,x5,0
addi x5,x5,0
addi x5,x5,0
addi x5,x5,0
lui x6,2
addi x6,x6,6
addi x6,x6,6
addi x6,x6,6
addi x6,x6,2
add x6,x8,x6
sw x5,0(x6)
lui x2,2
addi x2,x2,362
addi x2,x2,362
addi x2,x2,362
addi x2,x2,2
add x2,x2,x8
lui a0,65552
addi a0,a0,0
addi a0,a0,0
addi a7,x0,4
ecall
addi x2,x2,4
lui a0,65552
addi a0,a0,0
addi a0,a0,18
addi a7,x0,4
ecall
addi a7,x0,6
ecall
fsw fa0,0(x2)
addi x2,x2,4
addi x2,x2,-4
flw f3,0(x2)
lui x6,2
addi x6,x6,1
addi x6,x6,1
addi x6,x6,1
addi x6,x6,1
add x6,x6,x8
lw x6,0(x6)
addi x6,x6,8
fsw f3,0(x6)
lui x5,2
addi x5,x5,1
addi x5,x5,1
addi x5,x5,1
addi x5,x5,1
add x5,x5,x8
lw x5,0(x5)
addi x5,x5,8
flw f3,0(x5)
fsw f3,0(x2)
addi x2,x2,4
lui x7,266496
addi x7,x7,0
addi x7,x7,0
fmv.w.x f3,x7
fsw f3,0(x2)
addi x2,x2,4
addi x2,x2,-4
flw f3,0(x2)
lui x6,2
addi x6,x6,4
addi x6,x6,4
addi x6,x6,4
addi x6,x6,0
add x6,x6,x8
lw x6,0(x6)
addi x6,x6,4
fsw f3,0(x6)
lui x5,2
addi x5,x5,4
addi x5,x5,4
addi x5,x5,4
addi x5,x5,0
add x5,x5,x8
lw x5,0(x5)
addi x5,x5,4
flw f3,0(x5)
fsw f3,0(x2)
addi x2,x2,4
lui x7,264704
addi x7,x7,0
addi x7,x7,0
fmv.w.x f3,x7
fsw f3,0(x2)
addi x2,x2,4
addi x2,x2,-4
flw f3,0(x2)
lui x6,2
addi x6,x6,4
addi x6,x6,4
addi x6,x6,4
addi x6,x6,0
add x6,x6,x8
lw x6,0(x6)
addi x6,x6,8
fsw f3,0(x6)
lui x5,2
addi x5,x5,4
addi x5,x5,4
addi x5,x5,4
addi x5,x5,0
add x5,x5,x8
lw x5,0(x5)
addi x5,x5,8
flw f3,0(x5)
fsw f3,0(x2)
addi x2,x2,4
lui x7,270336
addi x7,x7,0
addi x7,x7,0
fmv.w.x f3,x7
fsw f3,0(x2)
addi x2,x2,4
addi x2,x2,-4
flw f3,0(x2)
addi x2,x2,-4
flw f4,0(x2)
fadd.s f3,f4,f3
fsw f3,0(x2)
addi x2,x2,4
addi x2,x2,-4
flw f3,0(x2)
lui x6,2
addi x6,x6,1
addi x6,x6,1
addi x6,x6,1
addi x6,x6,1
add x6,x6,x8
lw x6,0(x6)
addi x6,x6,12
fsw f3,0(x6)
lui x5,2
addi x5,x5,1
addi x5,x5,1
addi x5,x5,1
addi x5,x5,1
add x5,x5,x8
lw x5,0(x5)
addi x5,x5,12
flw f3,0(x5)
fsw f3,0(x2)
addi x2,x2,4
addi x2,x2,-4
flw fa0,0(x2)
addi x2,x2,4
lui a7,0
addi a7,a7,0
addi a7,a7,0
addi a7,a7,0
addi a7,a7,2
ecall
lui x5,0
addi x5,x5,0
addi x5,x5,0
addi x5,x5,0
addi x5,x5,0
sw x5,0(x2)
addi x2,x2,4
jal x30,__END__
__END__:
nop
