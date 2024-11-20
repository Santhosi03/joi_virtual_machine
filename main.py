import sys
import os
from Demo_24Oct24 import VM_Demo

functions={}
def preprocess_main_file(main_code, helper_codes):
    """Process the main file to replace function declarations with actual code from helper files."""
    main_lines = main_code.splitlines()
    processed_code = []
    
    # Helper dictionary to store functions from helper files
    helper_functions = {}
    main_functions={}
    function_name = None
    func_dec={}
    # Parse each helper file to identify functions and store their code
    for line in main_lines:
        tokens = line.split()
        # print(tokens)
        if tokens and tokens[0] == 'function':
                # Store previous function if it exists
                # Start a new function
                function_name = tokens[1]
                # print(tokens)
                if tokens[1]=='joi' and len(tokens) < 4:
                    continue
                func_dec[function_name]=[tokens[2],tokens[3]]
        if tokens and tokens[0]=='return':
                if function_name:
                    if function_name in main_functions:
                        print(main_functions)
                        raise ValueError(f"Multiple declarations of {function_name}")
                    main_functions[function_name] = True
                    
    for helper_code in helper_codes:
        lines = helper_code.splitlines()
        function_name = None
        function_lines = []
        
        for line in lines:
            tokens = line.split()
            if tokens and tokens[0] == 'function':
                # Store previous function if it exists
                # Start a new function
                function_name = tokens[1]
                function_lines = []
            if tokens and tokens[0]=='return':
                if function_name:
                    function_lines.append(line)
                    helper_functions[function_name] = '\n'.join(function_lines)
            elif function_name:
                function_lines.append(line)
        
        # Store the last function from the helper file
        if function_name:
            helper_functions[function_name] = '\n'.join(function_lines)

    # Process each line in the main file, replacing function declarations with helper function code
    # skip_lines = False
    print(f"mainfunctions\n{main_functions}\n helper_functions\n{helper_functions}")
    for line in main_lines:
        tokens = line.split()
        print(tokens,"...............tokens")
        # Check for function declaration in the main file
        if tokens and tokens[0] == 'function' and tokens[1] in helper_functions:
            # Replace function declaration with the actual code from the helper file
            if tokens[1] in main_functions:
                raise ValueError(f"Multiple declarations of {tokens[1]}")
            processed_code.append(helper_functions[tokens[1]])
            print(tokens[1], " 8kk ")
            # skip_lines = True
        # elif tokens and tokens[0] == 'ret':  # End of function in main file
        #     skip_lines = False
        # elif not skip_lines:
        else:
            processed_code.append(line)
    
    return '\n'.join(processed_code)


if __name__ == '__main__':
    # Get paths for the main file and helper files from arguments
    script_dir = os.path.dirname(__file__)
    main_file_path = sys.argv[1]
    save_path='./actual_outputs/'+sys.argv[-1]+'.asm'
    main_abs_path = os.path.join(script_dir, main_file_path)
    
    # Load main file content
    with open(main_abs_path) as main_file:
        main_code = main_file.read()
    
    # Load helper file contents
    helper_codes = []
    for helper_path in sys.argv[2:-1]:
        helper_abs_path = os.path.join(script_dir, helper_path)
        with open(helper_abs_path) as helper_file:
            helper_codes.append(helper_file.read())

    # Process the main file to replace function declarations with helper code
    vm_code = preprocess_main_file(main_code, helper_codes)
    # print(":::::::::",vm_code)

    # Generate the target assembly code
    asm_generator = VM_Demo()
    asm_code = asm_generator.generate_target_code(vm_code)

    # Write output to the specified asm file
    output_path = os.path.join(script_dir, save_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w+') as output_file:
        output_file.write(asm_code)
