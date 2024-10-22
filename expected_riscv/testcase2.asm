main:
    addi sp, sp, -16
    sw   ra, 12(sp)
    
    # Allocate Rectangle object
    li   a0, 8          # Size of Rectangle
    jal  ra, malloc
    
    # Initialize object
    li   t0, 4
    sw   t0, 0(a0)     # width
    li   t0, 5
    sw   t0, 4(a0)     # height
    
    # Call area method
    jal  ra, Rectangle_area
    
    lw   ra, 12(sp)
    addi sp, sp, 16
    ret

Rectangle_area:
    lw   t0, 0(a0)     # Load width
    lw   t1, 4(a0)     # Load height
    mul  a0, t0, t1    # Calculate area
    ret
