from enums import *
import re
import os


class Preprocess:
    def __init__(self):
        self.label_index = 0

    def get_new_label(self):
        label = '___L'+str(self.label_index)
        self.label_index += 1
        return label

    def preprocess(self, vm_code,functions):

        generator = (i for i in vm_code.splitlines())

        # Neq
        mod_vm_code = ''
        for line in generator:
            line = re.sub(r'LABEL', 'label', line)
            line = re.sub(r'ptr', 'PTR', line)
            line = re.sub(r'gte', 'ge\n', line)
            line = re.sub(r'lte', 'le\n', line)
            split_line = line.split(' ')

            if len(split_line) == 0:
                continue
            
            if line.startswith('JZ,'):
                parts = line.split(',')
                original_label = parts[1].strip()

                # Generate a unique dummy label
                dummy_label = f"{original_label}_no"

                mod_vm_code +=f"if-goto {dummy_label}\n" + f"goto {original_label}\n" + f"label {dummy_label}\n"
            elif split_line[0] == 'lib':
                script_dir = os.path.dirname(__file__)
                lib_path = 'libraries/' + split_line[-1]
                lib_abs_path = os.path.join(script_dir, lib_path)
                
                try:
                    with open(lib_abs_path) as lib_file:
                        mod_vm_code += re.sub(r'lib .*', '', line).strip()
                        mod_vm_code = self.preprocess(lib_file.read(),functions) + mod_vm_code
                        
                    print("IIIIIIIIIIIIIIIIIIIIIIIIIIIIIII")
                except FileNotFoundError:
                    raise FileNotFoundError(f"Missing library: '{split_line[-1]}' not found in libraries directory")

            elif split_line[0] == 'function':
                if len(split_line) == 4 :
                    split_line += ['0'] * (5 - len(split_line))
                    mod_vm_code += f'function {split_line[1]} 10 10 {split_line[3]}\n'
                elif len(split_line) < 5:
                    # Add default values to handle missing elements
                    split_line += ['0'] * (5 - len(split_line))

                    if split_line[2] == '0' and split_line[3] == '0':
                        mod_vm_code += f'function {split_line[1]} 10 10 {split_line[4]}\n'
                    elif split_line[2] == '0':
                        mod_vm_code += f'function {split_line[1]} 10 {split_line[3]} {split_line[4]}\n'
                    elif split_line[3] == '0':
                        mod_vm_code += f'function {split_line[1]} {split_line[2]} 10 {split_line[4]}\n'
                else:
                    mod_vm_code += line + '\n'
                    
                    
                func_name=split_line[1]
                func_args=split_line[2]
                func_type=split_line[3]
                if func_name in functions:
                    if functions[func_name][0]!=func_args or functions[func_name][1]!=func_type:
                        raise ValueError(f"Function {func_name} implementation doesn't match declaration.")
                functions[func_name]=[func_args,func_type]

            elif split_line[0] == Instructions.Neq.value:
                mod_vm_code += f"eq {split_line[-1]}\n"
                line = next(generator)
                label = self.get_new_label()
                mod_vm_code += f"if-goto {label}\n"
                line = re.sub(r'#', '__', line)
                prev_label = line.split(' ')[-1]
                mod_vm_code += f"goto {prev_label}\n"
                mod_vm_code += f"label {label}\n"

            elif split_line[0] == Instructions.Not.value:
                label0 = self.get_new_label()
                label1 = self.get_new_label()
                mod_vm_code += f"push constant 0 {split_line[-1]}\n"
                mod_vm_code += f"eq {split_line[-1]}\n"
                mod_vm_code += f"if-goto {label0}\n"
                mod_vm_code += f"push constant 0 {split_line[-1]}\n"
                mod_vm_code += f"goto {label1}\n"
                mod_vm_code += f"label {label0}\n"
                mod_vm_code += f"push constant 1 {split_line[-1]}\n"
                mod_vm_code += f"label {label1}\n"

            elif '//' in line:
                mod_vm_code += re.sub(r'//.*', '', line).strip()

            elif '#' in line:
                mod_vm_code += re.sub(r'#', '__', line) + '\n'

            elif split_line[0] in ["add", "sub", "mul", "div", "mod"] and len(split_line) < 2:
                mod_vm_code+= f"{split_line[0]} INT\n"
            else:
                mod_vm_code += line + '\n'
        # print("------------modified---",mod_vm_code)
        return mod_vm_code