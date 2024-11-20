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
    value = int(value)
    h = None

    if value < 0:
        h = hex((1 << 32) + value)
    else:
        h = hex(value)

    h = h.lstrip('0x')

    if (len(h) < 8):
        h = '0'*(8-len(h))+h

    upper = h[:5]
    lower_val = int(h[5:], 16)
    val = lower_val//3
    extra = lower_val-3*val
    return ('0x'+upper, val, extra)

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
            # Handle li conversion
            reg = parts[1].rstrip(',')
            value = int(parts[2])
            upper, val, extra = convert_rep(value)
            mod_asm_code += f"lui {reg}, {upper}\n"
            mod_asm_code += f"addi {reg}, {reg}, {val}\n"
            mod_asm_code += f"addi {reg}, {reg}, {val}\n"
            mod_asm_code += f"addi {reg}, {reg}, {val}\n"
            mod_asm_code += f"addi {reg}, {reg}, {extra}\n"
        
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