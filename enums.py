import enum


class Instructions(enum.Enum):
    push = 'push'
    pop = 'pop'
    function = 'function'
    label = 'label'
    goto = 'goto'
    ret = 'return'
    if_goto = 'if-goto'
    print_stmt = 'print'
    call = 'call'
    scan = 'scan'
    alloc = 'alloc'
    getindex= 'getindex'
    store = 'store'
    delete = 'delete'
    access = 'access'
    mcall = 'mcall'
    end = 'end'
    begin = 'begin'
    createobject = 'createobject'
    cls = 'class'
    pvt = 'private'
    pbc = 'public'
    declare = 'declare'
    mtd = 'method'
    getatr = 'getattribute'
    setatr = 'setattribute'

    Eq = 'eq'
    Lt = 'lt'
    Gt = 'gt'
    Ge = 'ge'
    Le = 'le'
    Neq = 'neq'
    Not = 'not'

    Add = 'add'
    Sub = 'sub'
    Mul = 'mul'
    Div = 'div'
    LShift = 'lshift'
    RShift = 'rshift'
    BitAnd = 'and'
    BitOr = 'or'
    BitXor = 'xor'
    Rem = 'mod'


class Segment(enum.Enum):
    local = 'local'
    argument = 'argument'
    constant = 'constant'
    temp = 'temp'
    data = 'data'


class Datatypes(enum.Enum):
    INT = 'INT'
    FLOAT = 'FLOAT'
    BOOL = 'BOOL'
    CHAR = 'CHAR'
    STR = 'STR'
    PTR = 'PTR'


class Operators(enum.Enum):
    Add = ['add', 'fadd.s']
    Sub = ['sub', 'fsub.s']
    LShift = ['sll']
    RShift = ['srl']
    BitAnd = ['and']
    BitOr = ['or']
    BitXor = ['xor']
    Rem = ['rem']
    Mul = ['mul']
    Div = ['div']

    Plus = '+'
    Minus = '-'
    # Mul = '*'
    # Div = '/'
    # Mod = '%'

    LeftShift = '<<'
    RightShift = '>>'
    LogicalAnd = '&&'
    LogicalOr = '||'
    Gt = ['bgt', 'flt.s', 'special']
    Lt = ['blt', 'flt.s']
    Ge = ['bge', 'fle.s', 'special']
    Le = ['ble', 'fle.s']
    Eq = ['beq', 'feq.s']