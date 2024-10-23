.data
prompt1: .ascii "Enter array size: "
prompt2: .ascii "Enter "
prompt3: .ascii " numbers:\n"
sum_msg: .ascii "Sum: "
avg_msg: .ascii "\nAverage: "
max_msg: .ascii "\nMaximum: "
newline: .ascii "\n"

.text
.globl main
main:
    # Prologue
    addi sp, sp, -32     # Space for variables and ra
    sw ra, 28(sp)        # Save return address
    sw s0, 24(sp)        # Save frame pointer
    addi s0, sp, 32      # Set up frame pointer
    
    # Print "Enter array size: "
    la a0, prompt1
    li a7, 4
    ecall
    
    # Read n (array size)
    li a7, 5
    ecall
    mv s1, a0           # s1 = n
    
    # Print "Enter n numbers:"
    la a0, prompt2
    li a7, 4
    ecall
    
    mv a0, s1           # Print n
    li a7, 1
    ecall
    
    la a0, prompt3
    li a7, 4
    ecall
    
    # Initialize variables
    li s2, 0            # s2 = sum = 0
    li s3, 0            # s3 = max = 0
    li t0, 0            # t0 = i = 0
    
loop:
    bge t0, s1, end_loop    # if (i >= n) goto end_loop
    
    # Read number
    li a7, 5
    ecall
    mv t1, a0           # t1 = current number
    
    # Update sum
    add s2, s2, t1      # sum += num
    
    # Update max if necessary
    bge s3, t1, skip_max    # if (max >= num) skip
    mv s3, t1           # max = num
skip_max:
    
    addi t0, t0, 1      # i++
    j loop
    
end_loop:
    # Print sum
    la a0, sum_msg
    li a7, 4
    ecall
    
    mv a0, s2
    li a7, 1
    ecall
    
    # Calculate and print average
    la a0, avg_msg
    li a7, 4
    ecall
    
    # Convert sum to float and divide by n
    fcvt.s.w fa0, s2    # Convert sum to float
    fcvt.s.w fa1, s1    # Convert n to float
    fdiv.s fa0, fa0, fa1 # fa0 = sum/n
    
    li a7, 2            # Print float
    ecall
    
    # Print maximum
    la a0, max_msg
    li a7, 4
    ecall
    
    mv a0, s3
    li a7, 1
    ecall
    
    la a0, newline
    li a7, 4
    ecall
    
    # Epilogue
    li a0, 0            # Return 0
    lw ra, 28(sp)
    lw s0, 24(sp)
    addi sp, sp, 32
    ret