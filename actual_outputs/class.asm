.section
.data
.section
.text
jal x30,__joi
# Begin class 0 definition
# Declared member 0 of type INT at offset 0
# Declared member 1 of type CHAR at offset 4
# Declared member 2 of type FLOAT at offset 5
# Begin method printnum for class 0
__class_0_method_printnum:
lui x5,2
addi x5,x5,8
add x5,x5,x8
lw x5,0(x5)
addi x5,x5,4
lw x5,0(x5)
sw x5,0(x2)
addi x2,x2,4
addi x2,x2,-4
lw x5,0(x2)
add a0,x5,x0
addi x2,x2,4
addi a7,x0,1
#PRINT PANREN DAAecall
addi x5,x0,1
sw x5,0(x2)
addi x2,x2,4
addi x2,x2,-4
lw x5,0(x2)
lui x6,2
addi x6,x6,8
lw x6,0(x6)
sw x5,0(x6)
lui x5,2
addi x5,x5,4
lw x2,0(x5)
lw x5,-8(x2)
lui x6,2
addi x6,x6,16
sw x5,0(x6)
lw x5,-12(x2)
lui x6,2
addi x6,x6,12
sw x5,0(x6)
lw x7,-16(x2)
lw x5,-20(x2)
lui x6,2
addi x6,x6,4
sw x5,0(x6)
lw x5,-4(x2)
lui x6,2
addi x6,x6,8
lw x2,0(x6)
addi x2,x2,4
lui x6,2
addi x6,x6,8
sw x7,0(x6)
jalr x0,x1,0
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
# Create object of class 0
# Storing object pointer information
lui x5,2
addi x5,x5,24
add x5,x5,x8
lw x6,0(x5)
lui x7,3
addi x7,x7,-1984
sw x7,0(x6)
addi x7,x0,9
sw x7,4(x6)
addi x7,x0,5
sw x7,8(x6)
addi x6,x6,12
sw x6,0(x5)
# Pushing object pointer triplet to stack
lui x5,3
addi x5,x5,-1984
sw x5,0(x2)
addi x2,x2,4
addi x5,x0,9
sw x5,0(x2)
addi x2,x2,4
addi x5,x0,5
sw x5,0(x2)
addi x2,x2,4
# Get attribute 0 of type INT
addi x2,x2,-12
lw x20,0(x2)
lw x21,4(x2)
lw x22,8(x2)
addi x22,x22,-5
# Calculate attribute offset
addi x23,x0,0
add x24,x20,x23
# Load attribute value based on type
lw x20,0(x24)
# Push attribute value to stack
sw x20,0(x2)
addi x2,x2,4
addi x2,x2,-4
lw x5,0(x2)
add a0,x5,x0
addi x2,x2,4
addi a7,x0,1
#PRINT PANREN DAAecall
addi x5,x0,1420
sw x5,0(x2)
addi x2,x2,4
# Method call for printnum
addi x2,x2,-12
lw x20,0(x2)
lw x21,4(x2)
lw x22,8(x2)
jal x1,__class_0_method_printnum
addi x2,x2,-4
lw x5,0(x2)
lui x6,2
addi x6,x6,12
add x6,x6,x8
lw x6,0(x6)
addi x6,x6,4
sw x5,0(x6)
addi x5,x0,2014
sw x5,0(x2)
addi x2,x2,4
# Set attribute 1 of type INT
addi x2,x2,-4
lw x20,0(x2)
addi x2,x2,-12
lw x21,0(x2)
lw x22,4(x2)
lw x23,8(x2)
addi x23,x23,-5
# Calculate attribute offset
addi x24,x0,4
add x24,x21,x24
# Store attribute value based on type
sw x20,0(x24)
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
