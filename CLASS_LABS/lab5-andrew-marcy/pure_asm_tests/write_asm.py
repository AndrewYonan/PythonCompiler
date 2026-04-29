
def asm_prologue():
    return f""".globl main
main:
    pushl %ebp ## save caller's base pointer
    movl %esp, %ebp ## set our base pointer
    pushl %ebx ## save callee saved registers
    pushl %esi
    pushl %edi
"""

def asm_epilogue():
    return """
    popl %edi ## restore callee saved registers
    popl %esi
    popl %ebx
    movl $0, %eax ## set return value
    movl %ebp, %esp ## restore esp
    popl %ebp ## restore ebp (alt. “leave”)
    ret ## jump execution to call site
    """

def test_leal_code():
    return f"""
    
    subl $4, %esp
    leal (%esp), %eax
    pushl $17
    pushl %eax
    call inject_int
    addl $8, %esp
    
    pushl %eax
    call print_any
    add $4, %esp

    """


def is_int():
    return f"""

    pushl $0       
    call inject_bool 
    addl $4, %esp        

    #pushl %eax          
    #call is_int          
    #addl $4, %esp        

    pushl %eax      
    call print_any 
    addl $4, %esp


    """

def inject_bool():
    return f"""

    pushl $17
    call inject_int
    addl $4, %esp

    pushl %eax
    call print_any
    addl $4, %esp

    """
def add_stuff_code():
    return f"""

    """

def list_1(): # creates and prints [1]
    return f"""

    # create list of SIZE 1, stored in ebx
    #========================================================

    pushl $2
    call inject_int
    addl $4, %esp

    pushl %eax
    call create_list
    addl $4, %esp

    pushl %eax
    call inject_big
    addl $4, %esp

    movl %eax, %ebx
    #========================================================


    pushl $0           # INDEX
    call inject_int
    addl $4, %esp
    movl %eax, %ecx

    pushl $68                  #VALUE
    call inject_int
    addl $4, %esp
    movl %eax, %edx

    # Step 4: set_subscript(container, key, val)
    pushl %edx               # push value = 1
    pushl %ecx               # push index = 0
    pushl %ebx               # push container = list
    call set_subscript
    addl $12, %esp

    pushl $1
    call inject_int
    addl $4, %esp
    movl %eax, %ecx

    pushl $102
    call inject_int
    addl $4, %esp
    movl %eax, %edx

    pushl %edx
    pushl %ecx
    pushl %ebx
    call set_subscript
    addl $12, %esp

    pushl %ebx               # push tagged list again
    call print_any
    addl $4, %esp


    """

def sum_list():
    return f"""
    
    # create list of SIZE 1, stored in ebx
    #========================================================

    pushl $1
    call inject_int
    addl $4, %esp

    pushl %eax
    call create_list
    addl $4, %esp

    pushl %eax
    call inject_big
    addl $4, %esp

    movl %eax, %ebx
    #========================================================
    
    pushl $0           # INDEX
    call inject_int
    addl $4, %esp
    movl %eax, %ecx

    pushl $68                  #VALUE
    call inject_int
    addl $4, %esp
    movl %eax, %edx

    # Step 4: set_subscript(container, key, val)
    pushl %edx               # push value = 1
    pushl %ecx               # push index = 0
    pushl %ebx               # push container = list
    call set_subscript
    addl $12, %esp
    
    pushl %ebx               # push tagged list again
    call print_any
    addl $4, %esp
    
    #========================================================
    #========================================================
    
    
    # create list of SIZE 1, stored in esi
    #========================================================

    pushl $1
    call inject_int
    addl $4, %esp

    pushl %eax
    call create_list
    addl $4, %esp

    pushl %eax
    call inject_big
    addl $4, %esp

    movl %eax, %esi
    #========================================================
    
    pushl $0           # INDEX
    call inject_int
    addl $4, %esp
    movl %eax, %ecx

    pushl $800                  #VALUE
    call inject_int
    addl $4, %esp
    movl %eax, %edx

    # Step 4: set_subscript(container, key, val)
    pushl %edx               # push value = 1
    pushl %ecx               # push index = 0
    pushl %esi               # push container = list
    call set_subscript
    addl $12, %esp
    
    pushl %esi               # push tagged list again
    call print_any
    addl $4, %esp
    
    
    # SUM
    #========================================================
    
    pushl %esi
    call project_big
    addl $4, %esp
    movl %eax, %esi
    
    pushl %ebx
    call project_big
    addl $4, %esp
    movl %eax, %ebx
    
    pushl %esi
    pushl %ebx
    call add
    addl $8, %esp
    
    pushl %eax
    call inject_big
    addl $4, %esp
    
    pushl %eax
    call print_any
    addl $4, %esp
    

    """

def get_code():
    return asm_prologue() + f"{sum_list()}" + "\n" + asm_epilogue() + "\n"


if __name__ == "__main__":

    dest_asm_file = "../tests/mytests/test1.s"
    x86_code = get_code()
    with open(dest_asm_file, 'w') as dest_file:
        dest_file.write(x86_code)

    print("====WRITTEN x86 CODE====")
    print(x86_code)

