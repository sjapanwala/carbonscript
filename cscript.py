#!/usr/bin/env python3
import sys
import getpass, os
import operator
import random

global allowed_types
allowed_types = ["str","int","flt","bool","arr","void"]


# this is where the "envriornmental rules are stored; can be modified with args"
envriornment_config = {
        "showtokens": False,
        "print_error_code": False
        }



variables = {
        "errorlevel" : {
            "cat": "assigned",
            "type": "int",
            "value": 0
            },
        "uname" : {
            "cat": "preset",
            "type": "str",
            "value": getpass.getuser()
            },
        "version": {
            "cat": "preset",
            "type": "str",
            "value": "v01.2/25"
            },
        "pi": {
            "cat": "preset",
            "type": "flt",
            "value": 3.14
            },
        "eu": {
            "cat": "preset",
            "type": "flt",
            "value": 2.72
            },
        "iteration" : {
            "cat" : "assigned",
            "type": "int",
            "value": 0
            },
        "rand": {
            "cat": "preset",
            "type": "randint",
            "value": f"randval(1-100)"
            }
    }

methods = {
        "function" : {
            "returntype": "void",
            "params": 0,
            "param_order": [],
            "content" : ["stdout \033[92mHello World!\nCongrats on Summoning Your First Function!\033[0m",],
        },
        "status" : {
            "returntype": "void",
            "params": 0,
            "param_order": [],
            "content" : ["stdout Exited With Status Code ?errorlevel","}"],
        },
        "add" : {
            "returntype": "int",
            "params": 2,
            "param_order": ["$a","$b"],
            'content': ['return ( $a + $b )', '}']  
            },
        "subtract": {
            "returntype": "int",
            "params": 2,
            "param_order": ["$a","$b"],
            'content': ['return ( $a - $b )', '}']
        },
        "multiply": {
            "returntype": "int",
            "params": 2,
            "param_order": ["$a","$b"],
            'content': ['return ( $a * $b )', '}']
        },
        "divide": {
            "returntype": "int",
            "params": 2,
            "param_order": ["$a","$b"],
            'content': ['return ( $a / $b )', '}']
        },
        "square": {
            "returntype": "int",
            "params": 1,
            "param_order": ["$a"],
            'content': ['return ( $a * $a )', '}']
        },
        "cube": {
            "returntype": "int",
            "params": 1,
            "param_order": ["$a"],
            'content': ['return ( $a * $a * $a )', '}']
        },
    }



def tokenization(user_input):
    """
    a simple tokenizer, takes text and converts it to something more readable by the code
    1. increm/decrem        -> to increase or decrease value (no postfix or prefix)
    2. ? (variables)        -> converts ?x into a variable with data
    3. @ (functioncalls)    -> calls functions stored in methods
    4. () (logical)         -> logical and math operations
    """
    try:
        if not user_input:
            return None
        token_array = user_input.split(" ")
        if "increm" in token_array[0]:
            increm(token_array[1:])
        if "decrem" in token_array[0]:
            decrem(token_array[1:])
        for i,token in enumerate(token_array):
            # check for precedence
            if token == "quit":
                exit()
            if "?" in token[0]:
                recovered = deVar(token)
                token_array[i] = recovered
            if token[0] == "@":
                ec,return_val = run_func(token[1:],token_array)
                token_array[i] = return_val[0]
                global func_code
                func_code = ec
        if "(" in token_array:
            token_array = do_math(token_array)
        return token_array
    except Exception as e:
        return ["undefined"]


def increm(tokens):
    for pos_var in tokens:
        if not isinstance(pos_var, int):
            if pos_var[0] == "?" and pos_var[1:] in variables:
                increm_variable = pos_var[1:]
                if variables[increm_variable]['type'] == "int":
                        variable_value = variables[increm_variable]['value']
                        variables[increm_variable]['value'] = int(variable_value) + 1

def decrem(tokens):
    for pos_var in tokens:
        if not isinstance(pos_var, int):
            if pos_var[0] == "?" and pos_var[1:] in variables:
                increm_variable = pos_var[1:]
                if variables[increm_variable]['type'] == "int":
                        variable_value = variables[increm_variable]['value']
                        variables[increm_variable]['value'] = int(variable_value) - 1



