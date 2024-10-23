.data
prompt: .ascii "Enter two numbers:\n"
msg_greater: .ascii "Sum is greater than 10: "
msg_lesser: .ascii "Sum is less than or equal to 10: "
msg_diff: .ascii "\nDifference is: "

.text
.globl main
main:
    # Prologue
    addi sp, sp, -32     # Space for 4 variables and ra
    sw ra, 28(sp)        # Save return address
    sw s0, 24(sp)        # Save frame pointer
    addi s0, sp, 32      # Set up frame pointer
    
    # Print prompt
    la a0, prompt
    li a7, 4
    ecall
    
    # Read first number
    li a7, 5
    ecall
    sw a0, -32(s0)       # Store a
    
    # Read second number
    li a7, 5
    ecall
    sw a0, -28(s0)       # Store b
    
    # Calculate sum
    lw t0, -32(s0)       # Load a
    lw t1, -28(s0)       # Load b
    add t2, t0, t1       # Add them
    sw t2, -24(s0)       # Store sum
    
    # Calculate difference
    sub t2, t0, t1       # Subtract
    sw t2, -20(s0)       # Store diff
    
    # Compare sum with 10
    lw t0, -24(s0)       # Load sum
    li t1, 10
    ble t0, t1, else_branch
    
    # Print "greater than" message
    la a0, msg_greater
    li a7, 4
    ecall
    lw a0, -24(s0)       # Load sum
    li a7, 1
    ecall
    j end_if
    
else_branch:
    la a0, msg_lesser
    li a7, 4
    ecall
    lw a0, -24(s0)       # Load sum
    li a7, 1
    ecall
    
end_if:
    # Print difference
    la a0, msg_diff
    li a7, 4
    ecall
    lw a0, -20(s0)       # Load diff
    li a7, 1
    ecall
    
    # Epilogue
    li a0, 0             # Return 0
    lw ra, 28(sp)
    lw s0, 24(sp)
    addi sp, sp, 32
    ret