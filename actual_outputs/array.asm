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
# Storing pointer information
lui x5,2
addi x5,x5,24
add x5,x5,x8
lw x6,0(x5)
lui x7,3
addi x7,x7,-1984
sw x7,0(x6)
addi x7,x0,5
sw x7,4(x6)
addi x7,x0,1
sw x7,8(x6)
addi x6,x6,12
sw x6,0(x5)
# Pushing pointer triplet to stack
lui x5,3
addi x5,x5,-1984
sw x5,0(x2)
addi x2,x2,4
addi x5,x0,5
sw x5,0(x2)
addi x2,x2,4
addi x5,x0,1
sw x5,0(x2)
addi x2,x2,4
addi x2,x2,-4
lw x5,0(x2)
lui x6,2
addi x6,x6,4
add x6,x6,x8
lw x6,0(x6)
addi x6,x6,12
sw x5,0(x6)
addi x2,x2,-4
lw x5,0(x2)
lui x6,2
addi x6,x6,4
add x6,x6,x8
lw x6,0(x6)
addi x6,x6,8
sw x5,0(x6)
addi x2,x2,-4
lw x5,0(x2)
lui x6,2
addi x6,x6,4
add x6,x6,x8
lw x6,0(x6)
addi x6,x6,4
sw x5,0(x6)
addi x5,x0,0
sw x5,0(x2)
addi x2,x2,4
addi x2,x2,-4
lw x5,0(x2)
lui x6,2
addi x6,x6,4
add x6,x6,x8
lw x6,0(x6)
addi x6,x6,16
sw x5,0(x6)
addi x5,x0,0
sw x5,0(x2)
addi x2,x2,4
addi x2,x2,-4
lw x5,0(x2)
lui x6,2
addi x6,x6,4
add x6,x6,x8
lw x6,0(x6)
addi x6,x6,20
sw x5,0(x6)
__L1:
addi x5,x0,5
sw x5,0(x2)
addi x2,x2,4
lui x5,2
addi x5,x5,4
add x5,x5,x8
lw x5,0(x5)
addi x5,x5,20
lw x5,0(x5)
sw x5,0(x2)
addi x2,x2,4
addi x2,x2,-4
lw x6,0(x2)
addi x2,x2,-4
lw x5,0(x2)
blt x5,x6,___CL0
beq x5,x6,___CL0
addi x7,x0,1
jal x30,___CL1
___CL0:
addi x7,x0,0
___CL1:
sw x7,0(x2)
addi x2,x2,4
addi x2,x2,-4
lw x5,0(x2)
addi x6,x0,1
beq x5,x6,__L2
jal x30,__L3
__L2:
lui x5,2
addi x5,x5,4
add x5,x5,x8
lw x5,0(x5)
addi x5,x5,20
lw x5,0(x5)
sw x5,0(x2)
addi x2,x2,4
addi x5,x0,1
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
addi x5,x5,4
add x5,x5,x8
lw x5,0(x5)
addi x5,x5,8
lw x5,0(x5)
sw x5,0(x2)
addi x2,x2,4
lui x5,2
addi x5,x5,4
add x5,x5,x8
lw x5,0(x5)
addi x5,x5,12
lw x5,0(x5)
sw x5,0(x2)
addi x2,x2,4
lui x5,2
addi x5,x5,4
add x5,x5,x8
lw x5,0(x5)
addi x5,x5,20
lw x5,0(x5)
sw x5,0(x2)
addi x2,x2,4
# Calculate array index address
addi x2,x2,-4
lw x20,0(x2)
addi x2,x2,-12
lw x21,0(x2)
lw x22,4(x2)
lw x23,8(x2)
bge x20,x22,__array_out_of_bounds
blt x20,x0,__array_out_of_bounds
# Determine element size based on type
addi x24,x0,0
jal x1,__type_check
            # Multiplication of x20 and x24
            addi x26,x0,0     # Initialize result
            addi x27,x0,0     # Initialize counter
            add x28,x20,x0  # Copy multiplicand
            add x29,x24,x0  # Copy multiplier
            
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
            add x20,x26,x0   # Move result to destination
        add x20,x20,x21