# --- START OF THE FILE READING SYSTEM, READING ".car" FILES ONLY ---
file_contents = []
def checkfile(filepath):
    """
    checks the authenticity of the file, and if it ends with ".car"
    """
    if os.path.isfile(filepath):
        if filepath[-4:] != ".car":
            print("\033[91mfile:type error: \033[0mfile must be of type .car")
            return False
        return True
    else:
        print("\033[91mfile:exists error: \033[0mfile does not exist")
        return False

raw_files = []
def open_file(filename):
    with open(filename, "r") as file:
        for line in file:
            file_contents.append(line.strip())
            raw_files.append(line)
    run_file(file_contents)

def run_file(file_contents):
    global file_line
    file_line = 0
    for codeline in file_contents:
        file_line += 1
        tokenizer = tokenization(codeline)
        if codeline in func_ignore:
            continue
        else:
            func_caller(tokenizer)

def func_caller(tokens):
    if envriornment_config["showtokens"] == True:
        print(tokens)
    if tokens == None:
        return 1
    user_input = tokens[0]
    if user_input == "return":
        return 0
    if user_input == "void":
        return 0
    if user_input == "//":
        return 2
    if user_input == "}":
        return 2
    if user_input == "{":
        return 2
    if user_input == "increm":
        return 0
    if user_input == "decrem":
        return 0
    if isinstance(user_input, str):
        pass
    if isinstance(user_input, str):
        if user_input[0:5] == "func;":
            # this calls for function making
            error_code = construct_functions(tokens)
            return error_code
    if isinstance(user_input, str):
        if user_input[0] == "@":
            if user_input[1:] not in methods:
                print(f"\033[91mfunction:call error: \033[0mthe function '{user_input}' does not exist")
                return 1
            else:
                error_code = func_code
                return error_code
    if user_input in globals() and callable(globals()[user_input]):
        error_code = globals()[user_input](list(tokens[1:]))
        return error_code
    else:
        if file_mode:
            print(f"\033[91mstatment:syntax error: \033[0m\033[93m On Line {file_line}\033[0m: '{user_input}' is not recognized.")
        else:
            print(f"\033[91mstatment:syntax error: \033[0m'{user_input}' is not recognized.")
        return 4

def type_check(value):
    if isinstance(value, int):
        return "int"
    elif isinstance(value, str):
        return "str"
    elif isinstance(value, float):
        return "flt"        
    elif isinstance(value, bool):
        return "bool"
    elif isinstance(value, list):
        return "arr"  
    else:
        return "?" 

def add_space(chunk):
    sp_idx = chunk.find("_")
    return chunk[:sp_idx], chunk[sp_idx+1:]

def deVar(variable):
    if variable[1:] in variables:
        var_val = variables[variable[1:]]["value"]
        var_type = variables[variable[1:]]["type"]
        if var_type == "str":
            return str(var_val)
        elif var_type == "int":
            return int(var_val)
        elif var_type == "arr":
            var_val = list(var_val)
            return var_val
        elif var_type == "flt":
            return float(var_val)
        elif var_type == "bool":
            return bool(var_val)
        elif var_type == "randint":
            return random.randint(random_min,random_max)
        else:
            return "\033[90mUndefined\033[0m"
    else:
        return "\033[90mUndefined\033[0m"

def deVarFunc(var):
    if var[1:] in variables:
        var_val = variables[var[1:]]["value"]
        var_type = variables[var[1:]]["type"]
        if var_type == "str":
            return str(var_val)
        elif var_type == "int":
            return int(var_val)
        elif var_type == "arr":
            var_val = list(var_val)
            return var_val
        elif var_type == "flt":
            return float(var_val)
        elif var_type == "bool":
            return bool(var_val)
        else:
            return "\033[90mUndefined\033[0m"
    else:
        return "\033[90mUndefined\033[0m"
    



