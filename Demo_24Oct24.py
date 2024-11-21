from enums import *
from preprocess import *
from postprocess import *
from heap import *

import re

'''TODO:
1) Heap Memory Segment actual implementation(init_mem)
2) Arrays mem alloc using heap/stack(Search in net and implement accordingly)
3) Dynamic Mem alloc like new and delete
4) Structs support
5) Object Oriented Support(Class Objects)
6) Linking strong testing 
'''
def simple_split(line):
    # Use a regular expression to match words or quoted phrases
    parts = re.findall(r'(?:[^\s"]+|"[^"]*")+', line)
    # Remove quotes from the quoted phrases
    return [part.strip('"') for part in parts]

# Example usage
line = 'This is "a test" string'
print(simple_split(line))


class VM_Demo:
    def __init__(self):
        self.sp = 8192
        self.lcl = 8196
        self.arg = 8200
        self.tmp = 8204
        self.heap = 8208
        self.print_start = 8212
        # 8220 for later use
        # start from 8224
        self.pointer_segment=8216
        self.heap_manager=HeapMemoryManager(size=10000)
        self.pointer_count = 0
        self.data_size = {
            'INT': 4,
            'FLOAT': 4,
            'CHAR': 1,
            'BOOL': 1,
            'PTR': 12  # 3 integers: base_address, size, datatype
        }
        self.type_check_label = None
        self.type_dict={'INT': 1, 'FLOAT': 2, 'CHAR': 3, 'BOOL': 4}
        self.text_segment = ".section\n.text\njal x30, joi\n"
        self.prev_operator = None
        self.prev_datatype = None
        self.prev_push_segment = None
        self.label_index = 0
        self.return_type = 'INT'
        self.num_local = 0
        self.num_temp = 0
        self.cur_function = "global"
        self.prev_push_datatype = None
        self.data_segment_start = 0x10010000
        self.data_segment_dict = {}
        self.data_segment = ".section\n.data\n"
        self.demo = True
        self.has_return = False
        self.functions = {}  # Dictionary to store function names and their validity

        self.class_definitions = {}  # Store class definitions
        self.class_methods = {}      # Store methods for each class
        self.class_sizes = {}        # Store object sizes for each class
        self.class_member_offsets = {}  # Store member variable offsets
        self.current_class_index = 0  # Track current class being defined

        self.current_scope = []
        self.current_context = None  # Can be 'class', 'private', 'public', 'method'

        self.lv_ofst = {}

    def init_mem(self):
        # 8224 to 8735 (512, local)
        self.text_segment += f"li x5, 8224\n"
        self.text_segment += f"li x6, {self.lcl}\n"
        self.text_segment += f"add x6, x8, x6\n"
        self.text_segment += f"sw x5, 0(x6)\n"

        # 8736 to 8767 (32, argument)
        self.text_segment += f"li x5, 8736\n"
        self.text_segment += f"li x6, {self.arg}\n"
        self.text_segment += f"add x6, x8, x6\n"
        self.text_segment += f"sw x5, 0(x6)\n"

        # 8768 to 9279 (512, temp)
        self.text_segment += f"li x5, 8768\n"
        self.text_segment += f"li x6, {self.tmp}\n"
        self.text_segment += f"add x6, x8, x6\n"
        self.text_segment += f"sw x5, 0(x6)\n"

        # 9280 to 10303 (1024, stack)
        self.text_segment += f"li x5, 9280\n"
        self.text_segment += f"li x6, {self.sp}\n"
        self.text_segment += f"add x6, x8, x6\n"
        self.text_segment += f"sw x5, 0(x6)\n"
        
        # 10304 to 11327 (1024, heap)
        ##Latest try: 10304 to 20303 (10000,heap)
        self.text_segment += f"li x5, 10304\n"
        self.text_segment += f"li x6, {self.heap}\n"
        self.text_segment += f"add x6, x8, x6\n"
        self.text_segment += f"sw x5, 0(x6)\n"
        
        # 11328 to 11839 (512, pointer_segment)
        #Latest try: 20304 to 20815
        self.text_segment += f"li x5, 20304\n"
        self.text_segment += f"li x6, {self.pointer_segment}\n"
        self.text_segment += f"add x6, x8, x6\n"
        self.text_segment += f"sw x5, 0(x6)\n"

        self.text_segment += f"li x5, 262144\n"
        self.text_segment += f"li x6, {self.print_start}\n"
        self.text_segment += f"add x6, x8, x6\n"
        self.text_segment += f"sw x5, 0(x6)\n"

        self.text_segment += f"li x2, 9280\n"
        self.text_segment += f"add x2, x2, x8\n\n"

    def label(self, line):
        """
        label L1
        """
        self.text_segment += f"{line[-1]}:\n"

    def get_new_label(self):
        label = '___CL'+str(self.label_index)
        self.label_index += 1
        return label

    def goto(self, line):
        """
        goto L0
        """
        self.text_segment += f"jal x30, {line[-1]}\n"
        
    def alloc(self, line):
        """
        alloc 10 INT
        Allocates memory in heap and pushes pointer triplet to stack
        """
        size = int(line[1])
        datatype = line[2]
        required_bytes = size * self.data_size[datatype]
        
        # Align to 4 bytes
        if required_bytes % 4 != 0:
            required_bytes += 4 - (required_bytes % 4)
            
        base_address = self.heap_manager.first_fit(required_bytes)
        if base_address is None:
            raise Exception("Out of memory")
            
        # Store pointer information
        self.text_segment += f"# Storing pointer information\n"
        self.text_segment += f"li x5, {self.pointer_segment}\n"
        self.text_segment += f"add x5, x5, x8\n"
        self.text_segment += f"lw x6, 0(x5)\n"  # Current pointer segment position
        
        # Store triplet (base_address, size, datatype)
        type_code = self.type_dict[datatype]
        
        self.text_segment += f"li x7, {base_address}\n"
        self.text_segment += f"sw x7, 0(x6)\n"
        self.text_segment += f"li x7, {size}\n"
        self.text_segment += f"sw x7, 4(x6)\n"
        self.text_segment += f"li x7, {type_code}\n"
        self.text_segment += f"sw x7, 8(x6)\n"
        
        # Update pointer segment position
        self.text_segment += f"addi x6, x6, 12\n"
        self.text_segment += f"sw x6, 0(x5)\n"
        
        # Push triplet to stack
        self.text_segment += f"# Pushing pointer triplet to stack\n"
        self.text_segment += f"li x5, {base_address}\n"
        self.text_segment += f"sw x5, 0(x2)\n"
        self.text_segment += f"addi x2, x2, 4\n"
        self.text_segment += f"li x5, {size}\n"
        self.text_segment += f"sw x5, 0(x2)\n"
        self.text_segment += f"addi x2, x2, 4\n"
        self.text_segment += f"li x5, {type_code}\n"
        self.text_segment += f"sw x5, 0(x2)\n"
        self.text_segment += f"addi x2, x2, 4\n"

    def getindex(self, line):
        """
        getindex
        Calculates array index address from pointer and index
        Uses x20-x25 for temporary storage to avoid conflicts
        """
        self.text_segment += f"# Calculate array index address\n"
        # Pop index
        self.text_segment += f"addi x2, x2, -4\n"
        self.text_segment += f"lw x20, 0(x2)\n"  # Index in x20
        
        # Pop pointer triplet (using x21-x23 for storage)
        self.text_segment += f"addi x2, x2, -12\n"
        self.text_segment += f"lw x21, 0(x2)\n"  # Base address in x21
        self.text_segment += f"lw x22, 4(x2)\n"  # Size in x22
        self.text_segment += f"lw x23, 8(x2)\n"  # Type code in x23
        
        # Check bounds
        self.text_segment += f"bge x20, x22, array_out_of_bounds\n"
        self.text_segment += f"bltz x20, array_out_of_bounds\n"
        
        # Calculate offset based on type
        self.text_segment += f"# Determine element size based on type\n"
        # x24 will store element size
        self.text_segment += f"li x24, 0\n"  # Initialize element size
        
        self.text_segment += f"jal x1, type_check\n"
        
        
        # # Calculation of final address
        # self.text_segment += f"type_calculate_address:\n"
        self.text_segment += f"mul x20, x20, x24\n"  # Multiply index by element size
        self.text_segment += f"add x20, x20, x21\n"
        # Push calculated address
        self.text_segment += f"sw x20, 0(x2)\n"
        self.text_segment += f"addi x2, x2, 4\n"

    def store(self, line):
        """
        store INT
        Stores value at calculated address
        Uses x20-x21 for temporary storage
        """
        datatype = line[1]
        self.text_segment += f"# Store value at address\n"
        
        # Pop value and address
        self.text_segment += f"addi x2, x2, -4\n"
        self.text_segment += f"lw x20, 0(x2)\n"  # Value in x20
        self.text_segment += f"addi x2, x2, -4\n"
        self.text_segment += f"lw x21, 0(x2)\n"  # Address in x21
        
        if datatype == 'INT' or datatype == 'PTR':
            self.text_segment += f"sw x20, 0(x21)\n"
        elif datatype == 'FLOAT':
            self.text_segment += f"fmv.s.x f0, x20\n"
            self.text_segment += f"fsw f0, 0(x21)\n"
        elif datatype == 'CHAR' or datatype == 'BOOL':
            self.text_segment += f"sb x20, 0(x21)\n"

    def access(self, line):
        """
        access INT
        Retrieves value from calculated address and pushes it onto stack
        Uses x20-x21 for temporary storage
        """
        datatype = line[1]
        self.text_segment += f"# Access value at address\n"
        
        # Pop address
        self.text_segment += f"addi x2, x2, -4\n"
        self.text_segment += f"lw x21, 0(x2)\n"  # Address in x21
        
        # Load value based on datatype
        if datatype == 'INT' or datatype == 'PTR':
            self.text_segment += f"lw x20, 0(x21)\n"
        elif datatype == 'FLOAT':
            self.text_segment += f"flw f0, 0(x21)\n"
            self.text_segment += f"fmv.x.w x20, f0\n"
        elif datatype == 'CHAR' or datatype == 'BOOL':
            self.text_segment += f"lb x20, 0(x21)\n"
        
        # Push value onto stack
        self.text_segment += f"sw x20, 0(x2)\n"
        self.text_segment += f"addi x2, x2, 4\n"


    def begin_class(self, line):
        """
        Begin class definition
        Syntax: class <class_number>
        """
        class_number = int(line[1])
        self.current_class_index = class_number
        
        # Initialize class-related data structures
        self.class_definitions[class_number] = {
            'private_members': [],
            'public_members': [],
            'methods': {}
        }
        self.class_member_offsets[class_number] = {}
        self.class_methods[class_number] = {}
        
        # Start tracking class scope
        self.text_segment += f"# Begin class {class_number} definition\n"

    def declare_member(self, line):
        """
        Declare class member variable
        Syntax: declare local <offset> <type>
        """
        # Get current class being defined
        class_number = self.current_class_index
        offset = int(line[2])
        datatype = line[3]
        
        # Track member in class definition
        current_def = self.class_definitions[class_number]
        
        # Determine if private or public based on previous context (assumed to be tracked externally)
        member_list = current_def['private_members'] if self.prev_operator == 'private' else current_def['public_members']
        member_list.append((offset, datatype))
        
        # Calculate offset within the object
        current_offset = 0
        for prev_offset, prev_type in member_list[:-1]:
            current_offset += self.data_size[prev_type]
        
        # Store the offset for this member
        self.class_member_offsets[class_number][offset] = current_offset
        
        self.text_segment += f"# Declared member {offset} of type {datatype} at offset {current_offset}\n"

    def method_begin(self, line):
        """
        Begin method definition for a class
        Syntax: method <method_name> <num_args> <return_type>
        """
        class_number = self.current_class_index
        method_name = line[1]
        num_args = int(line[2])
        return_type = line[3]
        
        # Store method information
        self.class_methods[class_number][method_name] = {
            'num_args': num_args,
            'return_type': return_type
        }
        
        # Generate a unique label for the method
        method_label = f"class_{class_number}_method_{method_name}"
        
        self.text_segment += f"# Begin method {method_name} for class {class_number}\n"
        self.text_segment += f"{method_label}:\n"

    def create_object(self, line):
        """
        Create an object of a specific class
        Syntax: createobject <class_number> <num_args>
        """
        class_number = int(line[1])
        num_args = int(line[2])
        
        # Determine object size
        object_size = 0
        if f'C_{class_number}' not in self.class_sizes:
            # Calculate object size based on member variables
            class_def = self.class_definitions[class_number]
            for _, datatype in class_def['private_members'] + class_def['public_members']:
                object_size += self.data_size[datatype]
            
            # Store the calculated size with C_ prefix
            self.class_sizes[f'C_{class_number}'] = object_size
        else:
            object_size = self.class_sizes[f'C_{class_number}']
        
        # Allocate memory for the object
        self.text_segment += f"# Create object of class {class_number}\n"
        # Generate assembly for allocation (similar to existing alloc method)
        # Note: This assumes the alloc method can handle a custom type
        base_address = self.heap_manager.first_fit(object_size)
        if base_address is None:
            raise Exception("Out of memory")
        
        # Store pointer information similar to alloc method
        self.text_segment += f"# Storing object pointer information\n"
        self.text_segment += f"li x5, {self.pointer_segment}\n"
        self.text_segment += f"add x5, x5, x8\n"
        self.text_segment += f"lw x6, 0(x5)\n"  # Current pointer segment position
        
        # Store triplet (base_address, size, datatype)
        type_code = self.type_dict.get(f'C_{class_number}', 5)  # Custom type code for classes
        
        self.text_segment += f"li x7, {base_address}\n"
        self.text_segment += f"sw x7, 0(x6)\n"
        self.text_segment += f"li x7, {object_size}\n"
        self.text_segment += f"sw x7, 4(x6)\n"
        self.text_segment += f"li x7, {type_code}\n"
        self.text_segment += f"sw x7, 8(x6)\n"
        
        # Update pointer segment position
        self.text_segment += f"addi x6, x6, 12\n"
        self.text_segment += f"sw x6, 0(x5)\n"
        
        # Push triplet to stack
        self.text_segment += f"# Pushing object pointer triplet to stack\n"
        self.text_segment += f"li x5, {base_address}\n"
        self.text_segment += f"sw x5, 0(x2)\n"
        self.text_segment += f"addi x2, x2, 4\n"
        self.text_segment += f"li x5, {object_size}\n"
        self.text_segment += f"sw x5, 0(x2)\n"
        self.text_segment += f"addi x2, x2, 4\n"
        self.text_segment += f"li x5, {type_code}\n"
        self.text_segment += f"sw x5, 0(x2)\n"
        self.text_segment += f"addi x2, x2, 4\n"

    def method_call(self, line):
        """
        Call a method on an object
        Syntax: mcall <method_name> <num_args> <return_type>
        """
        method_name = line[1]
        num_args = int(line[2])
        return_type = line[3]
        
        # Pop object pointer from stack
        self.text_segment += f"# Method call for {method_name}\n"
        self.text_segment += f"addi x2, x2, -12\n"
        self.text_segment += f"lw x20, 0(x2)\n"  # Base address of object
        self.text_segment += f"lw x21, 4(x2)\n"  # Object size
        self.text_segment += f"lw x22, 8(x2)\n"  # Object type code
        
        # Verify method exists for this object's class
        # Note: This would ideally be a more complex type check
        found_method = False
        for class_number, methods in self.class_methods.items():
            if method_name in methods:
                method_info = methods[method_name]
                if method_info['num_args'] == num_args and method_info['return_type'] == return_type:
                    # Generate method call
                    method_label = f"class_{class_number}_method_{method_name}"
                    self.text_segment += f"jal x1, {method_label}\n"
                    found_method = True
                    break
        
        if not found_method:
            raise Exception(f"Method {method_name} not found or type mismatch")


    def getattribute(self, line):
        """
        getattribute <class_number> <attribute_number> <type>
        Retrieves the value of the specified attribute from an object
        Uses x20-x24 for temporary storage to avoid conflicts

        Even though class number can be calculated programmatically, we cant really use the assembly value
        here in python to get the offset(the offsets arent there in assembly) so classnumber has to be included
        """
        class_number = int(line[1])
        attribute_number = int(line[2])
        attribute_type = line[3]
        
        self.text_segment += f"# Get attribute {attribute_number} of type {attribute_type}\n"
        
        # Pop object pointer triplet (using x20-x22 for storage)
        self.text_segment += f"addi x2, x2, -12\n"
        self.text_segment += f"lw x20, 0(x2)\n"  # Base address in x20
        self.text_segment += f"lw x21, 4(x2)\n"  # Size in x21
        self.text_segment += f"lw x22, 8(x2)\n"  # Type code in x22
        
        
        # Get the class number from the type code
        self.text_segment += f"addi x22, x22, -5\n"  # Convert type code to class number
        
        # Calculate attribute offset based on class member offsets
        offset = self.class_member_offsets[class_number][attribute_number]
        self.text_segment += f"# Calculate attribute offset\n"
        self.text_segment += f"li x23, {offset}\n"
        self.text_segment += f"add x24, x20, x23\n"  # x24 now has the address of the attribute
        
        # Load the attribute value based on its type
        self.text_segment += f"# Load attribute value based on type\n"
        if attribute_type == 'INT' or attribute_type == 'PTR':
            self.text_segment += f"lw x20, 0(x24)\n"
        elif attribute_type == 'FLOAT':
            self.text_segment += f"flw f0, 0(x24)\n"
            self.text_segment += f"fmv.x.w x20, f0\n"
        elif attribute_type == 'CHAR' or attribute_type == 'BOOL':
            self.text_segment += f"lb x20, 0(x24)\n"
        
        # Push the loaded value onto the stack
        self.text_segment += f"# Push attribute value to stack\n"
        self.text_segment += f"sw x20, 0(x2)\n"
        self.text_segment += f"addi x2, x2, 4\n"
        
    def setattribute(self, line):
        """
        setattribute <class_number> <attribute_number> <type>
        Sets the value of the specified attribute in an object
        Uses x20-x24 for temporary storage to avoid conflicts
        """
        class_number = int(line[1])
        attribute_number = int(line[2])
        attribute_type = line[3]
        
        self.text_segment += f"# Set attribute {attribute_number} of type {attribute_type}\n"
        
        # Pop value to be set
        self.text_segment += f"addi x2, x2, -4\n"
        self.text_segment += f"lw x20, 0(x2)\n"  # Value to set in x20
        
        # Pop object pointer triplet (using x21-x23 for storage)
        self.text_segment += f"addi x2, x2, -12\n"
        self.text_segment += f"lw x21, 0(x2)\n"  # Base address in x21
        self.text_segment += f"lw x22, 4(x2)\n"  # Size in x22
        self.text_segment += f"lw x23, 8(x2)\n"  # Type code in x23
        
        
        # Get the class number from the type code
        self.text_segment += f"addi x23, x23, -5\n"  # Convert type code to class number
        
        # Calculate attribute offset based on class member offsets
        offset = self.class_member_offsets[class_number][attribute_number]
        self.text_segment += f"# Calculate attribute offset\n"
        self.text_segment += f"li x24, {offset}\n"
        self.text_segment += f"add x24, x21, x24\n"  # x24 now has the address of the attribute
        
        # Store the value based on its type
        self.text_segment += f"# Store attribute value based on type\n"
        if attribute_type == 'INT' or attribute_type == 'PTR':
            self.text_segment += f"sw x20, 0(x24)\n"
        elif attribute_type == 'FLOAT':
            self.text_segment += f"fmv.s.x f0, x20\n"
            self.text_segment += f"fsw f0, 0(x24)\n"
        elif attribute_type == 'CHAR' or attribute_type == 'BOOL':
            self.text_segment += f"sb x20, 0(x24)\n"


    def push(self, line):
        """
        push local 4 INT
        push constant -5.6 FLOAT
        push constant 'c' CHAR
        push constant true BOOL
        """
        segment = line[1]
        self.prev_push_segment = segment
        datatype = line[-1]
        index = 0
        offset = 0
        self.prev_push_datatype = datatype

        if (segment != Segment.constant.value):
            index = int(line[2])
        else:
            if (datatype == Datatypes.INT.value or datatype == Datatypes.BOOL.value):
                index = int(line[2])
            elif (datatype == Datatypes.CHAR.value):
                if (segment == Segment.constant.value):
                    index = ord(line[2])
                else:
                    index = int(line[2])
            elif (datatype == Datatypes.FLOAT.value):
                index = float(line[2])
            elif (datatype == Datatypes.STR.value):
                index = int(line[2])

        if (segment == Segment.data.value):
            if (len(line) == 5):
                string_val = '"'+line[-2]+'"'
                var = f"__{self.cur_function}__data{index}"
                string_val = string_val[1:-1].replace(
                    "\\/", "/").encode().decode('unicode_escape')
                length = len(string_val)
                self.data_segment_dict[var] = [
                    ".asciz", line[-2], self.data_segment_start, length]
                self.data_segment_start += length+1
            else:
                # perform printing here itself
                if (self.demo):
                    var_name = f"__{self.cur_function}__data{index}"
                    total = hex(self.data_segment_dict[var_name][2])[2:]
                    upper, mid, lower = get_ieee_rep(None, total)

                    self.text_segment += f"lui a0, {upper}\n"
                    self.text_segment += f"addi a0, a0, {mid}\n"
                    self.text_segment += f"addi a0, a0, {lower}\n"
                    self.text_segment += "addi a7, x0, 4\necall\n"
                else:
                    var_name = f"__{self.cur_function}__data{index}"
                    total = hex(self.data_segment_dict[var_name][2])[2:]
                    upper, mid, lower = get_ieee_rep(None, total)

                    self.text_segment += f"lui x5, {upper}\n"
                    self.text_segment += f"addi x5, x5, {mid}\n"
                    self.text_segment += f"addi x5, x5, {lower}\n"

                    for i in self.data_segment_dict[var_name][1].lstrip('"').rstrip('"'):
                        self.text_segment += f"li x6, {ord(i)}\n"
                        self.text_segment += f"li x7, {self.print_start}\n"
                        self.text_segment += f"lw x30, 0(x7)\n"
                        self.text_segment += f"li x28, 1\n"
                        self.text_segment += f"sw x28, 0(x30)\n"
                        self.text_segment += f"addi x30, x30, 4\n"
                        
                        self.text_segment += f"sw x6, 0(x30)\n"
                        self.text_segment += f"addi x30, x30, 4\n"
                        self.text_segment += f"sw x30, 0(x7)\n"

                    self.text_segment += f"li x7, {self.print_start}\n"
                    self.text_segment += f"lw x30, 0(x7)\n"
                    self.text_segment += f"li x28, 1\n"
                    self.text_segment += f"sw x28, 0(x30)\n"
                    self.text_segment += f"addi x30, x30, 4\n"

                    self.text_segment += f"sw x0, 0(x30)\n"
                    self.text_segment += f"addi x30, x30, 4\n"
                    self.text_segment += f"sw x30, 0(x7)\n"

        elif (segment != Segment.constant.value):
            pointer = None
            if (segment == Segment.local.value):
                pointer = self.lcl
                dict = self.lv_ofst[self.cur_function]
                if index in dict:
                    offset = dict[index]
                if index + 1 not in dict:
                    next_offset = offset + self.data_size[datatype]
                    dict[index + 1] = next_offset
                print(f"{pointer} + {offset} at index: {index}")
            elif (segment == Segment.temp.value):
                pointer = self.tmp
                offset = index * 4
            elif (segment == Segment.argument.value):
                pointer = self.arg
                offset = index*4
            
            if (datatype == Datatypes.INT.value):
                # self.text_segment += f"lw x5, {-(pointer)}(x8)\n"

                self.text_segment += f"li x5, {(pointer)}\n"
                self.text_segment += f"add x5, x5, x8\n"
                self.text_segment += f"lw x5, 0(x5)\n"
                
                self.text_segment += f"addi x5, x5, {(offset+4)}\n"
                self.text_segment += f"lw x5, 0(x5)\n"
                self.text_segment += f"sw x5, 0(x2)\n"
                self.text_segment += f"addi x2, x2, 4\n"
            elif (datatype == Datatypes.CHAR.value or datatype == Datatypes.BOOL.value):
                # self.text_segment += f"lw x5, {-(pointer)}(x8)\n"
                self.text_segment += f"li x5, {(pointer)}\n"
                self.text_segment += f"add x5, x5, x8\n"
                self.text_segment += f"lw x5, 0(x5)\n"

                self.text_segment += f"addi x5, x5, {(offset+4)}\n"
                self.text_segment += f"lw x5, 0(x5)\n"
                self.text_segment += f"sw x5, 0(x2)\n"
                self.text_segment += f"addi x2, x2, 4\n"
            elif (datatype == Datatypes.FLOAT.value):
                # self.text_segment += f"lw x5, {-(pointer)}(x8)\n"
                self.text_segment += f"li x5, {(pointer)}\n"
                self.text_segment += f"add x5, x5, x8\n"
                self.text_segment += f"lw x5, 0(x5)\n"

                self.text_segment += f"addi x5, x5, {(offset+4)}\n"
                self.text_segment += f"flw f3, 0(x5)\n"
                self.text_segment += f"fsw f3, 0(x2)\n"
                self.text_segment += f"addi x2, x2, 4\n"
            elif (datatype ==Datatypes.PTR.value):
                for i in range(3):
                    self.text_segment += f"li x5, {pointer}\n"
                    self.text_segment += f"add x5, x5, x8\n"
                    self.text_segment += f"lw x5, 0(x5)\n"
                    
                    # Load each integer from consecutive offsets
                    self.text_segment += f"addi x5, x5, {(offset +4+ i*4)}\n"
                    self.text_segment += f"lw x5, 0(x5)\n"
                    
                    # Store on stack
                    self.text_segment += f"sw x5, 0(x2)\n"
                    self.text_segment += f"addi x2, x2, 4\n"
            # self.text_segment += "\n"

        elif (segment == Segment.constant.value):
            constant = index
            if (datatype == Datatypes.INT.value):
                self.text_segment += f"li x5, {constant}\n"
                self.text_segment += f"sw x5, 0(x2)\n"
                self.text_segment += f"addi x2, x2, 4\n"
            elif (datatype == Datatypes.CHAR.value):
                self.text_segment += f"li x5, {constant}\n"
                self.text_segment += f"sw x5, 0(x2)\n"
                self.text_segment += f"addi x2, x2, 4\n"
            elif (datatype == Datatypes.BOOL.value):
                self.text_segment += f"li x5, {1 if line[2]=='true' else 0}\n"
                self.text_segment += f"sw x5, 0(x2)\n"
                self.text_segment += f"addi x2, x2, 4\n"
            elif (datatype == Datatypes.FLOAT.value):
                self.text_segment += f"fli f3, {constant}\n"
                self.text_segment += f"fsw f3, 0(x2)\n"
                self.text_segment += f"addi x2, x2, 4\n"

            # self.text_segment += "\n"
        else:
            self.text_segment += f"addi x2, x2, -4\n"
            self.text_segment += f"lw x5, 0(x2)\n"
            self.text_segment += f"li x6, {self.lcl}\n"
            self.text_segment += f"lw x6, 0(x6)\n"
            self.text_segment += f"add x6, x6, x5\n"
            self.text_segment += f"lw x7, 0(x6)\n"
            self.text_segment += f"sw x7, 0(x2)\n"
            self.text_segment += f"addi x2, x2, 4\n"

        # self.text_segment += "\n"

    def pop(self, line):
        """
        pop local 4 INT
        pop temp 0 CHAR
        """
        segment = line[1]
        datatype = line[-1]
        index = int(line[2])
        offset = 0
        pointer = None
        if (segment == Segment.local.value):
            pointer = self.lcl
            dict = self.lv_ofst[self.cur_function]
            if index in dict:
                offset = dict[index]
            if index + 1 not in dict:
                next_offset = offset + self.data_size[datatype]
                dict[index + 1] = next_offset
            print(f"{pointer} + {offset} at index: {index}")
        elif (segment == Segment.temp.value):
            pointer = self.tmp
            offset = index*4
        elif (segment == Segment.argument.value):
            pointer = self.arg
            offset = index*4


        if (datatype == Datatypes.INT.value):
            self.text_segment += f"addi x2, x2, -4\n"

            if (self.prev_push_datatype == Datatypes.FLOAT.value):
                self.text_segment += f"flw f3, 0(x2)\n"
                self.text_segment += f"fcvt.w.s x5, f3\n"
            else:
                self.text_segment += f"lw x5, 0(x2)\n"

            # self.text_segment += f"lw x6, {-(pointer)}(x8)\n"

            self.text_segment += f"li x6, {pointer}\n"
            self.text_segment += f"add x6, x6, x8\n"
            self.text_segment += f"lw x6, 0(x6)\n"

            self.text_segment += f"addi x6, x6, {(offset+4)}\n"
            self.text_segment += f"sw x5, 0(x6)\n"
        elif (datatype == Datatypes.CHAR.value or datatype == Datatypes.BOOL.value):
            self.text_segment += f"addi x2, x2, -4\n"
            if (self.prev_push_datatype == Datatypes.FLOAT.value):
                self.text_segment += f"flw f3, 0(x2)\n"
                self.text_segment += f"fcvt.w.s x5, f3\n"
                self.text_segment += f"sw x5, 0(x2)\n"
                self.text_segment += f"lw x5, 0(x2)\n"
            else:
                self.text_segment += f"lw x5, 0(x2)\n"

            # self.text_segment += f"lw x6, {-(pointer)}(x8)\n"
            self.text_segment += f"li x6, {pointer}\n"
            self.text_segment += f"add x6, x6, x8\n"
            self.text_segment += f"lw x6, 0(x6)\n"

            self.text_segment += f"addi x6, x6, {(offset+4)}\n"
            self.text_segment += f"sw x5, 0(x6)\n"
        elif (datatype == Datatypes.FLOAT.value):
            self.text_segment += f"addi x2, x2, -4\n"
            if (self.prev_push_datatype == Datatypes.INT.value):
                self.text_segment += f"lw x5, 0(x2)\n"
                self.text_segment += f"fcvt.s.w f3, x5\n"
            elif (self.prev_push_datatype == Datatypes.CHAR.value or self.prev_push_datatype == Datatypes.BOOL.value):
                self.text_segment += f"lw x5, 0(x2)\n"
                self.text_segment += f"fcvt.s.w f3, x5\n"
            else:
                self.text_segment += f"flw f3, 0(x2)\n"
            # self.text_segment += f"lw x6, {-(pointer)}(x8)\n"
            self.text_segment += f"li x6, {pointer}\n"
            self.text_segment += f"add x6, x6, x8\n"
            self.text_segment += f"lw x6, 0(x6)\n"

            self.text_segment += f"addi x6, x6, {(offset+4)}\n"
            self.text_segment += f"fsw f3, 0(x6)\n"
        elif (datatype == Datatypes.PTR.value):
             # Pop 3 consecutive integers for pointer in reverse order
            for i in range(2, -1, -1):
                self.text_segment += f"addi x2, x2, -4\n"
                self.text_segment += f"lw x5, 0(x2)\n"
                
                # Load local variable base address
                self.text_segment += f"li x6, {pointer}\n"
                self.text_segment += f"add x6, x6, x8\n"
                self.text_segment += f"lw x6, 0(x6)\n"
                
                # Store to consecutive offsets
                self.text_segment += f"addi x6, x6, {(offset + 4 + i*4)}\n"
                self.text_segment += f"sw x5, 0(x6)\n"
        self.prev_push_datatype = None
        # self.text_segment += '\n'

    def Operator(self, line):
        """
        Add/Sub/LShift/RShift/BitAnd/BitOr/BitXor INT
        Add/Sub FLOAT
        """
        datatype = line[-1]
        operator = line[0]
        instruction = ''
        if (operator == Instructions.Add.value):
            instruction = Operators.Add.value
        elif (operator == Instructions.Sub.value):
            instruction = Operators.Sub.value
        elif (operator == Instructions.LShift.value):
            instruction = Operators.LShift.value
        elif (operator == Instructions.RShift.value):
            instruction = Operators.RShift.value
        elif (operator == Instructions.BitAnd.value):
            instruction = Operators.BitAnd.value
        elif (operator == Instructions.BitOr.value):
            instruction = Operators.BitOr.value
        elif (operator == Instructions.BitXor.value):
            instruction = Operators.BitXor.value
        elif (operator == Instructions.Rem.value):
            instruction = Operators.Rem.value
            # print("Mod")
        elif (operator == Instructions.Mul.value):
            instruction = Operators.Mul.value
            # print("mul")
        elif (operator == Instructions.Div.value):
            instruction = Operators.Div.value
            # print("Div")

        if (datatype == Datatypes.INT.value):
            self.text_segment += f"addi x2, x2, -4\n"
            self.text_segment += f"lw x5, 0(x2)\n"
            self.text_segment += f"addi x2, x2, -4\n"
            self.text_segment += f"lw x6, 0(x2)\n"
            self.text_segment += f"{instruction[0]} x5, x6, x5\n"
            self.text_segment += f"sw x5, 0(x2)\n"
            self.text_segment += f"addi x2, x2, 4\n"
        elif (datatype == Datatypes.CHAR.value):
            self.text_segment += f"addi x2, x2, -4\n"
            self.text_segment += f"lw x5, 0(x2)\n"
            self.text_segment += f"addi x2, x2, -4\n"
            self.text_segment += f"lw x6, 0(x2)\n"
            self.text_segment += f"{instruction[0]} x5, x6, x5\n"
            self.text_segment += f"sw x5, 0(x2)\n"
            self.text_segment += f"addi x2, x2, 4\n"
        elif (datatype == Datatypes.BOOL.value):
            self.text_segment += f"addi x2, x2, -4\n"
            self.text_segment += f"lw x5, 0(x2)\n"
            self.text_segment += f"addi x2, x2, -4\n"
            self.text_segment += f"lw x6, 0(x2)\n"
            self.text_segment += f"{instruction[0]} x5, x6, x5\n"
            self.text_segment += f"sw x5, 0(x2)\n"
            self.text_segment += f"addi x2, x2, 4\n"
        elif (datatype == Datatypes.FLOAT.value):
            if (operator == Instructions.Add.value or operator == Instructions.Sub.value):
                self.text_segment += f"addi x2, x2, -4\n"
                self.text_segment += f"flw f3, 0(x2)\n"
                self.text_segment += f"addi x2, x2, -4\n"
                self.text_segment += f"flw f4, 0(x2)\n"
                self.text_segment += f"{instruction[1]} f3, f4, f3\n"
                self.text_segment += f"fsw f3, 0(x2)\n"
                self.text_segment += f"addi x2, x2, 4\n"
            # float does not have any other operations

        # self.text_segment += '\n'

    def Condtion_builtin(self, line):
        """
        Eq INT
        if (x5 == x6){
            push 1 on top of stack
        }
        else{
            push 0 on top of stack
        }
        Lt INT
        """
        datatype = line[-1]
        condition = line[0]
        branch = 'eq'

        if (condition == Instructions.Eq.value):
            condition = Operators.Eq
            branch = Operators.Eq.value
        elif (condition == Instructions.Lt.value):
            condition = Operators.Lt
            branch = Operators.Lt.value
        elif (condition == Instructions.Ge.value):
            # print("hi")
            condition = Operators.Ge
            branch = Operators.Ge.value

        self.prev_operator = condition

        label1 = self.get_new_label()
        label2 = self.get_new_label()

        if (datatype == Datatypes.INT.value):
            self.text_segment += f"addi x2, x2, -4\n"
            self.text_segment += f"lw x6, 0(x2)\n"      # RHS
            self.text_segment += f"addi x2, x2, -4\n"
            self.text_segment += f"lw x5, 0(x2)\n"      # LHS

            self.text_segment += f"{branch[0]} x5, x6, {label1}\n"
            self.text_segment += f"addi x7, x0, 0\n"
            self.text_segment += f"jal x30, {label2}\n"
            self.text_segment += f"{label1}:\n"
            self.text_segment += f"addi x7, x0, 1\n"
            self.text_segment += f"{label2}:\n"

            # self.text_segment += f"sub x5, x5, x6\n"
            self.text_segment += f"sw x7, 0(x2)\n"
            self.text_segment += f"addi x2, x2, 4\n"
            self.prev_datatype = Datatypes.INT
        elif (datatype == Datatypes.CHAR.value):
            self.text_segment += f"addi x2, x2, -4\n"
            self.text_segment += f"lw x6, 0(x2)\n"      # LHS
            self.text_segment += f"addi x2, x2, -4\n"
            self.text_segment += f"lw x5, 0(x2)\n"      # RHS

            self.text_segment += f"{branch[0]} x5, x6, {label1}\n"
            self.text_segment += f"addi x7, x0, 0\n"
            self.text_segment += f"jal x30, {label2}\n"
            self.text_segment += f"{label1}:\n"
            self.text_segment += f"addi x7, x0, 1\n"
            self.text_segment += f"{label2}:\n"

            # self.text_segment += f"sub x5, x5, x6\n"
            self.text_segment += f"sw x7, 0(x2)\n"
            self.text_segment += f"addi x2, x2, 4\n"
            self.prev_datatype = Datatypes.CHAR
        elif (datatype == Datatypes.BOOL.value):
            self.text_segment += f"addi x2, x2, -4\n"
            self.text_segment += f"lw x6, 0(x2)\n"      # LHS
            self.text_segment += f"addi x2, x2, -4\n"
            self.text_segment += f"lw x5, 0(x2)\n"      # RHS

            self.text_segment += f"{branch[0]} x5, x6, {label1}\n"
            self.text_segment += f"addi x7, x0, 0\n"
            self.text_segment += f"jal x30, {label2}\n"
            self.text_segment += f"{label1}:\n"
            self.text_segment += f"add x7, x0, 1\n"
            self.text_segment += f"{label2}:\n"

            # self.text_segment += f"sub x5, x5, x6\n"
            self.text_segment += f"sw x7, 0(x2)\n"
            self.text_segment += f"addi x2, x2, 4\n"
            self.prev_datatype = Datatypes.BOOL
        # (need to check this conversion properly)
        elif (datatype == Datatypes.FLOAT.value):
            self.text_segment += f"addi x2, x2, -4\n"
            self.text_segment += f"flw f4, 0(x2)\n"      # LHS
            self.text_segment += f"addi x2, x2, -4\n"
            self.text_segment += f"flw f3, 0(x2)\n"      # RHS

            # self.text_segment += f"{branch[1]} f3, f4, {label1}\n"
            self.text_segment += f"{branch[1]} x28, f3, f4\n"
            self.text_segment += f"bne x28, x0, {label1}\n"

            self.text_segment += f"fadd.s f5, f0, f0\n"
            self.text_segment += f"jal x30, {label2}\n"
            self.text_segment += f"{label1}:\n"
            # self.text_segment += f"add.s f5, f0, 1\n"
            self.text_segment += f"fli f5, 1\n"
            self.text_segment += f"{label2}:\n"

            # self.text_segment += f"fsub.s x5, x5, x6\n"
            self.text_segment += f"fsw f5, 0(x2)\n"
            self.text_segment += f"addi x2, x2, 4\n"
            self.prev_datatype = Datatypes.FLOAT

    def LessThanOrEquals(self, line):
        """
        Le INT
        """
        datatype = line[-1]
        self.prev_operator = Operators.Le

        label1 = self.get_new_label()
        label2 = self.get_new_label()

        if (datatype == Datatypes.INT.value):
            self.text_segment += f"addi x2, x2, -4\n"
            self.text_segment += f"lw x6, 0(x2)\n"      # LHS
            self.text_segment += f"addi x2, x2, -4\n"
            self.text_segment += f"lw x5, 0(x2)\n"      # RHS

            self.text_segment += f"blt x5, x6, {label1}\n"
            self.text_segment += f"beq x5, x6, {label1}\n"
            self.text_segment += f"addi x7, x0, 0\n"
            self.text_segment += f"jal x30, {label2}\n"
            self.text_segment += f"{label1}:\n"
            self.text_segment += f"addi x7, x0, 1\n"
            self.text_segment += f"{label2}:\n"

            # self.text_segment += f"sub x5, x5, x6\n"
            self.text_segment += f"sw x7, 0(x2)\n"
            self.text_segment += f"addi x2, x2, 4\n"
            self.prev_datatype = Datatypes.INT
        elif (datatype == Datatypes.CHAR.value):
            self.text_segment += f"addi x2, x2, -4\n"
            self.text_segment += f"lw x6, 0(x2)\n"      # LHS
            self.text_segment += f"addi x2, x2, -4\n"
            self.text_segment += f"lw x5, 0(x2)\n"      # RHS

            self.text_segment += f"blt x5, x6, {label1}\n"
            self.text_segment += f"beq x5, x6, {label1}\n"
            self.text_segment += f"addi x7, x0, 0\n"
            self.text_segment += f"jal x30, {label2}\n"
            self.text_segment += f"{label1}:\n"
            self.text_segment += f"addi x7, x0, 1\n"
            self.text_segment += f"{label2}:\n"

            # self.text_segment += f"sub x5, x5, x6\n"
            self.text_segment += f"sw x7, 0(x2)\n"
            self.text_segment += f"addi x2, x2, 4\n"
            self.prev_datatype = Datatypes.CHAR
        elif (datatype == Datatypes.BOOL.value):
            self.text_segment += f"addi x2, x2, -4\n"
            self.text_segment += f"lw x6, 0(x2)\n"      # LHS
            self.text_segment += f"addi x2, x2, -4\n"
            self.text_segment += f"lw x5, 0(x2)\n"      # RHS

            self.text_segment += f"blt x5, x6, {label1}\n"
            self.text_segment += f"beq x5, x6, {label1}\n"
            self.text_segment += f"addi x7, x0, 0\n"
            self.text_segment += f"jal x30, {label2}\n"
            self.text_segment += f"{label1}:\n"
            self.text_segment += f"addi x7, x0, 1\n"
            self.text_segment += f"{label2}:\n"

            # self.text_segment += f"sub x5, x5, x6\n"
            self.text_segment += f"sw x7, 0(x2)\n"
            self.text_segment += f"addi x2, x2, 4\n"
            self.prev_datatype = Datatypes.BOOL
        # (need to check this conversion properly)
        elif (datatype == Datatypes.FLOAT.value):
            self.text_segment += f"addi x2, x2, -4\n"
            self.text_segment += f"flw f4, 0(x2)\n"      # LHS
            self.text_segment += f"addi x2, x2, -4\n"
            self.text_segment += f"flw f3, 0(x2)\n"      # RHS

            # self.text_segment += f"flt.s f3, f4, {label1}\n"
            self.text_segment += f"flt.s x28, f3, f4\n"
            self.text_segment += f"bne x28, x0, {label1}\n"

            # self.text_segment += f"fle.s f3, f4, {label1}\n"
            self.text_segment += f"fle.s x28, f3, f4\n"
            self.text_segment += f"bne x28, x0, {label1}\n"

            self.text_segment += f"fli f5, 0\n"
            self.text_segment += f"jal x30, {label2}\n"
            self.text_segment += f"{label1}:\n"
            self.text_segment += f"fli f5, 1\n"
            self.text_segment += f"{label2}:\n"

            # self.text_segment += f"fsub.s x5, x5, x6\n"
            self.text_segment += f"fsw f5, 0(x2)\n"
            self.text_segment += f"addi x2, x2, 4\n"
            self.prev_datatype = Datatypes.FLOAT

    def GreaterThan(self, line):
        """
        Gt INT
        """
        datatype = line[-1]
        self.prev_operator = Operators.Gt

        label1 = self.get_new_label()
        label2 = self.get_new_label()

        if (datatype == Datatypes.INT.value):
            self.text_segment += f"addi x2, x2, -4\n"
            self.text_segment += f"lw x6, 0(x2)\n"      # LHS
            self.text_segment += f"addi x2, x2, -4\n"
            self.text_segment += f"lw x5, 0(x2)\n"      # RHS

            self.text_segment += f"blt x5, x6, {label1}\n"
            self.text_segment += f"beq x5, x6, {label1}\n"
            self.text_segment += f"addi x7, x0, 1\n"
            self.text_segment += f"jal x30, {label2}\n"
            self.text_segment += f"{label1}:\n"
            self.text_segment += f"addi x7, x0, 0\n"
            self.text_segment += f"{label2}:\n"

            # self.text_segment += f"sub x5, x5, x6\n"
            self.text_segment += f"sw x7, 0(x2)\n"
            self.text_segment += f"addi x2, x2, 4\n"
            self.prev_datatype = Datatypes.INT
        elif (datatype == Datatypes.CHAR.value):
            self.text_segment += f"addi x2, x2, -4\n"
            self.text_segment += f"lw x6, 0(x2)\n"      # LHS
            self.text_segment += f"addi x2, x2, -4\n"
            self.text_segment += f"lw x5, 0(x2)\n"      # RHS

            self.text_segment += f"blt x5, x6, {label1}\n"
            self.text_segment += f"beq x5, x6, {label1}\n"
            self.text_segment += f"addi x7, x0, 1\n"
            self.text_segment += f"jal x30, {label2}\n"
            self.text_segment += f"{label1}:\n"
            self.text_segment += f"addi x7, x0, 0\n"
            self.text_segment += f"{label2}:\n"

            # self.text_segment += f"sub x5, x5, x6\n"
            self.text_segment += f"sw x7, 0(x2)\n"
            self.text_segment += f"addi x2, x2, 4\n"
            self.prev_datatype = Datatypes.CHAR
        elif (datatype == Datatypes.BOOL.value):
            self.text_segment += f"addi x2, x2, -4\n"
            self.text_segment += f"lw x6, 0(x2)\n"      # LHS
            self.text_segment += f"addi x2, x2, -4\n"
            self.text_segment += f"lw x5, 0(x2)\n"      # RHS

            self.text_segment += f"blt x5, x6, {label1}\n"
            self.text_segment += f"beq x5, x6, {label1}\n"
            self.text_segment += f"addi x7, x0, 1\n"
            self.text_segment += f"jal x30, {label2}\n"
            self.text_segment += f"{label1}:\n"
            self.text_segment += f"addi x7, x0, 0\n"
            self.text_segment += f"{label2}:\n"

            # self.text_segment += f"sub x5, x5, x6\n"
            self.text_segment += f"sw x7, 0(x2)\n"
            self.text_segment += f"addi x2, x2, 4\n"
            self.prev_datatype = Datatypes.BOOL
        # (need to check this conversion properly)
        elif (datatype == Datatypes.FLOAT.value):
            self.text_segment += f"addi x2, x2, -4\n"
            self.text_segment += f"flw f4, 0(x2)\n"      # LHS
            self.text_segment += f"addi x2, x2, -4\n"
            self.text_segment += f"flw f3, 0(x2)\n"      # RHS

            # self.text_segment += f"flt.s f3, f4, {label1}\n"
            self.text_segment += f"flt.s x28, f3, f4\n"
            self.text_segment += f"bne x28, x0, {label1}\n"

            # self.text_segment += f"fle.s f3, f4, {label1}\n"
            self.text_segment += f"fle.s x28, f3, f4\n"
            self.text_segment += f"bne x28, x0, {label1}\n"

            self.text_segment += f"fli f5, 1\n"
            self.text_segment += f"jal x30, {label2}\n"
            self.text_segment += f"{label1}:\n"
            self.text_segment += f"fli f5, 0\n"
            self.text_segment += f"{label2}:\n"

            # self.text_segment += f"fsub.s x5, x5, x6\n"
            self.text_segment += f"fsw f5, 0(x2)\n"
            self.text_segment += f"addi x2, x2, 4\n"
            self.prev_datatype = Datatypes.FLOAT

        # self.text_segment += '\n'

    def if_goto(self, line):
        """
        if-goto L4
        """
        datatype = self.prev_datatype
        label = line[-1]
        if (datatype == Datatypes.INT or datatype == None):
            self.text_segment += f"addi x2, x2, -4\n"
            self.text_segment += f"lw x5, 0(x2)\n"
            self.text_segment += f"li x6, 1\n"
            self.text_segment += f"beq x5, x6, {label}\n"
        elif (datatype == Datatypes.CHAR or datatype == Datatypes.BOOL):
            self.text_segment += f"addi x2, x2, -4\n"
            self.text_segment += f"lw x5, 0(x2)\n"
            self.text_segment += f"li x6, 1\n"
            self.text_segment += f"beq x5, x6, {label}\n"
        # Has to be re-done (the implementation has been changed for eq, lt, ... )
        elif (datatype == Datatypes.FLOAT):
            self.text_segment += f"addi x2, x2, -4\n"
            self.text_segment += f"flw f3, 0(x2)\n"
            # the top of the stack does not store the subtracted value
            # if (len(self.prev_operator.value) == 3):
            # self.text_segment += f"fsub.s f3, f0, f3\n"
            # self.text_segment += f"{self.prev_operator.value[1]} f3, f0, {label}\n"
            self.text_segment += f"fli f4, 1\n"
            # self.text_segment += f"fle.s f3, f4, {label}\n"
            self.text_segment += f"fle.s x28, f3, f4\n"
            self.text_segment += f"bne x28, x0, {label}\n"

        # self.text_segment += '\n'

        # self.prev_datatype = None
        self.prev_operator = None

    def print_stmt(self, line):
        """
        push local 0 INT
        print INT
        """
        datatype = line[-1]
        if (datatype == Datatypes.INT.value):
            self.text_segment += f"addi x2, x2, -4\n"
            self.text_segment += f"lw x5, 0(x2)\n"
            self.text_segment += f"add a0, x5, x0\n"
            self.text_segment += f"addi x2, x2, 4\n"
            self.text_segment += f"li a7, 1\n"
            self.text_segment += "#PRINT PANREN DAA"
            self.text_segment += f"ecall\n"
        elif (datatype == Datatypes.CHAR.value):
            self.text_segment += f"addi x2, x2, -4\n"
            self.text_segment += f"lw x5, 0(x2)\n"
            self.text_segment += f"add a0, x5, x0\n"
            self.text_segment += f"addi x2, x2, 4\n"
            self.text_segment += f"li a7, 11\n"
            self.text_segment += f"ecall\n"
        elif (datatype == Datatypes.BOOL.value):
            self.text_segment += f"addi x2, x2, -4\n"
            # self.text_segment += f"li x5, 0\n"
            self.text_segment += f"lw x5, 0(x2)\n"
            self.text_segment += f"add a0, x5, x0\n"
            self.text_segment += f"addi x2, x2, 4\n"
            self.text_segment += f"li a7, 4\n"
            self.text_segment += f"ecall\n"
        elif (datatype == Datatypes.FLOAT.value):
            self.text_segment += f"addi x2, x2, -4\n"
            self.text_segment += f"flw fa0, 0(x2)\n"
            self.text_segment += f"addi x2, x2, 4\n"
            self.text_segment += f"li a7, 2\n"
            self.text_segment += f"ecall\n"
        elif (datatype == Datatypes.STR.value):
                index = int(line[2])
                if (self.demo):
                    var_name = f"__{self.cur_function}__data{index}"
                    total = hex(self.data_segment_dict[var_name][2])[2:]
                    upper, mid, lower = get_ieee_rep(None, total)

                    self.text_segment += f"lui a0, {upper}\n"
                    self.text_segment += f"addi a0, a0, {mid}\n"
                    self.text_segment += f"addi a0, a0, {lower}\n"
                    self.text_segment += "addi a7, x0, 4\necall\n"
                else:
                    var_name = f"__{self.cur_function}__data{index}"
                    total = hex(self.data_segment_dict[var_name][2])[2:]
                    upper, mid, lower = get_ieee_rep(None, total)

                    self.text_segment += f"lui x5, {upper}\n"
                    self.text_segment += f"addi x5, x5, {mid}\n"
                    self.text_segment += f"addi x5, x5, {lower}\n"

                    for i in self.data_segment_dict[var_name][1].lstrip('"').rstrip('"'):
                        self.text_segment += f"li x6, {ord(i)}\n"
                        self.text_segment += f"li x7, {self.print_start}\n"
                        self.text_segment += f"lw x30, 0(x7)\n"
                        self.text_segment += f"li x28, 1\n"
                        self.text_segment += f"sw x28, 0(x30)\n"
                        self.text_segment += f"addi x30, x30, 4\n"
                        
                        self.text_segment += f"sw x6, 0(x30)\n"
                        self.text_segment += f"addi x30, x30, 4\n"
                        self.text_segment += f"sw x30, 0(x7)\n"

                    self.text_segment += f"li x7, {self.print_start}\n"
                    self.text_segment += f"lw x30, 0(x7)\n"
                    self.text_segment += f"li x28, 1\n"
                    self.text_segment += f"sw x28, 0(x30)\n"
                    self.text_segment += f"addi x30, x30, 4\n"

                    self.text_segment += f"sw x0, 0(x30)\n"
                    self.text_segment += f"addi x30, x30, 4\n"
                    self.text_segment += f"sw x30, 0(x7)\n"

        self.text_segment += '\n'

    def new_print_stmt(self, line):
        datatype = line[-1]
        if (datatype == Datatypes.INT.value or
                datatype == Datatypes.BOOL.value):
            self.text_segment += f"li x5, {self.print_start}\n"
            self.text_segment += f"li x28, 0\n"                     # int 
            self.text_segment += f"lw x30, 0(x5)\n"
            self.text_segment += f"sw x28, 0(x30)\n"
            self.text_segment += f"addi x30, x30, 4\n"

            self.text_segment += f"addi x2, x2, -4\n"
            self.text_segment += f"lw x6, 0(x2)\n"
            self.text_segment += f"addi x2, x2, 4\n"
            self.text_segment += f"sw x6, 0(x30)\n"
            self.text_segment += f"addi x30, x30, 4\n"
            self.text_segment += f"sw x30, 0(x5)\n"
            
        elif (datatype == Datatypes.CHAR.value):
            self.text_segment += f"li x5, {self.print_start}\n"
            self.text_segment += f"li x28, 1\n"                     # char 
            self.text_segment += f"lw x30, 0(x5)\n"
            self.text_segment += f"sw x28, 0(x30)\n"
            self.text_segment += f"addi x30, x30, 4\n"

            self.text_segment += f"addi x2, x2, -4\n"
            self.text_segment += f"lw x6, 0(x2)\n"
            self.text_segment += f"addi x2, x2, 4\n"
            self.text_segment += f"sw x6, 0(x30)\n"
            self.text_segment += f"addi x30, x30, 4\n"
            self.text_segment += f"sw x30, 0(x5)\n"

        elif (datatype == Datatypes.STR.value):
                index = int(line[2])
                if (self.demo):
                    var_name = f"__{self.cur_function}__data{index}"
                    total = hex(self.data_segment_dict[var_name][2])[2:]
                    upper, mid, lower = get_ieee_rep(None, total)

                    self.text_segment += f"lui a0, {upper}\n"
                    self.text_segment += f"addi a0, a0, {mid}\n"
                    self.text_segment += f"addi a0, a0, {lower}\n"
                    self.text_segment += "addi a7, x0, 4\necall\n"
                else:
                    var_name = f"__{self.cur_function}__data{index}"
                    total = hex(self.data_segment_dict[var_name][2])[2:]
                    upper, mid, lower = get_ieee_rep(None, total)

                    self.text_segment += f"lui x5, {upper}\n"
                    self.text_segment += f"addi x5, x5, {mid}\n"
                    self.text_segment += f"addi x5, x5, {lower}\n"

                    for i in self.data_segment_dict[var_name][1].lstrip('"').rstrip('"'):
                        self.text_segment += f"li x6, {ord(i)}\n"
                        self.text_segment += f"li x7, {self.print_start}\n"
                        self.text_segment += f"lw x30, 0(x7)\n"
                        self.text_segment += f"li x28, 1\n"
                        self.text_segment += f"sw x28, 0(x30)\n"
                        self.text_segment += f"addi x30, x30, 4\n"
                        
                        self.text_segment += f"sw x6, 0(x30)\n"
                        self.text_segment += f"addi x30, x30, 4\n"
                        self.text_segment += f"sw x30, 0(x7)\n"

                    self.text_segment += f"li x7, {self.print_start}\n"
                    self.text_segment += f"lw x30, 0(x7)\n"
                    self.text_segment += f"li x28, 1\n"
                    self.text_segment += f"sw x28, 0(x30)\n"
                    self.text_segment += f"addi x30, x30, 4\n"

                    self.text_segment += f"sw x0, 0(x30)\n"
                    self.text_segment += f"addi x30, x30, 4\n"
                    self.text_segment += f"sw x30, 0(x7)\n"

    def function_call(self, line,functions):
        num_args = int(line[-2])
        call_type=line[-1]
        call_args=line[-2]
        func_name = line[1]
        
        if (functions[func_name][0]!=call_args or functions[func_name][1]!=call_type):
            raise ValueError(f"Function {func_name} implementation doesn't match declaration.")

        if (num_args == 0):
            self.push('push constant 0 INT'.split(' '))

        if func_name not in self.functions:
            raise ValueError(f"Linking error: Function '{func_name}' is not defined.")
        
        if not self.functions[func_name]:
            raise ValueError(f"Linking error: Function '{func_name}' lacks a valid return statement.")

        # storing current arg pointer in x7 register
        self.text_segment += f"li x5, {self.arg}\n"
        self.text_segment += f"lw x7, 0(x5)\n"

        # setting arg pointer
        self.text_segment += f"addi x5, x2, {-(num_args+1)*4}\n"
        self.text_segment += f"li x6, {self.arg}\n"
        self.text_segment += f"sw x5, 0(x6)\n"

        # pushing context
        self.text_segment += f"li x5, {self.lcl}\n"
        self.text_segment += f"lw x6, 0(x5)\n"
        self.text_segment += f"sw x6, 0(x2)\n"
        self.text_segment += f"addi x2, x2, 4\n"

        # self.text_segment += f"li x5, -{self.arg}\n"
        # self.text_segment += f"lw x6, 0(x5)\n"
        self.text_segment += f"sw x7, 0(x2)\n"
        self.text_segment += f"addi x2, x2, 4\n"

        self.text_segment += f"li x5, {self.tmp}\n"
        self.text_segment += f"lw x6, 0(x5)\n"
        self.text_segment += f"sw x6, 0(x2)\n"
        self.text_segment += f"addi x2, x2, 4\n"

        self.text_segment += f"li x5, {self.heap}\n"
        self.text_segment += f"lw x6, 0(x5)\n"
        self.text_segment += f"sw x6, 0(x2)\n"
        self.text_segment += f"addi x2, x2, 4\n"

        self.text_segment += f"jal x1, {func_name}\n"
        
    

        # self.text_segment += '\n'

    def function_def(self, line):
        """
        function mult 2 3 FLOAT
        """
                # If a new function starts without a return in the previous one, throw an error
        if self.cur_function!="global" and not self.has_return:
            raise ValueError(f"Linking error: Function '{self.cur_function}' is missing a return statement.")

        print(line)
        # self.num_local = int(line[-3])
        self.num_local = int(line[-2])
        # self.num_temp = int(line[-2])
        self.num_temp = 5
        function = line[1]
        self.cur_function = function
        self.functions[function] = False  # Mark as not yet confirmed valid
        self.has_return = False  # Reset return tracker
        self.lv_ofst[function]  = {}

        if (function == 'joi'):
            self.text_segment += f"{function}:\n"
            self.init_mem()
            # self.text_segment += '\n'
            return

        self.text_segment += f"{function}:\n"
        # storing return address
        self.text_segment += f"sw x1, 0(x2)\n"

        # setting new LCL
        self.text_segment += f"addi x2, x2, 4\n"
        self.text_segment += f"li x5, {self.lcl}\n"
        self.text_segment += f"sw x2, 0(x5)\n"

        # setting new TMP
        self.text_segment += f"addi x6, x2, {self.num_local*4}\n"
        self.text_segment += f"li x5, {self.tmp}\n"
        self.text_segment += f"sw x2, 0(x5)\n"

        # setting new working stack
        self.text_segment += f"addi x2, x2, {(self.num_temp+self.num_local)*4}\n"
        # self.text_segment += '\n'

    def return_call(self, line):
        
        if (self.cur_function == 'joi'):
            self.text_segment += f"jal x30, __END__\n"
            return
        
        if self.cur_function!="global":
            self.has_return = True
            self.functions[self.cur_function] = True  # Mark function as valid

        self.text_segment += f"addi x2, x2, -4\n"
        self.text_segment += f"lw x5, 0(x2)\n"
        self.text_segment += f"li x6, {self.arg}\n"
        self.text_segment += f"lw x6, 0(x6)\n"
        self.text_segment += f"sw x5, 0(x6)\n"

        # self.text_segment += f"addi x2, x2, {(self.num_local+self.num_temp)*4}\n"
        self.text_segment += f"li x5, {self.lcl}\n"
        self.text_segment += f"lw x2, 0(x5)\n"

        self.text_segment += f"lw x5, -8(x2)\n"
        self.text_segment += f"li x6, {self.heap}\n"
        self.text_segment += f"sw x5, 0(x6)\n"
        
        
        self.text_segment += f"lw x5, -12(x2)\n"
        self.text_segment += f"li x6, {self.tmp}\n"
        self.text_segment += f"sw x5, 0(x6)\n"

        self.text_segment += f"lw x7, -16(x2)\n"
        # self.text_segment += f"li x6, -{self.arg}\n"
        # self.text_segment += f"sw x5, 0(x6)\n"

        self.text_segment += f"lw x5, -20(x2)\n"
        self.text_segment += f"li x6, {self.lcl}\n"
        self.text_segment += f"sw x5, 0(x6)\n"

        self.text_segment += f"lw x5, -4(x2)\n"

        self.text_segment += f"li x6, {self.arg}\n"
        self.text_segment += f"lw x2, 0(x6)\n"

        self.text_segment += f"addi x2, x2, 4\n"

        # self.text_segment += f"lw x5, 20(x2)\n"
        self.text_segment += f"li x6, {self.arg}\n"
        self.text_segment += f"sw x7, 0(x6)\n"

        self.text_segment += f"jalr x0, x1, 0\n"


        # self.text_segment += '\n'

    def scan(self, line):
        datatype = line[-1]

        if (datatype == Datatypes.INT.value):
            self.text_segment += "addi a7, x0, 5\necall\n"
            self.text_segment += f"sw a0, 0(x2)\n"

        # taking char input
        elif (datatype == Datatypes.CHAR.value):
            self.text_segment += "addi a7, x0, 12\necall\n"
            self.text_segment += f"sw a0, 0(x2)\n"

        # taking float input
        elif (datatype == Datatypes.FLOAT.value):
            self.text_segment += "addi a7, x0, 6\necall\n"
            self.text_segment += f"fsw fa0, 0(x2)\n"

        self.text_segment += f"addi x2, x2, 4\n"
        self.pop(f"pop {line[1]} {line[2]} {line[3]}".split(' '))



    def generate_type_conversion_code(self):
        # Type conversion code 
        self.text_segment += f"jal x30, __END__\n"
        self.text_segment += f"type_check:\n"
        self.text_segment += f"li x25, 1\n"  # INT type code
        self.text_segment += f"beq x23, x25, type_int\n"
        self.text_segment += f"li x25, 2\n"  # FLOAT type code
        self.text_segment += f"beq x23, x25, type_float\n"
        self.text_segment += f"li x25, 3\n"  # CHAR type code
        self.text_segment += f"beq x23, x25, type_char\n"
        self.text_segment += f"li x25, 4\n"  # BOOL type code
        self.text_segment += f"beq x23, x25, type_bool\n"
        
        self.text_segment += f"type_int:\n"
        self.text_segment += f"li x24, 4\n"
        
        self.text_segment += f"jalr x0, x1, 0\n"  # Use ret to return to the caller
        
        self.text_segment += f"type_float:\n"
        self.text_segment += f"li x24, 4\n"
        self.text_segment += f"jalr x0, x1, 0\n"
        
        self.text_segment += f"type_char:\n"
        self.text_segment += f"li x24, 1\n"
        self.text_segment += f"jalr x0, x1, 0\n"
        
        self.text_segment += f"type_bool:\n"
        self.text_segment += f"li x24, 1\n"
        self.text_segment += f"jalr x0, x1, 0\n"
    
    
    
    def generate_target_code(self, vm_code):

        preprocess = Preprocess()
        functions={}
        vm_code = preprocess.preprocess(vm_code,functions)
        # print("pppppppppppppppps",vm_code,"ppppppppppppppps")
        for line in vm_code.splitlines():
            # print(line)
            line = simple_split(line)
            if (len(line) == 0):
                continue

            if (line[0] == Instructions.Add.value or line[0] == Instructions.Sub.value or line[0] == Instructions.BitAnd.value or
                    line[0] == Instructions.BitOr.value or line[0] == Instructions.BitXor.value or line[0] == Instructions.LShift.value or
                    line[0] == Instructions.RShift.value or line[0] == Instructions.Rem.value or line[0] == Instructions.Mul.value or line[0] == Instructions.Div.value):
                self.Operator(line)
            elif (line[0] == Instructions.Eq.value or line[0] == Instructions.Lt.value or line[0] == Instructions.Ge.value):
                self.Condtion_builtin(line)
            elif (line[0] == Instructions.Le.value):
                self.LessThanOrEquals(line)
            elif (line[0] == Instructions.Gt.value):
                self.GreaterThan(line)
            elif (line[0] == Instructions.push.value):
                self.push(line)
            elif (line[0] == Instructions.pop.value):
                self.pop(line)
            elif (line[0] == Instructions.function.value):
                self.function_def(line)
            elif (line[0] == Instructions.ret.value):
                self.return_call(line)
            elif (line[0] == Instructions.if_goto.value):
                self.if_goto(line)
            elif (line[0] == Instructions.goto.value):
                self.goto(line)
            elif (line[0] == Instructions.label.value):
                self.label(line)
            elif (line[0] == Instructions.print_stmt.value):
                if (self.demo):
                    self.print_stmt(line)
                    # pass
                else:
                    self.new_print_stmt(line)
            elif (line[0] == Instructions.call.value):
                self.function_call(line,functions)
            elif (line[0] == Instructions.scan.value):
                self.scan(line)
                # pass
            elif (line[0] == Instructions.alloc.value):
                self.alloc(line)
            elif (line[0] == Instructions.getindex.value):
                self.getindex(line)
            elif (line[0] == Instructions.store.value):
                self.store(line)
            elif (line[0] == Instructions.access.value):
                self.access(line)

            elif line[0] == Instructions.mcall.value:
                self.method_call(line)
            
            elif line[0] == Instructions.end.value:
                # Handle scope ending
                if self.current_scope:
                    # Pop the last context from scope
                    popped_context = self.current_scope.pop()
                    
                    # Reset current context based on remaining scope
                    if self.current_scope:
                        self.current_context = self.current_scope[-1]
                    else:
                        self.current_context = None
            elif line[0] == Instructions.createobject.value:
                self.create_object(line)

            elif line[0] == Instructions.cls.value:
                self.begin_class(line)
                self.current_context = 'class'
            
            elif line[0] == Instructions.begin.value:
                if len(self.current_scope) == 0 and self.current_context == 'class':
                    self.current_scope.append('class')
                elif self.current_context in ['class', 'public', 'private']:
                    # Push current context to scope
                    self.current_scope.append(self.current_context)
            
            elif line[0] == Instructions.pvt.value:
                self.current_context = 'private'
            
            elif line[0] == Instructions.pbc.value:
                self.current_context = 'public'
            
            elif line[0] == Instructions.declare.value:
                if self.current_context in ['private', 'public']:
                    self.declare_member(line)
            
            elif line[0] == Instructions.mtd.value:
                self.method_begin(line)
                self.current_context = 'method'

            elif line[0] == Instructions.getatr.value:
                self.getattribute(line)
            
            elif line[0] == Instructions.setatr.value:
                self.setattribute(line)

            else:
                print("LABEL", line)

        #Adding the type to byte conversion:
        # Set size based on type
        # self.text_segment += f"type_int:\n"
        # self.text_segment += f"li x24, 4\n"
        # self.text_segment += f"j type_done\n"
        
        # self.text_segment += f"type_float:\n"
        # self.text_segment += f"li x24, 4\n"
        # self.text_segment += f"j type_done\n"
        
        # self.text_segment += f"type_char:\n"
        # self.text_segment += f"li x24, 1\n"
        # self.text_segment += f"j type_done\n"
        
        # self.text_segment += f"type_bool:\n"
        # self.text_segment += f"li x24, 1\n"
        # self.text_segment += f"j type_done\n"
        
        # self.text_segment += f"type_done:\n"
        # # Calculate final address
        # self.text_segment += f"mul x20, x20, x24\n"  # Multiply index by element size
        # self.text_segment += f"add x20, x20, x21\n"  # Add base address
        
        self.generate_type_conversion_code()
    
        self.text_segment =  postprocess(self.text_segment)
        

        sorted_list = sorted(
            self.data_segment_dict.items(), key=lambda x: x[1][2])

        for var, (type, value, _, __) in sorted_list:
            self.data_segment += f"{var}:\n\t{type} \"{value}\"\n"

        final_code = self.data_segment + self.text_segment
        return final_code
    
