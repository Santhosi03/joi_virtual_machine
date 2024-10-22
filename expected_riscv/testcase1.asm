main:
    addi sp, sp, -16    # Allocate stack frame
    sw   ra, 12(sp)     # Save return address
    
    # Push arguments and call
    li   a0, 5
    li   a1, 3
    jal  ra, add
    
    # Return
    lw   ra, 12(sp)     # Restore return address
    addi sp, sp, 16     # Deallocate stack frame
    ret

add:
    # a0 and a1 already contain arguments
    add  a0, a0, a1     # Add the numbers
    ret                 # Return result in a0