def run_func(funcname, params):
    #params = params[1:]
    # Get method details
    func_name_idx = params.index(f"@{funcname}")
    params = params[func_name_idx+1:]
    method = methods[funcname]
    
    # Validate parameter count
    if len(params) != method["params"]:
        print(f"\033[91mparameter:syntax error: \033[0mexpected {method['params']}; given {len(params)}")
        return 4, None

    
    # Create parameter hash map
    param_hash = {}
    for var, value in zip(method["param_order"], params):
        param_hash[var] = value
    
    # Create a copy of content to modify
    content = method["content"].copy()
    
    # Replace parameters in content
    for i, line in enumerate(content):
        for var, value in param_hash.items():
            line = line.replace(var, str(value))
        content[i] = line
    
    # Process content
    ec = 1
    returnval = []
    
    for line in content:
        if line == '}':
            continue
        
        if line.startswith('end'):
            ec = line.split()[1]
            continue
        
        if line.startswith('return'):
            returnval = tokenization(line[7:])
            continue
        elif 'return' in line:
            return_index = line.find('return')
            returnval = tokenization(line[return_index+7:])
            continue
        
        # Call function with tokenized line
        tokenizer = tokenization(line)
        func_caller(tokenizer)
    
    # Handle void return type
    if method["returntype"] == "void":
        returnval = ["void"]
    
    return ec, returnval

def construct_functions(tokens):
    # Initial validation checks remain the same
    if tokens[0].find(";") == -1:
        print("\033[91mfunction:type error: \033[0mno return type specified")
        return 3
    else:
        semi_idx = tokens[0].find(';') 
        functype = tokens[0][semi_idx+1:]
        if functype not in allowed_types:
            print("\033[91mfunction:type error: \033[0mreturn type not allowed")
            return 3
        if len(tokens) < 2:
            print("\033[91mfunction:naming error: \033[0mno function name specified")
            return 1
        elif len(tokens) < 3:
            print("\033[91mfunction:syntax error: \033[0mno function intake specified")
            return 4
        elif tokens[-1] != "{":
            print("\033[91mfunction:syntax error: \033[0mno function opener specified")
            return 4
        
        # Function header validation
        func_name = tokens[1]
        func_intake = tokens[2:-1]
        check = []
        for var in func_intake:
            if var[:var.find(";")] not in check:
                check.append(var[:var.find(";")])
            else:
                print("\033[91mfunc:duplicate vars: \033[0mprovided 1 or more duplicate header vars")
                return 1
        check = []

        if func_name in methods:
            print("\033[91mfunction:exists error: \033[0mfunction already exists")
            return 1
            
        for i in func_intake:
            if i != "$void":
                if i[0] != "$":
                    print("\033[91mfunction:syntax error: \033[0mno function intake specified")
                    return 4
            if i.find(";") == -1:
                if i != "$void":
                    print(f"\033[91mfunction:type error: \033[0mno function intake type specified for {i}")
                    return 3

        # Function body reading with proper brace tracking
        function_instructions = []
        if file_mode:
            func_header = " ".join(tokens)
            brace_count = 0
            found_function = False
            
            with open(file_path, "r") as file:
                lines = file.readlines()
                
            for line in lines:
                line = line.strip()
                func_ignore.append(line)

                
                # Start collecting when we find the function header
                if line == func_header.strip():
                    found_function = True
                    brace_count += 1  # Count the opening brace
                    continue
                
                if found_function:
                    # Count braces in the line
                    brace_count += line.count("{")
                    brace_count -= line.count("}")
                    
                    # Add the line to instructions
                    function_instructions.append(line)
                    
                    # If brace_count is 0, we've found the matching closing brace
                    if brace_count == 0:
                        # Remove the last line (closing brace) from instructions
                        function_instructions.pop()
                        break
        else:
            # Interactive mode with proper brace tracking
            brace_count = 1  # Start with 1 for the opening brace
            while brace_count > 0:
                file_input = input("func;> ")
                if not file_input.strip():  # Skip empty lines
                    continue
                
                # Count all braces in the current line
                brace_count += file_input.count("{")
                brace_count -= file_input.count("}")
                
                # Only add the line if it's not the final closing brace
                if brace_count > 0 or (file_input.strip() != "}" and brace_count == 0):
                    function_instructions.append(file_input)

        # Validate return statement if needed
        if functype != "void":
            find_return = False
            for cont in function_instructions:
                if "return" in cont:
                    find_return = True

            if not find_return:
                print(f"\033[91mfunction:syntax error: \033[0mno return value; expected type;{functype}")
                return 4

        # Process parameters
        param_order = []
        for param in func_intake:
            if param != "$void":
                if len(func_intake) >= 1:
                    semi_idx = param.find(";")
                    param_name = param[:semi_idx]
                    param_type = param[semi_idx+1:]
                    param_order.append(param_name)
                    variables[param_name] = {
                        "cat": "func",
                        "type": param_type,
                        "value": "hidden"
                    }
            else:
                func_intake = []

        # Create the method entry
        methods[func_name] = {
            "returntype": functype,
            "params": len(func_intake),
            "param_order": param_order,
            "content": function_instructions,
        }
        return 0


