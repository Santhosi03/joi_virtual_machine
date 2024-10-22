
divide:
    addi sp, sp, -16
    sw   ra, 12(sp)
    
    beqz a1, division_error
    
    div  a0, a0, a1
    j    divide_end
    
division_error:
    la   a0, error_msg
    jal  ra, exception_handler
    
divide_end:
    lw   ra, 12(sp)
    addi sp, sp, 16
    ret