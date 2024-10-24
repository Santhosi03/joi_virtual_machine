import sys
import os
from Demo_24Oct24 import VM_Demo

if __name__ == '__main__':
    script_dir = os.path.dirname(__file__)
    rel_path = sys.argv[1]
    abs_file_path = os.path.join(script_dir, rel_path)
    asm_code = ""

    with open(abs_file_path) as file:
        vm_code = file.read()

        # asm_generator = VM()
        print(vm_code)
        asm_generator = VM_Demo()
        # starting point of the virtual machine
        asm_code = asm_generator.generate_target_code(vm_code)

    script_dir = os.path.dirname(__file__)
    rel_path = 'actual_outputs/testcase3.asm'
    abs_file_path = os.path.join(script_dir, rel_path)

    with open(abs_file_path, 'w+') as file:
        file.write(asm_code)