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
        self.heap_manager=HeapMemoryManager()
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
        self.text_segment += f"li x5, 10304\n"
        self.text_segment += f"li x6, {self.heap}\n"
        self.text_segment += f"add x6, x8, x6\n"
        self.text_segment += f"sw x5, 0(x6)\n"
        
        # 11328 to 11839 (512, pointer_segment)
        self.text_segment += f"li x5, 11328\n"
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
            elif (segment == Segment.temp.value):
                pointer = self.tmp
            elif (segment == Segment.argument.value):
                pointer = self.arg

            if (datatype == Datatypes.INT.value):
                # self.text_segment += f"lw x5, {-(pointer)}(x8)\n"

                self.text_segment += f"li x5, {(pointer)}\n"
                self.text_segment += f"add x5, x5, x8\n"
                self.text_segment += f"lw x5, 0(x5)\n"

                self.text_segment += f"addi x5, x5, {(index*4+4)}\n"
                self.text_segment += f"lw x5, 0(x5)\n"
                self.text_segment += f"sw x5, 0(x2)\n"
                self.text_segment += f"addi x2, x2, 4\n"
            elif (datatype == Datatypes.CHAR.value or datatype == Datatypes.BOOL.value):
                # self.text_segment += f"lw x5, {-(pointer)}(x8)\n"
                self.text_segment += f"li x5, {(pointer)}\n"
                self.text_segment += f"add x5, x5, x8\n"
                self.text_segment += f"lw x5, 0(x5)\n"

                self.text_segment += f"addi x5, x5, {(index*4+4)}\n"
                self.text_segment += f"lw x5, 0(x5)\n"
                self.text_segment += f"sw x5, 0(x2)\n"
                self.text_segment += f"addi x2, x2, 4\n"
            elif (datatype == Datatypes.FLOAT.value):
                # self.text_segment += f"lw x5, {-(pointer)}(x8)\n"
                self.text_segment += f"li x5, {(pointer)}\n"
                self.text_segment += f"add x5, x5, x8\n"
                self.text_segment += f"lw x5, 0(x5)\n"

                self.text_segment += f"addi x5, x5, {(int(index)*4+4)}\n"
                self.text_segment += f"flw f3, 0(x5)\n"
                self.text_segment += f"fsw f3, 0(x2)\n"
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

        pointer = None
        if (segment == Segment.local.value):
            pointer = self.lcl
        elif (segment == Segment.temp.value):
            pointer = self.tmp
        elif (segment == Segment.argument.value):
            pointer = self.arg


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

            self.text_segment += f"addi x6, x6, {(index*4+4)}\n"
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

            self.text_segment += f"addi x6, x6, {(index*4+4)}\n"
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

            self.text_segment += f"addi x6, x6, {(index*4+4)}\n"
            self.text_segment += f"fsw f3, 0(x6)\n"

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
        elif (operator == Instructions.Mul.value):
            instruction = Operators.Mul.value
        elif (operator == Instructions.Div.value):
            instruction = Operators.Div.value

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

        self.text_segment += f"jalr x28, x5, 0\n"

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
        print("pppppppppppppppps",vm_code,"ppppppppppppppps")
        for line in vm_code.splitlines():
            # print(line)
            line = simple_split(line)
            if (len(line) == 0):
                continue

            if (line[0] == Instructions.Add.value or line[0] == Instructions.Sub.value or line[0] == Instructions.BitAnd.value or
                    line[0] == Instructions.BitOr.value or line[0] == Instructions.BitXor.value or line[0] == Instructions.LShift.value or
                    line[0] == Instructions.RShift.value):
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
    
