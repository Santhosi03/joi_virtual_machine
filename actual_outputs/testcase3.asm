.section
.data
__main__data0:
	.asciz "Enter array size: "
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
addi a7,x0,5
ecall
sw a0,0(x2)
addi x2,x2,4
addi x2,x2,-4
lw x5,0(x2)
lui x6,2
addi x6,x6,1
addi x6,x6,1
addi x6,x6,1
addi x6,x6,1
add x6,x6,x8
lw x6,0(x6)
addi x6,x6,4
sw x5,0(x6)
lui x5,0
addi x5,x5,0
addi x5,x5,0
addi x5,x5,0
addi x5,x5,0
sw x5,0(x2)
addi x2,x2,4
addi x2,x2,-4
lw x5,0(x2)
lui x6,2
addi x6,x6,1
addi x6,x6,1
addi x6,x6,1
addi x6,x6,1
add x6,x6,x8
lw x6,0(x6)
addi x6,x6,8
sw x5,0(x6)
lui x5,0
addi x5,x5,0
addi x5,x5,0
addi x5,x5,0
addi x5,x5,0
sw x5,0(x2)
addi x2,x2,4
addi x2,x2,-4
lw x5,0(x2)
lui x6,2
addi x6,x6,1
addi x6,x6,1
addi x6,x6,1
addi x6,x6,1
add x6,x6,x8
lw x6,0(x6)
addi x6,x6,12
sw x5,0(x6)
lui x5,0
addi x5,x5,0
addi x5,x5,0
addi x5,x5,0
addi x5,x5,0
sw x5,0(x2)
addi x2,x2,4
addi x2,x2,-4
lw x5,0(x2)
lui x6,2
addi x6,x6,1
addi x6,x6,1
addi x6,x6,1
addi x6,x6,1
add x6,x6,x8
lw x6,0(x6)
addi x6,x6,16
sw x5,0(x6)
__L1:
lui x5,2
addi x5,x5,1
addi x5,x5,1
addi x5,x5,1
addi x5,x5,1
add x5,x5,x8
lw x5,0(x5)
addi x5,x5,16
lw x5,0(x5)
sw x5,0(x2)
addi x2,x2,4
lui x5,2
addi x5,x5,1
addi x5,x5,1
addi x5,x5,1
addi x5,x5,1
add x5,x5,x8
lw x5,0(x5)
addi x5,x5,4
lw x5,0(x5)
sw x5,0(x2)
addi x2,x2,4
addi x2,x2,-4
lw x6,0(x2)
addi x2,x2,-4
lw x5,0(x2)
blt x5,x6,___CL0
addi x7,x0,0
jal x30,___CL1
___CL0:
addi x7,x0,1
___CL1:
sw x7,0(x2)
addi x2,x2,4
addi x2,x2,-4
lw x5,0(x2)
lui x6,0
addi x6,x6,0
addi x6,x6,0
addi x6,x6,0
addi x6,x6,1
beq x5,x6,__L2
jal x30,__L3
__L2:
addi a7,x0,5
ecall
sw a0,0(x2)
addi x2,x2,4
addi x2,x2,-4
lw x5,0(x2)
lui x6,2
addi x6,x6,1
addi x6,x6,1
addi x6,x6,1
addi x6,x6,1
add x6,x6,x8
lw x6,0(x6)
addi x6,x6,20
sw x5,0(x6)
lui x5,2
addi x5,x5,1
addi x5,x5,1
addi x5,x5,1
addi x5,x5,1
add x5,x5,x8
lw x5,0(x5)
addi x5,x5,20
lw x5,0(x5)
sw x5,0(x2)
addi x2,x2,4
lui x5,2
addi x5,x5,1
addi x5,x5,1
addi x5,x5,1
addi x5,x5,1
add x5,x5,x8
lw x5,0(x5)
addi x5,x5,8
lw x5,0(x5)
sw x5,0(x2)
addi x2,x2,4
addi x2,x2,-4
lw x5,0(x2)
lui x6,2
addi x6,x6,1
addi x6,x6,1
addi x6,x6,1
addi x6,x6,1
add x6,x6,x8
lw x6,0(x6)
addi x6,x6,8
sw x5,0(x6)
lui x5,2
addi x5,x5,1
addi x5,x5,1
addi x5,x5,1
addi x5,x5,1
add x5,x5,x8
lw x5,0(x5)
addi x5,x5,20
lw x5,0(x5)
sw x5,0(x2)
addi x2,x2,4
lui x5,2
addi x5,x5,1
addi x5,x5,1
addi x5,x5,1
addi x5,x5,1
add x5,x5,x8
lw x5,0(x5)
addi x5,x5,12
lw x5,0(x5)
sw x5,0(x2)
addi x2,x2,4
addi x2,x2,-4
lw x6,0(x2)
addi x2,x2,-4
lw x5,0(x2)
blt x5,x6,___CL2
beq x5,x6,___CL2
addi x7,x0,1
jal x30,___CL3
___CL2:
addi x7,x0,0
___CL3:
sw x7,0(x2)
addi x2,x2,4
addi x2,x2,-4
lw x5,0(x2)
lui x6,0
addi x6,x6,0
addi x6,x6,0
addi x6,x6,0
addi x6,x6,1
beq x5,x6,__L4
jal x30,__L5
__L4:
lui x5,2
addi x5,x5,1
addi x5,x5,1
addi x5,x5,1
addi x5,x5,1
add x5,x5,x8
lw x5,0(x5)
addi x5,x5,20
lw x5,0(x5)
sw x5,0(x2)
addi x2,x2,4
addi x2,x2,-4
lw x5,0(x2)
lui x6,2
addi x6,x6,1
addi x6,x6,1
addi x6,x6,1
addi x6,x6,1
add x6,x6,x8
lw x6,0(x6)
addi x6,x6,12
sw x5,0(x6)
__L5:
lui x5,2
addi x5,x5,1
addi x5,x5,1
addi x5,x5,1
addi x5,x5,1
add x5,x5,x8
lw x5,0(x5)
addi x5,x5,16
lw x5,0(x5)
sw x5,0(x2)
addi x2,x2,4
lui x5,0
addi x5,x5,0
addi x5,x5,0
addi x5,x5,0
addi x5,x5,0
sw x5,0(x2)
addi x2,x2,4
addi x2,x2,-4
lw x5,0(x2)
addi x2,x2,-4
lw x6,0(x2)
add x5,x6,x5
sw x5,0(x2)
addi x2,x2,4
addi x2,x2,-4
lw x5,0(x2)
lui x6,2
addi x6,x6,1
addi x6,x6,1
addi x6,x6,1
addi x6,x6,1
add x6,x6,x8
lw x6,0(x6)
addi x6,x6,16
sw x5,0(x6)
jal x30,__L1
__L3:
lui x5,2
addi x5,x5,1
addi x5,x5,1
addi x5,x5,1
addi x5,x5,1
add x5,x5,x8
lw x5,0(x5)
addi x5,x5,8
lw x5,0(x5)
sw x5,0(x2)
addi x2,x2,4
lui x5,2
addi x5,x5,1
addi x5,x5,1
addi x5,x5,1
addi x5,x5,1
add x5,x5,x8
lw x5,0(x5)
addi x5,x5,4
lw x5,0(x5)
sw x5,0(x2)
addi x2,x2,4
addi x2,x2,-4
lw x5,0(x2)
fcvt.s.w f3,x5
lui x6,2
addi x6,x6,1
addi x6,x6,1
addi x6,x6,1
addi x6,x6,1
add x6,x6,x8
lw x6,0(x6)
addi x6,x6,24
fsw f3,0(x6)
lui x5,2
addi x5,x5,1
addi x5,x5,1
addi x5,x5,1
addi x5,x5,1
add x5,x5,x8
lw x5,0(x5)
addi x5,x5,8
lw x5,0(x5)
sw x5,0(x2)
addi x2,x2,4
addi x2,x2,-4
lw x5,0(x2)
add a0,x5,x0
addi x2,x2,4
lui a7,0
addi a7,a7,0
addi a7,a7,0
addi a7,a7,0
addi a7,a7,1
ecall
lui x5,2
addi x5,x5,1
addi x5,x5,1
addi x5,x5,1
addi x5,x5,1
add x5,x5,x8
lw x5,0(x5)
addi x5,x5,24
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
lui x5,2
addi x5,x5,1
addi x5,x5,1
addi x5,x5,1
addi x5,x5,1
add x5,x5,x8
lw x5,0(x5)
addi x5,x5,12
lw x5,0(x5)
sw x5,0(x2)
addi x2,x2,4
addi x2,x2,-4
lw x5,0(x2)
add a0,x5,x0
addi x2,x2,4
lui a7,0
addi a7,a7,0
addi a7,a7,0
addi a7,a7,0
addi a7,a7,1
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