def fi(tokens):
    if envriornment_config["showtokens"] == True:
        print(tokens)
    global fi_code
    fi_code = 0
    if tokens[0] == True:
        func_caller(tokens[1:])
        fi_code = 0
        return 0
    else:
        fi_code = 1
        return 1


def elsefi(tokens):
    global fi_code
    if fi_code != 1:
        return 1
    else:
        if tokens[0] == True:
            func_caller(tokens[1:])
            fi_code = 0
            return 0
        else:
            fi_code = 1
            return 1

def default(tokens):
    if fi_code !=1:
        return 1
    else:
        func_caller(tokens[0:])
        return 0
    
def repeat(tokens):
    """
    Handle repeat loops in both file and interactive modes
    token_input -> ["5","{"]
    repeat 5 {
        // contents
    }
    """
    # Input validation
    if len(tokens) < 1:
        print("\033[91mrepeat:value: \033[0mno repition attribute assigned")
        return 1
    elif tokens[-1] != "{":
        print("\033[91mrepeat:opener: \033[0mno repeat loop opener provided")
        return 1
    
    # Parse repeat value
    try:
        repeat_val = int(tokens[0])
    except ValueError:
        print("\033[91mrepeat:type error: \033[0mno int assigned for repeator")
        return 3
        
    loop_contents = []
    
    try:
        if file_mode:
            func_header = f"repeat {repeat_val} {{"
            inside_loop = False
            repeat_val = repeat_val - 1
            
            with open(file_path, "r") as read_file:
                lines = read_file.readlines()
                
            for i, line in enumerate(lines):
                line = line.strip()
                
                # Find the start of our repeat block
                if line == func_header:
                    inside_loop = True
                    continue
                
                # Collect contents until closing brace
                if inside_loop:
                    if line == "}":
                        break
                    if line:  # Only add non-empty lines
                        loop_contents.append(line)
        else:
            # Interactive mode remains the same
            file_input = ""
            while file_input != "}":
                file_input = input("repeat loop> ")
                if file_input != "}":
                    loop_contents.append(file_input)
    
    except Exception as e:
        print(f"\033[91mrepeat:error: \033[0m{str(e)}")
        return 1
        
    try:
        # Reset iteration counter
        variables["iteration"]["value"] = 0
        
        # Execute the loop contents repeat_val times
        for _ in range(repeat_val):
            for command in loop_contents:
                minitoke = tokenization(command)
                func_caller(minitoke)
                variables["iteration"]["value"] += 1
                
        variables["iteration"]["value"] = 0
        return 0
        
    except Exception as e:
        print(f"\033[91mrepeat:execution error: \033[0m{str(e)}")
        return 1

def do(tokens):
    """
    do {benchmarker} {operation} {comparison} {
    // code
    }
    """
    operators = {
        "<": lambda x, y: x < y,
        ">": lambda x, y: x > y,
        "==": lambda x, y: x == y,
        "<=": lambda x, y: x <= y,
        ">=": lambda x, y: x >= y
    }

    if len(tokens) < 4:
        print("\033[91mdo:arguments: \033[0mNot enough arguments given")
        return 1

    bench_marker, op, compare, opener = tokens[0], tokens[1], tokens[2], tokens[-1]

    # Validate arguments
    try:
        bench_marker = int(bench_marker)
    except ValueError:
        print("\033[91mdo:value: \033[0mBenchmarker must be an integer")
        return 1

    try:
        compare = int(compare)
    except ValueError:
        print("\033[91mdo:value: \033[0mComparison must be an integer")
        return 1

    if op not in operators:
        print("\033[91mdo:value: \033[0mInvalid operator provided")
        return 1

    if opener != "{":
        print("\033[91mdo:opener: \033[0mNo opening brace defined")
        return 1

    # Parse instructions
    do_instructions = []

    if file_mode:  # File-based input
        
        with open(file_path, 'r') as readFile:
            func_header = f"do {bench_marker} {op} {compare} {{"
            brace_count = 0
            capturing = False

            for line in readFile:
                line = line.strip()

                if line == func_header:
                    capturing = True
                    brace_count += 1
                    continue

                if capturing:
                    if line == "{":
                        brace_count += 1
                    elif line == "}":
                        brace_count -= 1

                    if brace_count == 0:
                        break  # Exit when the block is fully parsed

                    do_instructions.append(line)
    else:  # Manual input mode
        while True:
            line_input = input("do loop> ").strip()
            if line_input == "}":
                break
            do_instructions.append(line_input)

    if file_mode:
        while operators[op](bench_marker+1, compare):
            for command in do_instructions:
                minitoke = tokenization(command)
                func_caller(minitoke)
            bench_marker += 1  
            variables["iteration"]['value'] += 1
    else:
        while operators[op](bench_marker, compare):
            for command in do_instructions:
                minitoke = tokenization(command)
                func_caller(minitoke)
            bench_marker += 1  
            variables["iteration"]['value'] += 1
    
    variables["iteration"]['value'] = 0
    return 0







