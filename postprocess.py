import struct
import re


def get_ieee_rep(value, hex=None):
    if hex is None:
        hex = ''.join('{:02x}'.format(x)[::-1]
                      for x in struct.pack('f', float(value)))[::-1]
    upper = hex[:5]
    mid = hex[5]
    lower = hex[6:]
    return ('0x'+upper, '0x'+mid, '0x'+lower)


def convert_rep(value):
    """
    More efficient conversion of large immediate values
    
    Args:
        value (int): The immediate value to load
    
    Returns:
        tuple: (upper_immediate, lower_immediate)
    """
    value = int(value)
    
    # Handle negative numbers by converting to unsigned 32-bit representation
    if value < 0:
        value = (1 << 32) + value
    
    # Split into upper and lower 12-bit parts
    upper_imm = value >> 12  # Upper 20 bits
    lower_imm = value & 0xFFF  # Lower 12 bits
    
    # Handle sign extension for negative lower immediate
    if lower_imm > 0x7FF:  # If lower 12 bits represent a negative number
        upper_imm += 1
        lower_imm -= 4096
    
    return upper_imm, lower_imm

def optimize_li(reg, value):
    """
    Generate more efficient load immediate instructions
    
    Args:
        reg (str): Register to load value into
        value (int): Immediate value to load
    
    Returns:
        str: Optimized assembly instructions
    """
    optimized_code = ""
    
    # Special case for small values that fit in 12 bits
    if -2048 <= value < 2048:
        return f"addi {reg}, x0, {value}\n"
    
    # Get upper and lower immediate values
    upper_imm, lower_imm = convert_rep(value)
    
    # Load upper 20 bits
    if upper_imm != 0:
        optimized_code += f"lui {reg}, {upper_imm}\n"
    
    # Add lower 12 bits if non-zero
    if lower_imm != 0:
        # Use addi for both positive and negative lower immediates
        optimized_code += f"addi {reg}, {reg}, {lower_imm}\n"
    
    return optimized_code



label_index=0
def handle_multiplication(rd, rs1, rs2):
        """
        Implements multiplication using add and shift
        Returns series of supported instructions
        """
        global label_index
        label_prefix = f"__mul_{label_index}"
        label_index += 1
        
        return f"""
            # Multiplication of {rs1} and {rs2}
            addi x26, x0, 0     # Initialize result
            addi x27, x0, 0     # Initialize counter
            add x28, {rs1}, x0  # Copy multiplicand
            add x29, {rs2}, x0  # Copy multiplier
            
            {label_prefix}_loop:
            beq x29, x0, {label_prefix}_done
            andi x30, x29, 1    # Check LSB
            beq x30, x0, {label_prefix}_shift
            add x26, x26, x28   # Add multiplicand to result
            
            {label_prefix}_shift:
            slli x28, x28, 1    # Shift multiplicand left
            srli x29, x29, 1    # Shift multiplier right
            bge x0, x0, {label_prefix}_loop
            
            {label_prefix}_done:
            add {rd}, x26, x0   # Move result to destination
        """

    
def postprocess(asm_code):
    mod_asm_code = ''
    # print(asm_code[:50])
    # print('llllll')
    
    # Process each line
    for line in asm_code.splitlines():
        line = line.strip()
        if not line:
            continue
            
        # Split instruction and operands
        parts = line.split()
        if not parts:
            continue
            
        op = parts[0]
        
        # Handle labels
        if line.endswith(':'):
            if not line.startswith('__'):
                mod_asm_code += f"__{line}\n"
            else:
                mod_asm_code += f"{line}\n"
            continue
            
        # Handle different instructions
        if op == 'mul':
            # mul rd, rs1, rs2
            rd = parts[1].rstrip(',')
            rs1 = parts[2].rstrip(',')
            rs2 = parts[3]
            mod_asm_code += handle_multiplication(rd, rs1, rs2)
            
        elif op == 'j':
            # Convert j to bge x0, x0
            target = parts[1]
            if not target.startswith('__'):
                target = f"__{target}"
            mod_asm_code += f"bge x0, x0, {target}\n"
            
        elif op == 'bltz':
            # Convert bltz x5, label to blt x5, x0, label
            reg = parts[1].rstrip(',')
            target = parts[2]
            if not target.startswith('__'):
                target = f"__{target}"
            mod_asm_code += f"blt {reg}, x0, {target}\n"
            
        elif op == 'li':
            reg = parts[1].rstrip(',')
            value = int(parts[2])
            mod_asm_code += optimize_li(reg, value)
        
        elif op == 'lb':
            # Replace lb with lw and keep the rest of the line
            mod_asm_code += line.replace('lb', 'lw', 1) + "\n"
            
        elif op == 'fli':
            # Handle floating point immediate
            reg = parts[1].rstrip(',')
            value = float(parts[2])
            upper, mid, lower = get_ieee_rep(value)
            mod_asm_code += f"lui x7, {upper}\n"
            mod_asm_code += f"addi x7, x7, {mid}\n"
            mod_asm_code += f"addi x7, x7, {lower}\n"
            mod_asm_code += f"fmv.w.x {reg}, x7\n"
            
        else:
            # Handle labels in branch/jump instructions
            if op in ['beq', 'bne', 'blt', 'bge', 'bltu', 'bgeu', 'jal']:
                parts[-1] = f"__{parts[-1]}" if not parts[-1].startswith('__') else parts[-1]
                mod_asm_code += " ".join(parts) + "\n"
            else:
                mod_asm_code += line + "\n"

    # mod_asm_code = asm_code + '\n'

    # print(mod_asm_code[:50])

    mod_asm_code += f"__array_out_of_bounds:\n"
    mod_asm_code += f"nop\n"
    
    mod_asm_code += f"__END__:\n"
    mod_asm_code += f"nop\n"

    final_asm_code = ''
    enable = False
    for line in mod_asm_code.splitlines():
        if ('.text' in line):
            enable = True
        if (enable):
            final_asm_code += re.sub(r', ', ',', line)
        final_asm_code += '\n'

    final_asm_code = re.sub(r'\n\n', '\n', final_asm_code)
    # print(final_asm_code[:50])
    final_code=''
    for line in final_asm_code.splitlines():
        if('0x' in line):
            hex_val=line.split('0x')[-1]
            int_val=int(hex_val,16)
            final_code+=f"{line.split('0x')[0]}{int_val}\n"
        else:
            final_code+=f"{line}\n"
    return ('.section'+final_code)