sw x20,0(x2)
addi x2,x2,4
lui x5,2
addi x5,x5,12
add x5,x5,x8
lw x5,0(x5)
addi x5,x5,4
lw x5,0(x5)
sw x5,0(x2)
addi x2,x2,4
# Store value at address
addi x2,x2,-4
lw x20,0(x2)
addi x2,x2,-4
lw x21,0(x2)
sw x20,0(x21)
lui x5,2
addi x5,x5,4
add x5,x5,x8
lw x5,0(x5)
addi x5,x5,16
lw x5,0(x5)
sw x5,0(x2)
addi x2,x2,4
lui x5,2
addi x5,x5,4
add x5,x5,x8
lw x5,0(x5)
addi x5,x5,4
lw x5,0(x5)
sw x5,0(x2)
addi x2,x2,4
lui x5,2
addi x5,x5,4
add x5,x5,x8
lw x5,0(x5)
addi x5,x5,8
lw x5,0(x5)
sw x5,0(x2)
addi x2,x2,4
lui x5,2
addi x5,x5,4
add x5,x5,x8
lw x5,0(x5)
addi x5,x5,12
lw x5,0(x5)
sw x5,0(x2)
addi x2,x2,4
lui x5,2
addi x5,x5,4
add x5,x5,x8
lw x5,0(x5)
addi x5,x5,20
lw x5,0(x5)
sw x5,0(x2)
addi x2,x2,4
# Calculate array index address
addi x2,x2,-4
lw x20,0(x2)
addi x2,x2,-12
lw x21,0(x2)
lw x22,4(x2)
lw x23,8(x2)
bge x20,x22,__array_out_of_bounds
blt x20,x0,__array_out_of_bounds
# Determine element size based on type
addi x24,x0,0
jal x1,__type_check
            # Multiplication of x20 and x24
            addi x26,x0,0     # Initialize result
            addi x27,x0,0     # Initialize counter
            add x28,x20,x0  # Copy multiplicand
            add x29,x24,x0  # Copy multiplier
            
            __mul_1_loop:
            beq x29,x0,__mul_1_done
            andi x30,x29,1    # Check LSB
            beq x30,x0,__mul_1_shift
            add x26,x26,x28   # Add multiplicand to result
            
            __mul_1_shift:
            slli x28,x28,1    # Shift multiplicand left
            srli x29,x29,1    # Shift multiplier right
            bge x0,x0,__mul_1_loop
            
            __mul_1_done:
            add x20,x26,x0   # Move result to destination
        add x20,x20,x21
sw x20,0(x2)
addi x2,x2,4
# Access value at address
addi x2,x2,-4
lw x21,0(x2)
lw x20,0(x21)
sw x20,0(x2)
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
addi x6,x6,4
add x6,x6,x8
lw x6,0(x6)
addi x6,x6,16
sw x5,0(x6)
lui x5,2
addi x5,x5,4
add x5,x5,x8
lw x5,0(x5)
addi x5,x5,20
lw x5,0(x5)
sw x5,0(x2)
addi x2,x2,4
addi x5,x0,1
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
addi x6,x6,4
add x6,x6,x8
lw x6,0(x6)
addi x6,x6,20
sw x5,0(x6)
jal x30,__L1
__L3:
lui x5,2
addi x5,x5,4
add x5,x5,x8
lw x5,0(x5)
addi x5,x5,16
lw x5,0(x5)
sw x5,0(x2)
addi x2,x2,4
addi x2,x2,-4
lw x5,0(x2)
add a0,x5,x0
addi x2,x2,4
addi a7,x0,1
#PRINT PANREN DAAecall
addi x5,x0,0
sw x5,0(x2)
addi x2,x2,4
jal x30,__END__
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