def rand(tokens):
    if len(tokens) < 2:
        print("\033[91mrandint:params error:\033[0mnot enough params given")
        return 1
    else:
        try:
            random_min = int(tokens[0])
        except:
            return 1
        try:
            random_max = int(tokens[1])
        except:
            return 1
        print(random.randint(random_min,random_max))
        return 0



def varlist(void):
        print("\033[93mAll Initialized Variables:\033[0m\n")
        max_key_length = max(len(str(key)) for key in variables)
        max_type_length = max(len(str(variables[key]['type'])) for key in variables)
        max_value_length = max(len(str(variables[key]['value'])) for key in variables)
        max_cat_length = max(len(str(variables[key]['cat'])) for key in variables)
        format_string = f"{{:<{max_key_length}}}    {{:<{max_cat_length}}}    {{:<{max_type_length}}}     {{:<{max_value_length}}}    "
        print(format_string.format("Variable","IsModify",  "Type", "Value"))
        print(format_string.format("________","______", "____", "_____\n"))
        show_val = ""
        show_mod = ""
        for key in variables:
            #if len(str(variables[key]["value"])) > 10:
                #show_val = f"{variables[key]['value'][:10]}..."
            #else:
                #show_val = f"{variables[key]['value']}"
            if str(variables[key]['cat']) == "preset":
                show_mod = "False"
                mod_col = "\033[91m"
            elif str(variables[key]['cat']) == "func":
                show_mod = "Reserved"
                mod_col = "\033[90m"
            else:
                show_mod = "True"
                mod_col = "\033[92m"
            reset = "\033[0m"
            print(format_string.format(
                str(key), 
                str(show_mod),
                str(variables[key]['type']),
                str(variables[key]['value'])
            ))
        return 0

def funclist(void):
    print("\033[33mAll Defined Functions\n\033[0m")
    max_method_length = max(len(str(key)) for key in methods)
    max_type_length = max(len(str(methods[key]['returntype'])) for key in methods)
    max_arg_length = max(len(str(methods[key]['params'])) for key in methods)
    format_string = f"{{:<{max_method_length}}}     {{:<{max_type_length}}}     {{:<{max_arg_length}}}"
    print(format_string.format("Function","Type","Expected"))
    print(format_string.format("________","____","_______\n"))
    for key in methods:
        print(format_string.format(
                str(key), 
                str(methods[key]['returntype']), 
                str(methods[key]['params'])
            ))
    return 0

def varcheck(void):
    if void[0] in variables:
        print("\033[93mVariable Information:\033[0m\n")
        key_length = max(len(void[0]), len("Variable"))
        type_length = max(len(str(variables[void[0]]['type'])), len("Type"))
        value_length = max(len(str(variables[void[0]]['value'])), len("Value"))
        cat_length = max(len(str(variables[void[0]]['cat'])), len("isModify"))
        cat_val = ""
        if variables[void[0]]['cat'] == "preset":
            cat_val = "False"
        else:
            cat_val = "True"


    
        header_format = f"{{:<{key_length}}}    {{:<{cat_length}}}    {{:<{type_length}}}     {{:<{value_length}}}    "
        value_format = f"{{:<{key_length}}}    {{:<{cat_length}}}    {{:<{type_length}}}     {{:<{value_length}}}    "
    
        print(header_format.format("Variable", "isModify","Type", "Value"))
        print(header_format.format("________", "______", "____", "_____\n"))
    
        print(value_format.format(
            void[0], 
            cat_val,
            variables[void[0]]['type'], 
            variables[void[0]]['value']
        ))
        return 0
    else:
        print(f"\033[91mvariable:exists error: \033[0mvariable \033[91m'{void[0]}'\033[0m not found")
        return 1



