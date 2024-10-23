import enum

class Instructions(enum.Enum):
    # Stack Operations
    ipush = 'ipush'       # Push an integer value onto the stack
    fpush = 'fpush'       # Push a float value onto the stack
    ipop = 'ipop'         # Pop an integer value from the stack
    fpop = 'fpop'         # Pop a float value from the stack
    idup = 'idup'         # Duplicate the top integer value
    fdup = 'fdup'         # Duplicate the top float value
    iswap = 'iswap'       # Swap top two integer values
    fswap = 'fswap'       # Swap top two float values
    i2f = 'i2f'           # Convert integer to float
    f2i = 'f2i'           # Convert float to integer
 
    # Arithmetic Operations
    IAdd = 'iadd'         # Add top two integer values
    ISub = 'isub'         # Subtract second top from top integer value
    IMul = 'imul'         # Multiply top two integer values
    IDiv = 'idiv'         # Divide second top by top integer value
    FAdd = 'fadd'         # Add top two float values
    FSub = 'fsub'         # Subtract second top from top float value
    FMul = 'fmul'         # Multiply top two float values
    FDiv = 'fdiv'         # Divide second top by top float value
    Mod = 'mod'           # Modulo operation

    # Comparison Operations
    Eq = 'eq'             # Equal
    Neq = 'neq'           # Not Equal
    Lt = 'lt'             # Less Than
    Le = 'le'             # Less Than or Equal
    Gt = 'gt'             # Greater Than
    Ge = 'ge'             # Greater Than or Equal

    # Control Flow
    call = 'call'         # Call a function
    ret = 'return'           # Return from function

    # Memory Operations
    LOAD = 'load'         # Load from memory
    STORE = 'store'       # Store to memory
    ALLOC = 'alloc'       # Allocate memory
    FREE = 'free'         # Free allocated memory

    # Object-Oriented Operations
    NEW = 'new'           # Create a new object
    GETFIELD = 'getfield' # Get object field
    SETFIELD = 'setfield' # Set object field
    VCALL = 'vcall'       # Call a virtual method
    DELETE = 'delete'     # Call destructor and free object memory

    # I/O Operations
    PRINTI = 'printi'     # Print integer
    PRINTF = 'printf'     # Print float
    PRINTS = 'prints'     # Print string
    SCANI = 'scani'       # Scan integer
    SCANF = 'scanf'       # Scan float
    SCANS = 'scans'       # Scan string
    PRINTLNI = 'printlni' # Print integer with newline
    PRINTLNF = 'printlnf'  # Print float with newline
    PRINTLNS = 'printlns'  # Print string with newline
    
    Add = 'add'            # Add operation
    Sub = 'sub'            # Subtract operation        
    And = 'and'            # Bitwise AND
    Or = 'or'              # Bitwise OR
    Not = 'not'            # Logical NOT
    
    MOV = 'mov'            # Move operation
    ENTER = 'enter'        # Enter function
    LEAVE = 'leave'        # Leave function
    SAVE = 'save'          # Save state
    RESTORE = 'restore'    # Restore state
    
    IPUSHI = 'ipushi'      # Push immediate integer
    FPUSHF = 'fpushf'      # Push immediate float
    ADJUSTSP = 'adjustsp'  # Adjust stack pointer
    LOADFP = 'loadfp'      # Load from frame pointer
    STOREFP = 'storefp'    # Store to frame pointer
    
    LOADREL = 'loadrel'    # Load relative to frame pointer
    STOREREL = 'storerel'  # Store relative to frame pointer
    LOADIND = 'loadind'    # Load indirect (pointer dereferencing)
    STOREIND = 'storeind'  # Store indirect (pointer dereferencing)


class Segment(enum.Enum):
    integer_stack = 'int_stack'   # Integer stack for operations and local int variables
    float_stack = 'float_stack'   # Float stack for operations and local float variables
    heap = 'heap'                 # Dynamic memory allocation (objects, arrays, mutable strings)
    static = 'static'             # Static/global variables, string literals, vtables
    string_pool = 'string_pool'   # String constants pool
    code = 'code'                 # Bytecode instructions


class Datatypes(enum.Enum):
    INT = 'INT'           # Integer type
    FLOAT = 'FLOAT'       # Float type
    BOOL = 'BOOL'         # Boolean type
    CHAR = 'CHAR'         # Character type
    STR = 'STR'           # String type


class Operators(enum.Enum):
    Add = ['add', 'fadd.s']      # Add operation
    Sub = ['sub', 'fsub.s']      # Subtract operation
    And = ['and']                 # Bitwise AND
    Or = ['or']                   # Bitwise OR
    Not = ['not']                 # Logical NOT

    Plus = '+'                    # Plus operator
    Minus = '-'                   # Minus operator
    Mul = '*'                     # Multiply operator
    Div = '/'                     # Divide operator
    Mod = '%'                     # Modulo operator

    LogicalAnd = '&&'            # Logical AND
    LogicalOr = '||'             # Logical OR
    LogicalNot = '~'             # Logical NOT
    
    Gt = ['bgt', 'flt.s', 'special']
    Lt = ['blt', 'flt.s']
    Ge = ['bge', 'fle.s', 'special']
    Le = ['ble', 'fle.s']
    Eq = ['beq', 'feq.s']
