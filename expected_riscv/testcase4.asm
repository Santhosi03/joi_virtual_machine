Square_constructor:
    addi sp, sp, -16
    sw   ra, 12(sp)
    
    # Allocate object
    li   a0, 8
    jal  ra, malloc
    
    # Set vtable
    la   t0, vtable_Square
    sw   t0, 0(a0)
    
    # Set side
    sw   a1, 4(a0)
    
    lw   ra, 12(sp)
    addi sp, sp, 16
    ret

Square_area:
    lw   t0, 4(a0)     # Load side
    mul  a0, t0, t0    # Calculate area
    ret