def do_math(tokens):
    operator_map = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv,
        '%': operator.mod,
        '**': operator.pow,
        '//': operator.floordiv,
        '==': operator.eq,
        '!=': operator.ne,
        '>': operator.gt,
        '<': operator.lt,
        '>=': operator.ge,
        '<=': operator.le,
    }

    # Step 1: Process parentheses (if any)
    while '(' in tokens:
        # Find the innermost parentheses
        first = tokens.index('(')
        last = len(tokens) - 1 - list(reversed(tokens)).index(')')
        
        # Evaluate the expression inside the parentheses
        sub_tokens = tokens[first + 1:last]
        result = do_math(sub_tokens)  # Recursive call for nested expressions
        
        # Replace the parentheses with the result
        tokens[first] = result[0]
        del tokens[first + 1:last + 1]

    # Step 2: Process operators (left-to-right for simplicity)
    i = 0
    while i < len(tokens):
        if tokens[i] in operator_map:
            # Perform the operation and replace the operands and operator
            result = operator_map[tokens[i]](int(tokens[i - 1]), int(tokens[i + 1]))
            tokens[i - 1:i + 2] = [result]
            i -= 1  # Adjust index to account for reduced list size
        else:
            i += 1

    return tokens




# -- everything before is the actual working sections of the interpretor -- #
# -- everything after this line is the interpretor commands -- #

def set(tokens):
    """
    set x = "hello world"
    set y = 10;int

    values can be categorized as (str,int,flt,bool,arr) by adding a semicolon after the value
    but if no value types are added, it will be auto typed. the set command is used to define variables
    that can be changed; meaning they are mutable

    expected input:
        tokens (arr) -> ["set","x","=","10;int"]
    return value (int): this is the error code
        if successful:
            return 0
        else:
            return 1
    """
    allowed_types = ["str","int","flt","bool","arr"]
    if "=" not in tokens:
        print("\033[91mset:args error: \033[0mplease add expected params")
        return 0
    else:
        eq_place = tokens.index("=")
        if not tokens[eq_place+1]:
            print("\033[91mset:args error: \033[0mplease add expected params")
            return 1
        if not tokens[eq_place-1]:
            print("\033[91mset:args error: \033[0mplease add expected params")
            return 1
        var_key = tokens[eq_place-1]
        if var_key in variables:
            if variables[var_key]["cat"] == "preset":
                print("\033[91mset:const error: \033[0mvariable cannot be rewritten")
                return 1
        var_valueraw = tokens[eq_place+1]
        
        # Check if there is a semicolon and process accordingly
        if isinstance(var_valueraw, int):
            var_val = var_valueraw
            var_type = "int"
        
        elif isinstance(var_valueraw, float):
            var_val = var_valueraw
            var_type = "flt"

        elif var_valueraw.find(";") > -1:
            semi_idx = var_valueraw.find(";")
            var_val = var_valueraw[:semi_idx]
            var_type = var_valueraw[semi_idx+1:]
        else:
            var_val = var_valueraw
            var_type = type_check(var_val)

        if var_type not in allowed_types:
            print("\033[91mset:type error: \033[0minvalid type")
            return 3

        cat_val = "assigned"

        variables[var_key] = {
            "cat": cat_val,
            "type": var_type,
            "value": var_val
        }
        return 0

def const(tokens):
    """
    const x = "hello world"
    const y = 10;int

    values can be categorized as (str,int,flt,bool,arr) by adding a semicolon after the value
    but if no value types are added, it will be auto typed. the const command is used to define variables
    that cannot be changed; meaning they are not mutable

    expected input:
        tokens (arr) -> ["const","x","=","10;int"]
    return value (int): this is the error code
        if successful:
            return 0
        else:
            return 1
    """


    allowed_types = ["str","int","flt","bool","arr"]
    if "=" not in tokens:
        return 0
    else:
        eq_place = tokens.index("=")
        var_key = tokens[eq_place-1]
        if var_key in variables:
            if variables[var_key]["cat"] == "preset":
                print("\033[91mconst:const error: \033[0mvariable cannot be rewritten")
                return 1
        if not tokens[eq_place+1]:
            print("\033[91mconst:args error: \033[0mplease add expected params")
            return 1
        var_valueraw = tokens[eq_place+1]
        
        if isinstance(var_valueraw, int):
            var_val = var_valueraw
            var_type = type_check(var_val)

        elif isinstance(var_valueraw, float):
            var_val = var_valueraw
            var_type = type_check(var_val)

        elif var_valueraw.find(";") > -1:
            semi_idx = var_valueraw.find(";")
            var_val = var_valueraw[:semi_idx]
            var_type = var_valueraw[semi_idx+1:]
        else:
            var_val = var_valueraw
            var_type = type_check(var_val)

        if var_type not in allowed_types:
            print("\033[91mconst:type error: \033[0minvalid type")
            return 3

        cat_val = "preset"

        variables[var_key] = {
            "cat": cat_val,
            "type": var_type,
            "value": var_val
        }
        return 0

