.section
.data
.section
.text
jal x30,__joi
__joi:
lui x5,2
addi x5,x5,32
lui x6,2
addi x6,x6,4
add x6,x8,x6
sw x5,0(x6)
lui x5,2
addi x5,x5,544
lui x6,2
addi x6,x6,8
add x6,x8,x6
sw x5,0(x6)
lui x5,2
addi x5,x5,576
lui x6,2
addi x6,x6,12
add x6,x8,x6
sw x5,0(x6)
lui x5,2
addi x5,x5,1088
lui x6,2
add x6,x8,x6
sw x5,0(x6)
lui x5,3
addi x5,x5,-1984
lui x6,2
addi x6,x6,16
add x6,x8,x6
sw x5,0(x6)
lui x5,5
addi x5,x5,-176
lui x6,2
addi x6,x6,24
add x6,x8,x6
sw x5,0(x6)
lui x5,64
lui x6,2
addi x6,x6,20
add x6,x8,x6
sw x5,0(x6)
lui x2,2
addi x2,x2,1088
add x2,x2,x8
addi x5,x0,6
sw x5,0(x2)
addi x2,x2,4
addi x2,x2,-4
lw x5,0(x2)
lui x6,2
addi x6,x6,4
add x6,x6,x8
lw x6,0(x6)
addi x6,x6,4
sw x5,0(x6)
addi x5,x0,7
sw x5,0(x2)
addi x2,x2,4
addi x2,x2,-4
lw x5,0(x2)
lui x6,2
addi x6,x6,12
add x6,x6,x8
lw x6,0(x6)
addi x6,x6,4
sw x5,0(x6)
lui x5,2
addi x5,x5,4
add x5,x5,x8
lw x5,0(x5)
addi x5,x5,4
lw x5,0(x5)
sw x5,0(x2)
addi x2,x2,4
lui x5,2
addi x5,x5,12
add x5,x5,x8
lw x5,0(x5)
addi x5,x5,4
lw x5,0(x5)
sw x5,0(x2)
addi x2,x2,4
addi x2,x2,-4
lw x5,0(x2)
addi x2,x2,-4
lw x6,0(x2)
            # Multiplication of x6 and x5
            addi x26,x0,0     # Initialize result
            addi x27,x0,0     # Initialize counter
            add x28,x6,x0  # Copy multiplicand
            add x29,x5,x0  # Copy multiplier
            
            __mul_0_loop:
            beq x29,x0,__mul_0_done
            andi x30,x29,1    # Check LSB
            beq x30,x0,__mul_0_shift
            add x26,x26,x28   # Add multiplicand to result
            
            __mul_0_shift:
            slli x28,x28,1    # Shift multiplicand left
            srli x29,x29,1    # Shift multiplier right
            bge x0,x0,__mul_0_loop
            
            __mul_0_done:
            add x5,x26,x0   # Move result to destination
        sw x5,0(x2)
addi x2,x2,4
addi x2,x2,-4
lw x5,0(x2)
add a0,x5,x0
addi x2,x2,4
addi a7,x0,1
#PRINT PANREN DAAecall
jal x30,__END__
__type_check:
addi x25,x0,1
beq x23,x25,__type_int
addi x25,x0,2
beq x23,x25,__type_float
addi x25,x0,3
beq x23,x25,__type_char
addi x25,x0,4
beq x23,x25,__type_bool
__type_int:
addi x24,x0,4
jalr x0,x1,0
__type_float:
addi x24,x0,4
jalr x0,x1,0
__type_char:
addi x24,x0,1
jalr x0,x1,0
__type_bool:
addi x24,x0,1
jalr x0,x1,0
__array_out_of_bounds:
nop
__END__:
nop
