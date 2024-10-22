createArray:
    addi sp, sp, -16
    sw   ra, 12(sp)
    sw   s0, 8(sp)
    
    # Allocate array
    slli t0, a0, 2     # Multiply size by 4
    mv   a1, a0        # Save size
    mv   a0, t0
    jal  ra, malloc
    
    mv   s0, a0        # Save array pointer
    li   t0, 0         # i = 0
    
loop:
    bge  t0, a1, end_loop
    
    # arr[i] = i
    slli t1, t0, 2     # t1 = i * 4
    add  t1, s0, t1    # t1 = arr + i*4
    sw   t0, 0(t1)     # arr[i] = i
    
    addi t0, t0, 1     # i++
    j    loop
    
end_loop:
    mv   a0, s0        # Return array pointer
    
    lw   s0, 8(sp)
    lw   ra, 12(sp)
    addi sp, sp, 16
    ret