def let(tokens):
    """
    create a varible without assigning a value, these values are mutable, but they can be turned into consts later
    a let variable cannot be defined for a variable that already exists

    like this,
    let x;int

    expected input:
        tokens (arr) -> ["let","x;type"]
    return value (int): this is the error code
        if successful:
            return 0
        else:
            return 1
    """
    if len(tokens) < 1:
        print("\033[91mlet:args error: \033[0mplease add expected params")
        return 1
    var_key_raw = tokens[0]
    if var_key_raw.find(";") == -1:
        print("\033[91mlet:args error: \033[0mplease add expected params")
        return 1
    semi_idx = var_key_raw.find(";")
    var_key = var_key_raw[:semi_idx]
    if var_key in variables:
        print("\033[91mlet:exists error: \033[0mvariable already has value")
        return 1
    var_type = var_key_raw[semi_idx+1:]
    cat_val = "assigned"
    variables[var_key] = {
        "cat": cat_val,
        "type": var_type,
        "value": "undefined"
    }
    return 0 


    
def stdout(tokens):
    """
    stdout aggregates everything in the list, so no use for quotes
    to add a space you need to add a "_", this is done in the tokenizer
    also adds spaces after every index
    expected:
    ["hello","world"] -> helloworld
    """
    phrase = ""
    try:
        for i in tokens:
            if len(phrase) > 1:
                phrase += " "
            phrase += str(i)
        print(f"\033[0m{phrase}")
        #print(type(phrase))
        return 0
    except:
        return 1


def stdin(tokens):
    """
    This is essentially the same as defining a variable, but this will be taken as real-time input
    instead of a set value. It follows typing as "stdin myVar;int please add your age"
    where:
    - var_key is "myVar"
    - var_type is int
    - it will ask the user "please add your age"
    """
    if not tokens:
        print("\033[91mstdin:args error: \033[0mplease add expected params")
        return 1

    var_keyraw = tokens[0]
    
    if var_keyraw.find(";") == -1:
        print("\033[91mstdin:type error: \033[0mno type specified")
        return 3

    try:
        semi_idx = var_keyraw.find(";")
        var_key = var_keyraw[:semi_idx]
        if var_key in variables:
            if variables[var_key]["cat"] == "preset":
                print("\033[91msstdin:const error: \033[0mvariable cannot be rewritten")
                return 1
        var_type = var_keyraw[semi_idx+1:]
        
        var_types = ["str","int","bool","arr"]
        if var_type not in var_types:
            print("\033[91mstdin:type error: \033[0minvalid type provided")
            return 3

        phrase = " ".join(tokens[1:])
        
        var_val = input(f"\033[33m{var_type} \033[0m{phrase} ")
        if var_type == "str":
            try:
                str(var_val)
            except:
                print(f"\033[91mstdin:type error: \033[0minvalid type provided, expected {var_type}")
                exit(1)
        elif var_type == "int":
            try:
                int(var_val)
            except:
                print(f"\033[91mstdin:type error: \033[0minvalid type provided, expected {var_type}")
                exit(1)
        if not var_val:
            var_val = "not specified"
        variables[var_key] = {
            "type": var_type,
            "value": var_val,
            "cat" : "assigned"
        }

        return 0

    except Exception as e:
        print(f"\033[91merror: \033[0m{str(e)}")
        return 1

def clear(void):
    try:
        os.system("clear")
        return 0
    except:
        return 1
    
