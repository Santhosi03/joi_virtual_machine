.data
prompt_name:    .ascii "Enter your name: "
prompt_temp:    .ascii "Enter temperature in Celsius: "
msg_result:     .ascii ", "
msg_fahrenheit: .ascii "°C is "

.text
.global main
main:
    # Prologue
    addi sp, sp, -48     # Space for variables and ra
    sw ra, 44(sp)
    sw s0, 40(sp)
    addi s0, sp, 48
    
    # Print name prompt
    la a0, prompt_name
    li a7, 4
    ecall
    
    # Read name
    addi a0, sp, 8       # Buffer for name
    li a1, 50            # Max length
    li a7, 8
    ecall
    
    # Print temperature prompt
    la a0, prompt_temp
    li a7, 4
    ecall
    
    # Read celsius
    li a7, 6
    ecall
    fsw fa0, -48(s0)     # Store celsius
    
    # Convert to fahrenheit
    flw ft0, -48(s0)     # Load celsius
    li t0, 9
    fcvt.s.w ft1, t0
    fmul.s ft0, ft0, ft1 # celsius * 9
    li t0, 5
    fcvt.s.w ft1, t0
    fdiv.s ft0, ft0, ft1 # / 5
    li t0, 32
    fcvt.s.w ft1, t0
    fadd.s ft0, ft0, ft1 # + 32
    fsw ft0, -44(s0)     # Store fahrenheit
    
    # Print result
    addi a0, sp, 8       # Load name address
    li a7, 4
    ecall
    la a0, msg_result
    li a7, 4
    ecall
    flw fa0, -48(s0)     # Load celsius
    li a7, 2
    ecall
    la a0, msg_fahrenheit
    li a7, 4
    ecall
    flw fa0, -44(s0)     # Load fahrenheit
    li a7, 2
    ecall
    
# Epilogue
    li a0, 0
    lw ra, 44(sp)
    lw s0, 40(sp)
    addi sp, sp, 48
    ret