def numceil(tokens):
    if len(tokens) < 2:
        print("\033[91mnumceil:args error: \033[0mplease add expected params")
    if not tokens[0]:
        print("\033[91mnumceil:args error: \033[0mplease add expected params")
        return 1
    elif not tokens[1]:
        print("\033[91mnumceil:args error: \033[0mplease add significant digits")
        return 1
    else:
        try:
            num = float(tokens[0])
            sig = int(tokens[1])
            num = round(num, sig)
            print(num)
            return 0
        except:
            return 1

def ls(tokens):
    if len(tokens) < 1:
        dir_path = '.'
    else:
        dir_path = tokens[0]
    files = []
    try:
        for filename in os.listdir(dir_path):
            if filename[filename.rfind("."):] == ".arc":
                files.append(filename)
            else:
                continue
        print("Compatible Files")
        print("   ".join(files))
        return 0
    except:
        return 1

def run(tokens):
    if len(tokens) != 1:
        print('\033[91mrun:file error:\033[0m too many / no run file provided')
        return 1
    elif checkfile(tokens[0]):
        global file_path
        file_path = tokens[0]
        global file_mode
        file_mode = True
        open_file(file_path)
        if envriornment_config["print_error_code"] == True:
            if returncode != 0:
                print(f"\033[97mExit Code: \033[91m{returncode}\033[0m")
            else:
                print(f"\033[97mExit Code: \033[92m{returncode}\033[0m")
        file_mode = False
        return 0
    else:
        print('\033[91mrun:file error: \033[0mnot a valid file')
        return 1



def help():
    print("""Welcome To CarbonScript Help!
    
    All files to be passed by the interpretor must end with \033[92m.car\033[0m Extentions

    Please Interact with the \033[92m'learn_cscript.md'\033[0m for more information about syntax and writing code

    For Code Examples, please refer to \033[92m'/examples'\033[0m folder
    """)







def main(returncode):
    if len(sys.argv) > 1 and not TEST:
        if checkfile(sys.argv[1]):
            global file_path
            file_path = sys.argv[1]
            global file_mode
            file_mode = True
            global file_line
            file_line = 1  

            open_file(file_path)
            if envriornment_config["print_error_code"] == True:
                if returncode != 0:
                    print(f"\033[97mExit Code: \033[91m{returncode}\033[0m")
                else:
                    print(f"\033[97mExit Code: \033[92m{returncode}\033[0m")
    else:
        try:
            print(f"""
    Welcome To CarbonScript \033[92m{variables['version']['value']}\033[0m
    to exit session press ctrl+c or type "quit"
    Created by: \033[94msjapanwala\033[0m
            """)
            while True:
                file_mode = False
                command = ""
                while command.lower() != "exit":
                    if returncode == 0:
                        rc = "\033[92m➜\033[0m"
                    elif returncode == 2:
                        rc = "\033[90m➜\033[0m"
                    else:
                        rc = "\033[91m➜\033[0m"
                    command = input(f"\n\033[0mCarbonScript {rc}\033[0m ")
                    tokens = tokenization(command)
                    returncode = func_caller(tokens)
                    set(["errorlevel","=",f"{returncode}"])
                    if envriornment_config["print_error_code"] == True:
                        if returncode != 0:
                            print(f"\033[97mExit Code: \033[91m{returncode}\033[0m")
                        else:
                            print(f"\033[97mExit Code: \033[92m{returncode}\033[0m")
        except KeyboardInterrupt:
            print("\rCarbonScript Session Ended Successful; Goodbye")
            exit(1)


if __name__ == "__main__":
    global returncode
    returncode = 0
    global fi_code
    fi_code = 0
    global func_ignore
    func_ignore = []
    global func_allowance 
    func_allowance = False
    global loop_contents
    loop_contents = []
    global random_min
    global random_max
    random_min = 1
    random_max = 100
    global file_line
    file_line = 0

    if len(sys.argv) > 1:
        TEST = False
        if sys.argv[1] == "--v":
            print(f"CarbonScript Version: \033[92m{variables['version']['value']}\033[0m\nfrom: www.github.com/sjapanwala/CarbonScript")
            exit()
        elif "env:show-ec" in sys.argv:
            envriornment_config["print_error_code"] = True
            TEST = True
        elif "env:show-tk" in sys.argv:
            envriornment_config["showtokens"] = True
            TEST = True
        elif "--help" in sys.argv:
            help()
            exit(1)

    main(returncode)
