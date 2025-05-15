#!/usr/bin/env python3
# -- TODO --
# allow for forced typing


import sys
import getpass, os
import operator
import random
import subprocess
import math
import time
global allowed_types
allowed_types = ["str","cstr","int","cint","flt","bool","arr","void","struct"]


# this is where the "envriornmental rules are stored; can be modified with args"
envriornment_config = {
        "showtokens": False,
        "print_error_code": False,
        "show_error_msgs": True,
        "force_run": False
        }

in_file_args = ("show-tokens","hide-errors","show-ec","force-run","force-dontrun")



variables = {
        "void" : {
            "cat": "preset",
            "type": "void",
            "value": "void",
        },
        "errorlevel" : {
            "cat": "elevated",
            "type": "int",
            "value": 0
            },
        "errorlevel_history" : {
            "cat": "preset",
            "type": "arr",
            "value": [],
        },
        "conditional_series" : {
            "cat": "preset",
            "type": "arr",
            "value": [],
        },
        "uname" : {
            "cat": "preset",
            "type": "str",
            "value": getpass.getuser()
            },
        "version": {
            "cat": "preset",
            "type": "str",
            "value": "v04.0/25"
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
        "true": {
            "cat": "preset",
            "type": "int",
            "value": 1
        },
        "false": {
                "cat": "preset",
                "type": "int",
                "value": 0
        },
        "fileInteraction": {
            "cat": "preset",
            "type": "str",
            "value": "void"
        },
        "args": {
            "cat": "preset",
            "type": "arr",
            "value": "[]"
        },
            "iteration" : {
            "cat" : "elevated",
            "type": "int",
            "value": 0
            },
        "rand": {
            "cat": "elevated",
            "type": "int",
            "value": 0
            },
        "pop": {
            "cat": "elevated",
            "type": "int",
            "value": 0,
        },
        "len": {
            "cat": "elevated",
            "type": "int",
            "value": 0,
        },
        "sorted": {
            "cat": "elevated",
            "type": "arr",
            "value": []
        },

    }

methods = {
        "status" : {
            "returntype": "void",
            "params": 0,
            "param_order": [],
            "content" : ["stdout \033[93m * \033[0m Exited With Status Code ?errorlevel","}"],
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
        "reverse": {
            "returntype": "arr",
            "params": 1,
            "param_order": ["$a"],
            "content": ['set a = ceil($a)','length ?a','let reversed;arr','repeat ?len {','pop $a','push reversed ?pop','}','return ?reversed'] 
        },
    }

structs = {}

remap_keywords = {
    "if": "fi",
    "ifelse":"elsefi",
    "else":"default",
    "sort": "sort_array",
    "libutils": "import_libraries",
    "fwrite": "file_write",
    "fset": "file_assign",
    "fclear": "file_erase",
    "fread": "file_read",
    "struct": "print_structs",
}

def print_structs(structname):
        if len(structname) < 1:
            return 1
        if structname[0] in structs:
            struct = structs[structname[0]]
            print(f"{structname[0]} {{")
            
            for field_name, field_info in struct.items():
                if isinstance(field_info, dict) and 'value' in field_info:
                    value = field_info['value']
                    if isinstance(value, str):
                        print(f'    "{field_name}": \'{value}\',')
                    else:
                        print(f'    "{field_name}": {value},')
            
            print("}")
            return 0
        else:
            return 1

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
        token_array = aggregate(user_input.split(" "))
        token_array = [word.replace('"', '') for word in token_array]
        if "increm" in token_array[0]:
            increm(token_array[1:])
        if "decrem" in token_array[0]:
            decrem(token_array[1:])
        # scan for comments
        
        for i,token in enumerate(token_array):
            if token_array[0] == "//":
                token_array = "~"
            elif token == "//":
                token_array = token_array[:i]
        token_array = [item for item in token_array if item != ""]
        
        for i,token in enumerate(token_array):
            # check for precedence
            if token in remap_keywords:
                token_array[i] = remap_keywords[token]
            if token == "true":
                token_array[i] = int(1)
            if token == "false":
                token_array[i] = int(0)
            if "?" in token[0]:
                if "]" in token[-1] and "[" in token:
                    return_val = indexing(token)
                    token_array[i] = return_val
                else:
                    recovered = deVar(token)
                    token_array[i] = recovered
            if token[0] == "@":
                ec,return_val = run_func(token[1:],token_array)
                token_array[i] = return_val[0]
                variables['errorlevel']['value'] = int(ec)
                global func_code
                func_code = ec
            if "ceil(" in token:
                if ")" in token:
                    l_idx = token.rfind(")")
                    r_idx = token.rfind("(")
                    number = token[r_idx + 1 : l_idx]
                    number = tokenization(number)
                    number = float(number[0])  
                    token_array[i] = math.ceil(number)  
            if "floor(" in token:
                if ")" in token:
                    l_idx = token.rfind(")")
                    r_idx = token.rfind("(")
                    number = token[r_idx + 1 : l_idx]  
                    number = tokenization(number)
                    number = float(number[0])  
                    token_array[i] = math.floor(number) 
            if "type(" in token:
                if ")" in token:
                    l_idx = token.rfind(")")
                    r_idx = token.rfind("(")
                    to_check_type = token[r_idx + 1 : l_idx]
                    type_check_response = type_check(tokenization(to_check_type)[0])
                    token_array[i] = type_check_response
            if "cnum(" in token:
                if ")" in token:
                    l_idx = token.rfind(")")
                    r_idx = token.rfind("(")
                    to_convert = token[r_idx + 1 : l_idx]
                    converted = ascii_to_decimal_inter((tokenization(to_convert)[0]))
                    token_array[i] = int(converted)
            if "ascii(" in token:
                if ")" in token:
                    l_idx = token.rfind(")")
                    r_idx = token.rfind("(")
                    to_convert = token[r_idx + 1 : l_idx]
                    converted = decimal_to_ascii_stringer((tokenization(to_convert)[0]))
                    token_array[i] = str(converted)
        if "(" in token_array:
            token_array = do_math(token_array)
        return token_array
    except Exception as e:
        return ["undefined"]

def indexing(token):
    first_idx = token.rfind("[")
    last_idx = token.rfind("]")
    index_val = tokenization(token[first_idx+1:last_idx])
    toke_var = token[:first_idx]
    recovered = deVar(toke_var)
    if "." in toke_var:
        recovered = deStruct(toke_var[1:])

    if isinstance(recovered, list) or isinstance(recovered,str):
        return_val = recovered[int(index_val[0])]
    else:
        return_val = variables['void']['value']
    return return_val

def get_args():
    args = []
    if sys.argv:
        arg_len = len(sys.argv)
        if arg_len > 11:
            for _ in range(arg_len):
                args.append(ascii_to_decimal_inter('void'))
        else:
            for _ in range(10):
                args.append(ascii_to_decimal_inter('void'))
        for count,arg in enumerate(sys.argv):
            args[count] = arg
        variables["args"]["value"] = args[1:]

def ascii_to_decimal_inter(x):
    string = ""
    for i in x:
        temp_string = f"{ord(i):03d}"  
        string += temp_string  
    string += f"{len(x):04d}"  
    return int(string)  

def decimal_to_ascii_stringer(number):
    length_code = str(number)[-4:]
    deci_code = str(number)[:-4]
    if len(deci_code) % 3 != 0:
        deci_code = deci_code.zfill(len(deci_code) + (3 - len(deci_code) % 3))
    parts = [int(deci_code[i:i+3]) for i in range(0, len(deci_code), 3)]
    string = ""
    for i in parts:
        string += chr(i)
    return string

def aggregate(tokens):
    """
    Merges words enclosed in quotes into a single string without returning quotes.

    :param input_list: List of strings
    :return: Modified list with merged quoted strings, without quotes
    """
    result = []
    in_quotes = False
    quoted_string = []

    for item in tokens:
        if item.startswith('"') and not in_quotes:  
            in_quotes = True
            quoted_string.append(item.lstrip('"'))
        elif item.endswith('"') and in_quotes: 
            quoted_string.append(item.rstrip('"'))
            result.append(" ".join(quoted_string))
            in_quotes = False
            quoted_string = []
        elif in_quotes:  
            quoted_string.append(item)
        else:  
            result.append(item)

    if in_quotes:
        result.append(" ".join(quoted_string))
    return result

def rem(variable):
    print(variable)

def increm(tokens):
    for pos_var in tokens:
        if not isinstance(pos_var, int):
            if pos_var[0] == "?" and pos_var[1:] in variables:
                increm_variable = pos_var[1:]
                if variables[increm_variable]['type'] == "int":
                    if variables[increm_variable]['cat'] == "assigned":
                        variable_value = variables[increm_variable]['value']
                        variables[increm_variable]['value'] = int(variable_value) + 1

def decrem(tokens):
    for pos_var in tokens:
        if not isinstance(pos_var, int):
            if pos_var[0] == "?" and pos_var[1:] in variables:
                increm_variable = pos_var[1:]
                if variables[increm_variable]['type'] == "int":
                    if variables[increm_variable]['cat'] == "assigned":
                        variable_value = variables[increm_variable]['value']
                        variables[increm_variable]['value'] = int(variable_value) - 1

    

# --- START OF THE FILE READING SYSTEM, READING ".car" FILES ONLY ---
file_contents = []
def checkfile(filepath):
    """
    checks the authenticity of the file, and if it ends with ".car"
    """
    if os.path.isfile(filepath):
        #if filepath[-4:] != ".car":
        #print("\033[91mfile:type error: \033[0mfile must be of type .car")
        #return False
        return True
    else:
        print("\033[91mfile:exists error: \033[0mfile does not exist")
        return False

raw_files = []
def open_file(filename):
    with open(filename, "r") as file:
        counter = 0
        for line in file:
            counter +=1
            file_contents.append(line.strip())
            raw_files.append(line)
            if line.strip() == "RULE force-dontrun":
                print(f"\033[90m{file_path} {counter}:RULE: force-dontrun")
                print("\033[91merror: \033[0mYou are not allowed to run this file!")
                exit(1)
            if line.strip() == "RULE hide-errors":
                envriornment_config['show_error_msgs'] = False
            if line.strip() == "RULE show-ec":
                envriornment_config['print_error_code'] = True
            if line.strip() == "RULE show-tk":
                envriornment_config['showtokens'] = True
            if line.strip() == "RULE force-run":
                envriornment_config['force_run'] = True 
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
            returncode = func_caller(tokenizer)
            variables["errorlevel"]["value"] = returncode
            if returncode not in (0,2):
                error_responder(returncode,file_line,codeline,file_contents)
            elif variables['errorlevel']['value'] not in (0,2):
                returncode = variables['errorlevel']['value']
                error_responder(returncode,file_line,codeline,file_contents)
    #find_optimization(file_contents)

def error_mapper(error_code):
    return_map = {
        0 : "ok",
        1 : "ambiguous error",
        2 : "comment",
        3 : "unexpected type interaction.",
        4 : f"unexpected syntax provided.",
        5 : "incompleted parameters proveded",
        8 : "mathematical logic error",
        15: "unable to initialized essential items",
        16: "initializatized",
        9 : "file interaction error",
        17: "ctrl c detected, exited program",
        81: "libutil not found",
        404: "forbidden call",
    }
    ec_color_map = {
        0: "\033[1;92m",
        1: "\033[1;91m",
        3: "\033[1;38;5;220m",
        2: "\033[1;90m",
        4: "\033[38;5;202m",
        5: "\033[38;5;196m",
        8: "\033[38;5;129m",
        9: "\033[38;5;111m",
        15: "\033[38;5;115m",
        16: "\033[38;5;116m",
        17: "\033[38;5;142m",
        81: "\033[38;5;199m",
        404: "\033[1;90m",
    }
    if error_code in return_map:
        error_reason = return_map[error_code]
        ec_color = ec_color_map[error_code]
    else:
        error_reason = ("error was not identfiable")
        ec_color = "\033[97m"
        error_code = -1

    return error_reason,ec_color

def error_responder(error_code,linenum,codeline,contents):
    variables['errorlevel']['value'] = 0
    error_reason,ec_color = error_mapper(error_code)
    get_num_len = len(str(linenum))
    stat_bar = f"{file_path}"
    print(f"""{stat_bar}:{linenum}:{error_code}
{get_num_len * " "} {ec_color}|\033[0m
\033[90m{linenum}\033[0m {ec_color}|\033[0m {codeline}
{get_num_len * " "} {ec_color}|\033[0m \033[91m{len(codeline) * "^"} {ec_color}{error_reason}\033[0m

\033[1;91merror: \033[0maborting due to status code {error_code}
   """)
    if envriornment_config['force_run'] == False:
        exit(1)

def find_optimization(contents):
    events = {}
    for i in contents:
        print(i)

def suggest_func(input):
    omit_suggestions = {
        "find_optimization" : "void",
        "tokenization" : "void",
        "aggregate" : "void",
        "checkfile" : "void",
        "open_file": "void",
        "run_file": "void",
        "error_responder": "void",
        "suggest_func": "void",
        "func_caller" : "void",
        "type_check": "void",
        "add_space": "void",
        "deVar": "void",
        "deVarFunc": "void",
        "run_func": "void",
        "construct_functions": "void",
        "do_math": "void",
        "help": "void",
        "update": "void",
        "main": "void",
        "print_structs": "struct",
        "file_read": "void",
        "file_write": "fwrite",
        "file_assign": "fset",
        "indexing": "void",
        "sort_array": "sort",
        "import_libraries": "libutils",
        "get_args": "void",
        "force_type": "type()",
        "ascii_to_decimal_inter": "cnum()",
        "decimal_to_ascii_stringer": "ascii()"
    }
    
    
    callable_globals = {name: obj for name, obj in globals().items() if callable(obj)}
    suggestions = []
    for name, obj in callable_globals.items():
        if str(input) in name or str(input) in remap_keywords:
            if name in omit_suggestions:
                if omit_suggestions[name] != "void":
                    suggestions.append(f"Did You Mean \033[93m{omit_suggestions[name]}\033[0m?")
            elif name not in omit_suggestions:
                suggestions.append(f"Did You Mean \033[93m{name}\033[0m?")
    return suggestions[0] if suggestions else ""


def func_caller(tokens):
    variables["conditional_series"]["value"].append(int(fi_code))
    variables["errorlevel_history"]["value"].append(int(variables["errorlevel"]["value"]))
    if envriornment_config["showtokens"] == True:
        print(tokens)
    
    if tokens == None:
        return 2
    user_input = tokens[0]
    if user_input == "RULE":
        return 0
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
    if user_input == "~":
        return 2
    if user_input in in_file_args:
        return 0
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
    omit = {
            "find_optimization",
            "tokenization",
            "aggregate",
            "checkfile",
            "open_file",
            "run_file",
            "error_responder",
            "suggest_func",
            "func_caller",
            "type_check",
            "add_space",
            "deVar",
            "deVarFunc",
            "run_func",
            "construct_functions",
            "do_math",
            "help",
            "update",
            "main"
        }

    for token in tokens:
        if isinstance(token,str):
            if token.lower() == "undefined":
                return 8
    if user_input in globals() and callable(globals()[user_input]):
        if user_input in omit:
            print(f"\033[91mforbidden function:\033[0m You are not allowed to call this function")
            return 404
        error_code = globals()[user_input](list(tokens[1:]))
        return error_code
    else:
        if file_mode:
            if envriornment_config['show_error_msgs']:
                suggestion = suggest_func(user_input)
                print(f"\033[91mstatment:syntax error\033[0m: '{user_input}' is not defined. {suggestion}")
                return 4
            return 4
        else:
            suggestion = suggest_func(user_input)
            print(f"\033[91mstatment:syntax error: \033[0m'{user_input}' is not defined. {suggestion}")
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
    elif isinstance(value,dict):
        return "struct"
    else:
        return "void"


def add_space(chunk):
    sp_idx = chunk.find("_")
    return chunk[:sp_idx], chunk[sp_idx+1:]
    
def force_type(var_val,var_type):
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
        if var_val == 1:
                return True
        return False


def deVar(variable):
    if "." in variable:
        return_value = deStruct(variable[1:])
        return return_value
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
            if var_val == 1:
                    return True
            return False
        elif var_type =="cstr":
            return int(var_val)
        elif var_type == "randint":
            return random.randint(random_min,random_max)
        else:
            return variables['void']['value']
    elif variable[1:] in structs:
        return structs[variable[1:]]
    else:
        return variables['void']['value']

def deStruct(var):
    if "." in var:
        struct_name_index = var.find(".")
        struct_key = var[struct_name_index+1:]
        struct_name = var[:struct_name_index]
        if struct_name not in structs:
            return variables['void']['value']
        elif struct_key not in structs[struct_name]:
            return  variables['void']['value']
        else:
            value_type = structs[struct_name][struct_key]["type"]
            value_value = structs[struct_name][struct_key]["value"]
            if value_type == "str":
                return str(value_value)
            elif value_type == "int":
                return int(value_value)
            elif value_type == "flt":
                return float(value_value)
            elif value_type == "arr":
                return (value_value)
            elif value_type == "bool":
                if value_value == 1:
                    return True
                return False
            else:
              return variables['void']['value']


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
            return variables['void']['value']
    else:
        return variables['void']['value']
    

def carbon(tokens):
    if len(tokens) < 1:
        print("\033[91merror: carbon calls:\033[0mprovide a valid carbonscript function")
        return 1
    system_call = tokens[0]
    if system_call == "vars":
        varlist("void")
        return 0
    if system_call == "quit":
        if len(tokens) < 2:
            exit(0)
        else:
            exit(tokens[1])
    elif system_call == "funcs":
        funclist("void")
        return 0
    elif system_call == "structs":
        structlist("void")
        return 0
    elif system_call == "history":
        curr_val = 0
        history_arr = variables["errorlevel_history"]["value"]

        header = (f"{'PId':<5}│ {'Level Code Information':<35}│ {'Code':<5}")
        seperator = (
    f"{'─' * 5}┼"
    f"{'─' * 36}┼"
    f"{'─' * 5}─"
)
        print(f"{header}\n{seperator}")
        for code in history_arr:
            ec_reason, ec_color = error_mapper(code)
            curr_val += 1
            reason_col = f"{ec_reason:<35}"
            print(f"{curr_val:<5}│ {ec_color}{reason_col}\033[0m│ {ec_color}{code:<5}\033[0m")
        return 0
    print("\033[91merror: carbon calls:\033[0mprovide a valid carbonscript function")
    return 1
def func_return(analysis):
    returned_value = tokenization(analysis)
    print(returned_value)


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
    ec = 0
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
        ec = func_caller(tokenizer)
    
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

def read_block(keyword):
    """Reads a multiline code block after a keyword like 'if', 'elsefi', or 'default'."""
    instructions = []
    brace_count = 0

    if file_mode:
        with open(file_path, "r") as file:
            lines = file.readlines()

        found_block = False
        for line in lines:
            line_stripped = line.strip()

            if not found_block and line_stripped.startswith(keyword) and "{" in line_stripped:
                found_block = True
                brace_count += 1
                continue

            if found_block:
                instructions.append(line_stripped)
                brace_count += line_stripped.count("{")
                brace_count -= line_stripped.count("}")

                if brace_count <= 0:
                    break
    else:
        brace_count = 1
        while brace_count > 0:
            file_input = input(f"{keyword};> ")
            if not file_input.strip():
                continue
            instructions.append(file_input)
            brace_count += file_input.count("{")
            brace_count -= file_input.count("}")

    func_ignore.extend(instructions)
    return instructions

def fi(tokens):
    if len(tokens) < 1:
        print("\033[91mif:params error: \033[0mnot enough params provided")
        return 5
    if envriornment_config["showtokens"] == True:
        print(tokens)
    global fi_code
    fi_code = 0
    if tokens[0] == True:
        returncode = func_caller(tokens[1:])
        if returncode not in (0,2):
            return returncode
        fi_code = 0
        return 0
    else:
        fi_code = 1
        return 0


def elsefi(tokens):
    if len(tokens) < 1:
        print("\033[91mifelse:params error: \033[0mnot enough params provided")
        return 5
    global fi_code
    if fi_code != 1:
        return 0
    else:
        if tokens[0] == True:
            returncode = func_caller(tokens[1:])
            if returncode not in (0,2):
                return returncode
            fi_code = 0
            return 0
        else:
            fi_code = 1
            return 0

def default(tokens):
    if len(tokens) < 1:
        print("\033[91melse:params error: \033[0mnot enough params provided")
        return 5
    if fi_code !=1:
        return 0
    else:
        return_code = func_caller(tokens[0:])
        if returncode not in (0,2):
            return returncode
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
        print("\033[91mrepeat:value: \033[0mno repetition attribute assigned")
        return 1
    elif tokens[-1] != "{":
        print("\033[91mrepeat:opener: \033[0mno repeat loop opener provided")
        return 1
    
    # Parse repeat value
    try:
        repeat_val = int(tokens[0])
    except ValueError:
        try:
            repeat_val = int(variables[tokens[0]]['value'])
        except:
            print("\033[91mrepeat:type error: \033[0mno int assigned for repeator")
            return 3
        
    loop_contents = []
    
    try:
        if file_mode:
            func_header = f"repeat {repeat_val} {{"
            inside_loop = False
            
            with open(file_path, "r") as read_file:
                lines = read_file.readlines()
                
            for i, line in enumerate(lines):
                line = line.strip()
                
                if line.startswith("repeat ?"):
                    var_name = line.split()[1][1:]
                    if var_name in variables:
                        line = f"repeat {variables[var_name]['value']} {{"
                
                if line == func_header:
                    inside_loop = True
                    continue
                
                if inside_loop:
                    if line == "}":
                        break
                    if line:  
                        loop_contents.append(line)
            
            repeat_val = repeat_val - 1
            
        else:
            file_input = ""
            while file_input != "}":
                file_input = input("repeat loop> ")
                if file_input != "}":
                    loop_contents.append(file_input)
    
    except Exception as e:
        print(f"\033[91mrepeat:error: \033[0m{str(e)}")
        return 1
        
    try:
        variables["iteration"]["value"] = 0
        
        
        for _ in range(repeat_val):  
            for command in loop_contents:
                minitoke = tokenization(command)
                ec = func_caller(minitoke)
                if ec not in (0,2):
                    return ec
                variables["iteration"]["value"] += 1
                
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
    variables["iteration"]['value'] = 0

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
    
    return 0


def until(tokens):
    # Basic parameter validation
    if len(tokens) < 3:
        print("\033[91muntil:params error:\033[0m not enough params given")
        return 1

    statement_decider = tokens[0]
    if tokens[1] != "=":
        print("\033[91muntil:operator error:\033[0m operator needs to be '='")
        return 1
    try:
        # This is the target value for the condition
        statement_value = int(tokens[2])
    except ValueError:
        print("\033[91muntil:type error:\033[0m statement value needs to be an int")
        return 3

    # Check for the opening brace
    if tokens[-1] != "{":
        print("\033[91muntil:opener error:\033[0m opening brace not provided")
        return 1

    # Gather the loop block contents
    loop_contents = []
    if file_mode:
        loop_header = f"until {statement_decider} = {statement_value} {{"
        in_loop = False
        with open(file_path, 'r') as readfile:
            for line in readfile:
                stripped = line.strip()
                if stripped == loop_header:
                    in_loop = True
                    continue
                if in_loop:
                    if stripped == '}':
                        break
                    loop_contents.append(line.rstrip())
    else:
        loop_input = ""
        while loop_input != "}":
            loop_input = input("until; ")
            if loop_input != '}':
                loop_contents.append(loop_input)

    # Recursive loop that re-evaluates the condition each time.
    def recur_loop(contents):
        try:
            # Evaluate the current value of the variable referenced by statement_decider.
            current_value = eval(statement_decider, globals())
        except Exception as e:
            print("\033[91muntil:evaluation error:\033[0m", e)
            return 1

        # Exit condition: when the current value equals the target.
        if current_value == statement_value:
            return 0
        else:
            for instruction in contents:
                # Execute each instruction. It is assumed that func_caller and tokenization are defined.
                ec = func_caller(tokenization(instruction))
            # Recursively call the loop again, re-checking the condition.
            return recur_loop(contents)

    # Start the recursive loop.
    return recur_loop(loop_contents)





def rand(tokens):
    if len(tokens) < 2:
        print("\033[91mrandint:params error:\033[0mnot enough params given")
        return 1,0
    else:
        try:
            random_min = int(tokens[0])
        except:
            return 1,0
        try:
            random_max = int(tokens[1])
        except:
            return 1,0
        random_val = (random.randint(random_min,random_max))
        variables['rand'] = {
            "cat": "preset",
            "type": "int",
            "value": random_val
        }
        return 0



def varlist(void):
    seperator = (
    f"{'─' * 5}┼"
    f"{'─' * 21}┼"
    f"{'─' * 7}┼"
    f"{'─' * 5}─"
)
    
    header = (f"{'VId':<5}│ {'Variable Name':<20}│ {'Type':<5} │ {'Mod':<3}")
    print(f"{header}\n{seperator}")
    func_id = 0
    for var in variables:
        func_id+=1
        if variables[var]['cat'] == "preset":
            mod_val = f"\033[1;91m0"
        elif variables[var]['cat'] == "elevated":
            mod_val = f"\033[1;93m2"
        else:
            mod_val = f"\033[1;92m1"
        type = variables[var]['type']
        print(f"{func_id:<5}│ {var:<20}│ {type:<6}│ {mod_val:<3}\033[0m")
    return 0

def funclist(void):
    seperator = (
    f"{'─' * 5}┼"
    f"{'─' * 21}┼"
    f"{'─' * 7}┼"
    f"{'─' * 7}─"
)
    header = (f"{'FId':<5}│ {'Function Name':<20}│ {'Type':<5} │ {'Params':<5}")
    print(f"{header}\n{seperator}")
    func_id = 0
    for func in methods:
        func_id+=1
        returntype = methods[func]['returntype']
        params = methods[func]['params']
        print(f"{func_id:<5}│ {func:<20}│ {returntype:<6}│ {params:<5}")
    return 0

def structlist(void):
    seperator = (
    f"{'─' * 5}┼"
    f"{'─' * 21}┼"
    f"{'─' * 9}─"
)
    
    header = (f"{'SId':<5}│ {'Struct Name':<20}│ {'Elements':<6}")
    print(f"{header}\n{seperator}")
    func_id = 0
    for struct in structs:
        Elements = len(structs[struct])
        print(f"{func_id:<5}│ {struct:<20}│ {Elements:<6}")
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
    if "=" not in tokens:
        print("\033[91mset:params error: \033[0mplease add expected params")
        return 5
    else:
        eq_place = tokens.index("=")
        if not tokens[eq_place+1]:
            print("\033[91mset:params error: \033[0mplease add expected params")
            return 5
        if not tokens[eq_place-1]:
            print("\033[91mset:params error: \033[0mplease add expected params")
            return 5
        var_key = tokens[eq_place-1]
        if var_key in variables:
            if variables[var_key]["cat"] != "assigned":
                print("\033[91mset:const error: \033[0mvariable cannot be rewritten")
                return 1
        if var_key in structs:
            print("\033[91mset:struct error: \033[0ma struct with this name already exists")
            return 1
        var_valueraw = tokens[eq_place+1]
        
        if isinstance(var_valueraw, int):
            var_val = var_valueraw
            var_type = "int"
        
        elif isinstance(var_valueraw, float):
            var_val = var_valueraw
            var_type = "flt"
        
        elif isinstance(var_valueraw, list):
            var_val = var_valueraw
            var_type = "arr"




        elif var_valueraw.find(";") > -1:
            semi_idx = var_valueraw.find(";")
            var_val = var_valueraw[:semi_idx]
            var_type = var_valueraw[semi_idx+1:]

            if var_type == "bool":
                if var_val in ("true","false"):
                    if var_val == "true":
                        var_val = 1
                    elif var_val == "false":
                        var_val = 0
                else:
                    try:
                        var_val = int(var_val)
                        if var_val > 1 or var_val < 0:
                            print("\033[91mset:type error: \033[0mbool has to be 0/1 or true/false")
                            return 3
                    except:
                        print("\033[91mset:assignment error: \033[0mbool has to be 0/1 or true/false")
                        return 1

            if var_type == "arr":
                var_val = var_val.split(',')

            if var_type == "cstr":
                converted = ascii_to_decimal_inter((tokenization(var_val)[0]))
                var_val = int(converted)

                    
        else:
            var_val = var_valueraw
            var_type = type_check(var_val)




    
        if var_type not in allowed_types:
            print("\033[91mset:type error: \033[0minvalid type")
            return 3

        cat_val = "assigned"

        if ":" in var_key:
            struct_key_index = var_key.find(":")
            struct_name = var_key[:struct_key_index]
            struct_key = var_key[struct_key_index+1:]
            if struct_name not in structs:
                print("\033[91mset error: struct init:\033[0m struct has not been initialized")
                return 1
            else:
                structs[struct_name][struct_key] = {
                    "cat": cat_val,
                    "type": var_type,
                    "value": var_val,
                }
                return 0
        
        if var_key in variables:
            if variables[var_key]['value'] == "undefined":
                if variables[var_key]['type'] != var_type:
                    print(f"\033[91mset:type error: \033[0mexpecting {variables[var_key]['type']}, provided {var_type}")
                    return 1
                else:
                    variables[var_key]['value'] = var_val
                    return 0



        

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


    if "=" not in tokens:
        return 1
    else:
        eq_place = tokens.index("=")
        var_key = tokens[eq_place-1]
        if var_key in variables:
            if variables[var_key]["cat"] != "assigned":
                print("\033[91mconst:const error: \033[0mvariable cannot be rewritten")
                return 1
        if var_key in structs:
            print("\033[91mconst:struct error: \033[0ma struct with this name already exists")
            return 1        
        if not tokens[eq_place+1]:
            print("\033[91mconst:params error: \033[0mplease add expected params")
            return 5
        var_valueraw = tokens[eq_place+1]
        
        if isinstance(var_valueraw, int):
            var_val = var_valueraw
            var_type = type_check(var_val)

        elif isinstance(var_valueraw, float):
            var_val = var_valueraw
            var_type = type_check(var_val)

        elif isinstance(var_valueraw, list):
            var_val = var_valueraw
            var_type = "arr"


        elif var_valueraw.find(";") > -1:
            semi_idx = var_valueraw.find(";")
            var_val = var_valueraw[:semi_idx]
            var_type = var_valueraw[semi_idx+1:]

            if var_type == "bool":
                if var_val in ("true","false"):
                    if var_val == "true":
                        var_val = 1
                    elif var_val == "false":
                        var_val = 0
                else:
                    try:
                        var_val = int(var_val)
                        if var_val > 1 or var_val < 0:
                            print("\033[91mconst:assignment error: \033[0mbool has to be 0/1 or true/false")
                            return 1
                    except:
                        print("\033[91mconst:assignment error: \033[0mbool has to be 0/1 or true/false")
                        return 1
            if var_type == "arr":
                var_val = var_val.split(',')

            if var_type == "cstr":
                converted = ascii_to_decimal_inter((tokenization(var_val)[0]))
                var_val = int(converted)

        else:
            var_val = var_valueraw
            var_type = type_check(var_val)

        if var_type not in allowed_types:
            print("\033[91mconst:type error: \033[0minvalid type")
            return 3

        cat_val = "preset"

        if ":" in var_key:
            struct_key_index = var_key.find(":")
            struct_name = var_key[:struct_key_index]
            struct_key = var_key[struct_key_index+1:]
            if struct_name not in structs:
                print("\033[91mset error: struct init:\033[0m struct has not been initialized")
                return 1
            else:
                structs[struct_name][struct_key] = {
                    "cat": cat_val,
                    "type": var_type,
                    "value": var_val,
                }
                return 0

        if var_key in variables:
            if variables[var_key]['value'] == "undefined":
                if variables[var_key]['type'] != var_type:
                    print(f"\033[91mconst:type error: \033[0mexpecting {variables[var_key]['type']}, provided {var_type}")
                    return 1
                else:
                    variables[var_key]['value'] = var_val
                    return 0

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
        print("\033[91mlet:params error: \033[0mplease add expected params")
        return 5
    var_key_raw = tokens[0]
    if var_key_raw.find(";") == -1:
        print("\033[91mlet:params error: \033[0mplease add expected params")
        return 5
    semi_idx = var_key_raw.find(";")
    var_key = var_key_raw[:semi_idx]
    if var_key in variables:
        print("\033[91mlet:exists error: \033[0mvariable already has value")
        return 1
    if var_key in structs:
            print("\033[91mlet:struct error: \033[0ma struct with this name already exists")
            return 1
    var_type = var_key_raw[semi_idx+1:]
    if var_type not in allowed_types:
        print("\033[91mlet:type error: \033[0minvalid type")
        return 3

    if var_type == "arr":
        var_value = []
    elif var_type == "struct":
        structs[var_key] = {}
        return 0
    else:
        var_value = "void"
    cat_val = "assigned"
    variables[var_key] = {
        "cat": cat_val,
        "type": var_type,
        "value": var_value
    }
    return 0 




def push(tokens):
    if len(tokens) < 2:
        print("\033[91mpush:params error: \033[0mnot enough params provided")
        return 1

    if tokens[0] not in variables:
        print("\033[91mpush:error: \033[0marray not initialized")
        return 1 

    if variables[tokens[0]]['type'] != "arr":
        print("\033[91mpush:type error: \033[0mvariable is not an array")
        return 3

    for item in tokens[1:]:
        # Ensure item is a string before checking ";"
        if isinstance(item, str) and ";" in item:
            type_idx = item.find(";")
            value = item[:type_idx]
            item_type = item[type_idx + 1:]

            if item_type in allowed_types:
                # Convert value based on type
                if item_type == "int":
                    value = int(value)
                elif item_type == "flt":
                    value = float(value)
                elif item_type == "str":
                    value = str(value)
            else:
                print(f"\033[91mpush:type error: \033[0minvalid type '{item_type}'")
                return 4
        else:  # No type provided, try to infer it
            value = str(item).strip()  # Ensure item is a string before conversion
            # Try to infer the type
            try:
                value = int(value)  # Try converting to int
            except ValueError:
                try:
                    value = float(value)  # Try converting to float
                except ValueError:
                    value = str(value)  # Default to string if both fail

        variables[tokens[0]]['value'].append(value)

    return 0

def pop(tokens):
    if len(tokens) < 1:
        print("\033[91mpop:params error: \033[0mnot enough params provided")
        return 1
    if tokens[0] not in variables:
        print("\033[91mpop:exist error: \033[0marray does not exist")
        return 1
    if variables[tokens[0]]['type'] != "arr":
        print("\033[91mpop:type error: \033[0mvariable is not an array")
        return 3
    if len(variables[tokens[0]]['value']) <= 0:
        print("\033[91mpop:content error: \033[0marray is empty")
        return 1
    temp_array = variables[tokens[0]]['value']
    item = temp_array[-1]
    item_type = ""
    try:
        item = int(item) 
        item_type = "int"
    except ValueError:
        try:
            item = float(item)
            item_type = "flt"
        except ValueError:
            item_type = "str"
    temp_array = temp_array[:-1]
    variables['pop'] = {
        "cat": "preset",
        "type": item_type,
        "value": item
    }
    variables[tokens[0]]['value'] = temp_array
    return 0


def length(tokens):
    """
    Expects exactly one token and stores its length in 'variables'.
    """
    if len(tokens) != 1:
        print("\033[91mlength:params error: \033[0mexpects 1 token")
        return 1 

    target = tokens[0]

    variables['len'] = {
        "cat": "preset",
        "type": "int",
        "value": len(target)
    }
    return 0


def stdload(tokens):
    """
    loads an output to a stream; can be accessed later
    """
    pass
    

    
def stdout(tokens):
    """
    stdout aggregates everything in the list, so no use for quotes
    to add a space you need to add a "_", this is done in the tokenizer
    also adds spaces after every index
    expected:
    ["hello","world"] -> helloworld
    """
    phrase = ""
    if len(tokens) < 1:
        return 1
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
    try:
        if not tokens:
            print("\033[91mstdin:params error: \033[0mplease add expected params")
            return 5

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
                    return 1
            elif var_type == "int":
                try:
                    int(var_val)
                except:
                    print(f"\033[91mstdin:type error: \033[0minvalid type provided, expected {var_type}")
                    return 1
            elif var_type == "flt":
                try:
                    float(var_val)
                except:
                    print(f"\033[91mstdin:type error: \033[0minvalid type provided, expected {var_type}")
                    return 1
            elif var_type == "bool":
                try:
                    if var_val.lower() in ("true","false"):
                        if var_val == "true":
                            var_val = 1
                        elif var_val == "false":
                            var_val = 0
                    else:
                        try:
                            var_val = int(var_val)
                            if var_val > 1 or var_val < 0:
                                print(f"\033[91mstdin:assignment error: \033[0mbool has to be either 0/1 or true/false")
                                return 1
                        except:
                            print(f"\033[91mstdin:assignment error: \033[0mbool has to be either 0/1 or true/false")
                            return 1
                except:
                    print(f"\033[91mstdin:type error: \033[0minvalid type provided, expected {var_type}")
                    return 1

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
    except:
        return 17


def std_operations(tokens):
    pass

def clear(void):
    try:
        os.system("clear")
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

def sort_array(tokens):
    if len(tokens) < 1:
        print("\033[91merror: sorting error: \033[0mnothing provided")
        return 1
    if isinstance(tokens[0],list):
        array = tokens[0]
        sorted_array = quicksort(array)
        variables["sorted"] = {
            "cat": "preset",
            "type": "arr",
            "value": sorted_array,
        }
        return 0
    else:
        print("\033[91merror: sorting error: \033[0mno array provided")
        return 1

def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2] 
    left = [x for x in arr if x < pivot] 
    middle = [x for x in arr if x == pivot]  
    right = [x for x in arr if x > pivot] 
    return quicksort(left) + middle + quicksort(right)



def import_libraries(tokens):
    for lib in tokens:
        imported_libraries.append(lib)
    print(imported_libraries)
    return 0

def file_assign(tokens):
    if len(tokens) < 1:
        print("\033[91merror: fset:\033[0m no file name given")
        return 1
    else:
        variables["fileInteraction"]["value"] = tokens[0]
        return 0

def file_write(tokens):
    if len(tokens) < 1:
        return 1
    if variables["fileInteraction"]["value"] == "void":
        print("\033[91merror: fwrite:\033[0m no file name has been assigned")
        return 1
    else:
        fwrite_filename = variables["fileInteraction"]["value"]
        with open(fwrite_filename,'a') as fwrite_file:
            write_output = " ".join(map(str, tokens))
            fwrite_file.writelines(f"{str(write_output)}\n")
        return 0

def file_erase(void):
    if variables["fileInteraction"]["value"] == "void":
        print("\033[91merror: fclear:\033[0m no file name has been assigned")
        return 1
    else:
        fwrite_filename = variables["fileInteraction"]["value"]
        with open(fwrite_filename,'w') as fwrite_file:
            pass
        return 0

def file_read(tokens):
    if len(tokens) < 1:
        print("\033[91merror: fread:\033[0m no content destination defined")
        return 1
    if variables["fileInteraction"]["value"] == "void":
        print("\033[91merror: fread:\033[0m no file name has been assigned")
        return 1
    fread_filename = variables["fileInteraction"]["value"]
    """
    if fread_filename.rfind(".") != -1:
        cleaned_filename = fread_filename[:fread_filename.rfind(".")]
    else:
        cleaned_filename = fread_filename
    """
    cont_destin = tokens[0]
    if cont_destin in structs:
        print(f"\033[91merror: fread:\033[0m{cont_destin} already exists")
        return 1
    fread_contents = []
    try:
        with open(fread_filename,"r") as fread_filecontents:
            for line in fread_filecontents:
                fread_contents.append(line.strip())
    except:
        print(f"\033[91merror: fread missing:\033[0m {fread_filename} was not found")
        return 9

    if  cont_destin not in structs:
        structs[cont_destin] = {}
    structs[cont_destin]["contents"] = {
                    "cat": "preset",
                    "type": "arr",
                    "value": fread_contents,
    }
    structs[cont_destin]["len"] = {
                    "cat": "preset",
                    "type": "int",
                    "value": len(fread_contents),
    }
    structs[cont_destin]["type"] = {
                    "cat": "preset",
                    "type": "str",
                    "value": fread_filename[fread_filename.rfind(".")+1:],
    }
    return 0


## --- user interation with the terminal --- 
def help():
    RESET = "\033[0m"
    BOLD = "\033[1m"
    BRIGHT_GREEN = "\033[92m"
    BLUE = "\033[94m"
    YELLOW = "\033[33m"
    CYAN = "\033[96m"
    
    print(f"\n{BOLD}CARBONSCRIPT HELP{RESET}")
    print("─" * 50)
    print(f"\n{BOLD}{BLUE}DESCRIPTION{RESET}")
    print(f"{RESET}CarbonScript is a toy interpretor built in Python3.\nDeveloped by {BRIGHT_GREEN}Saaim Japanwala{RESET} as a side project.\nBy no means is it the fastest,\nthe most effecient, or the best interpretor to ever be created, \033[3m\033[90mthats what python is for :){RESET}\nPlease enjoy my work!")
    print(f"\n{BOLD}{BLUE}DOCUMENTATION{RESET}")
    print(f"  {BRIGHT_GREEN}WebDocs{RESET}       https://sjapanwala.github.io/carbonscript/")
    print(f"  {BRIGHT_GREEN}README{RESET}        https://github.com/sjapanwala/carbonscript")


    print(f"\n{BOLD}{BLUE}CLI COMMANDS{RESET}")
    print(f"  {BRIGHT_GREEN}--update{RESET}      Updates the interpreter {YELLOW}(requires sudo){RESET}")
    print(f"  {BRIGHT_GREEN}--help{RESET}        Shows this help menu")
    print(f"  {BRIGHT_GREEN}--logs{RESET}        Shows lastests update logs")
    print(f"  {BRIGHT_GREEN}--v{RESET}           Displays interpreter version; download source")
    
    print(f"\n{BOLD}{BLUE}STARTUP INSTRUCTIONS{RESET}")
    print(f"  {BRIGHT_GREEN}env:show-tk{RESET}   Shows debug tokens")
    print(f"  {BRIGHT_GREEN}env:show-ec{RESET}   Shows return code")
    
    print(f"\n{BOLD}{BLUE}ERROR CODES{RESET}")
    print(f"  {BRIGHT_GREEN}  -1{RESET}          Unexptected Error; No Set Reason")
    print(f"  {BRIGHT_GREEN}   0{RESET}          Void; Nothing Abnormal")
    print(f"  {BRIGHT_GREEN}   1{RESET}          Ambiguous Error")
    print(f"  {BRIGHT_GREEN}   2{RESET}          Comment Code")
    print(f"  {BRIGHT_GREEN}   3{RESET}          Type Error")
    print(f"  {BRIGHT_GREEN}   4{RESET}          Syntax Error")
    print(f"  {BRIGHT_GREEN}   5{RESET}          Incompleted Parameters")
    print(f"  {BRIGHT_GREEN}   8{RESET}          Logical Artithemitc Error")
    print(f"  {BRIGHT_GREEN}   9{RESET}          File Interaction Error")
    print(f"  {BRIGHT_GREEN}   15{RESET}         Initialization Error")
    print(f"  {BRIGHT_GREEN}   16{RESET}         Initialized")
    print(f"  {BRIGHT_GREEN}   17{RESET}         Ctrl+C Detected")
    print(f"  {BRIGHT_GREEN}   81{RESET}         Unknown Library Imported")

    # Footer 
    print("\n" + "─" * 50)
    print(f"Run {CYAN}car{RESET} with arguments to execute operations")

def download_libs(args):
    file_cache = []
    approved_libs = []
    download_mirror = "https://raw.githubusercontent.com/sjapanwala/carbonscript/refs/heads/define/libraries/libs.txt"
    file_contents = subprocess.check_output(["curl", "-s", download_mirror], text=True)
    file_cache.extend(file_contents.splitlines())
    for libname in args:
        if libname in file_cache:  
            approved_libs.append(libname)
        else:
            print(f"\033[91merror: libdownload:\033[0m {libname} not in the official lib repo")
    if not approved_libs:  
        sys.exit(1)
    print(f"Downloading {len(approved_libs)} libraries...")
    for i in approved_libs:
        print(f"{i}   [{10 * '#'}]")

def update():

    
    # Colors and styling
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[32m"
    BRIGHT_GREEN = "\033[92m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    YELLOW = "\033[33m"
    CYAN = "\033[96m"
    
    # Spinner frames
    spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    
    # Path setup
    temp_file = os.path.expanduser("~/.temp_csc")
    bin_file = os.path.expanduser("/usr/local/bin/car")
    

    def clear_line():
        return "\r\033[K" 
    

    print(f"\n{BOLD}CARBONSCRIPT UPDATE{RESET}")
    print("─" * 50)
    
    def show_status(message, success=None, frames=5):
        for i in range(frames):
            if success is None:
                spin_char = spinner[i % len(spinner)]
                print(f"{clear_line()}{BLUE}{spin_char}{RESET} {message}", end="", flush=True)
                time.sleep(0.1)
        
        if success is True:
            print(f"{clear_line()}{BRIGHT_GREEN}✓{RESET} {message}", flush=True)
        elif success is False:
            print(f"{clear_line()}{RED}✗{RESET} {message}", flush=True)
    
    def prompt_user(prompt_text):
        print(f"{clear_line()}{CYAN}?{RESET} {prompt_text}", end=" ", flush=True)
        return input().strip().lower()
    
    show_status("Preparing update check...", success=None, frames=3)
    show_status("Preparing update check...", success=True)
    
    update_check = prompt_user("Check for updates? (y/n)")
    
    if update_check != "y":
        print(f"{clear_line()}{RED}✗{RESET} Update process aborted by user")
        exit(1)
    
    for i in range(10):
        spin_char = spinner[i % len(spinner)]
        print(f"{clear_line()}{BLUE}{spin_char}{RESET} Downloading update file... {i*10}%", end="", flush=True)
        time.sleep(0.1)
    
    try:
        subprocess.run(["curl", "-s", "-o", temp_file, "https://raw.githubusercontent.com/sjapanwala/carbonscript/refs/heads/define/cscript.py"])
        print(f"{clear_line()}{BRIGHT_GREEN}✓{RESET} Update file downloaded successfully")
    except Exception as e:
        print(f"{clear_line()}{RED}✗{RESET} Failed to download update file")
        print(f"{RED}Error: {e}{RESET}")
        exit(1)
    
    for i in range(5):
        spin_char = spinner[i % len(spinner)]
        print(f"{clear_line()}{BLUE}{spin_char}{RESET} Comparing version files...", end="", flush=True)
        time.sleep(0.1)
    
    try:
        update_size = os.path.getsize(temp_file)
        current_size = os.path.getsize(bin_file)
        
        if update_size != current_size:
            print(f"{clear_line()}{BRIGHT_GREEN}✓{RESET} New version available!")
            print(f"{CYAN}Current:{RESET} {current_size} bytes | {CYAN}Updated:{RESET} {update_size} bytes")
            
            apply_check = prompt_user("Apply updates? (y/n)")
            
            if apply_check == "y":
                # Apply update with progress on the same line
                for i in range(10):
                    spin_char = spinner[i % len(spinner)]
                    print(f"{clear_line()}{BLUE}{spin_char}{RESET} Applying update... {i*10}%", end="", flush=True)
                    time.sleep(0.1)
                
                subprocess.run(["sudo", "cp", temp_file, bin_file])
                print(f"{clear_line()}{BRIGHT_GREEN}✓{RESET} Update applied successfully")
                
                print(f"\n{BOLD}UPDATE NOTES:{RESET}")
                print("─" * 30)
                print(f"\n{BOLD}{BLUE}Check Out Update Information with \033[92mcar --logs{RESET}")
            else:
                print(f"{clear_line()}{YELLOW}⚠{RESET} Update canceled - No changes made")
                exit(1)
        else:
            print(f"{clear_line()}{BRIGHT_GREEN}✓{RESET} CarbonScript is already at the latest version")
    except Exception as e:
        print(f"{clear_line()}{RED}✗{RESET} Error checking updates")
        print(f"{RED}Error: {e}{RESET}")
        exit(1)
    subprocess.run(["rm",f"{temp_file}"])


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
                        rc = "\033[92m>>\033[0m"
                    elif returncode == 2:
                        rc = "\033[90m>>\033[0m"
                    else:
                        rc = "\033[91m>>\033[0m"
                    command = input(f"\n\033[0m{rc}\033[0m ")
                    tokens = tokenization(command)
                    returncode = func_caller(tokens)
                    variables["errorlevel"]['value'] = returncode
                    if envriornment_config["print_error_code"] == True:
                        if returncode != 0:
                            print(f"\033[97mExit Code: \033[91m{returncode}\033[0m")
                        else:
                            print(f"\033[97mExit Code: \033[92m{returncode}\033[0m")
        except KeyboardInterrupt:
            print("\rSession Ended Successfully; Goodbye")
            exit(1)


if __name__ == "__main__":
    ## starting components
    try:
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
        global imported_libraries
        imported_libraries = []
        variables['errorlevel']['value'] = 16
    except:
        variables['errorlevel']['value'] = 15
        print("\033[1;91merror: internal\033[0m internal interpreter error")

    """
    Args Analysis Breakdown
    --v:            Version
    env:show-ec     Shows Error Code (SYN. RULE show-ec)
    env:show-tk     Shows Token Arrays (SYN. RULE show-tk)
    --help          Help Screen w/ Error Code Map
    --update        Runs Updater Function
    --logs          Shows Update Logs
    --libutil       Downloads Libraries

    """
    if len(sys.argv) > 1:
        get_args()
        TEST = False
        if sys.argv[1] == "--v":
            print(f"CarbonScript Version: \033[92m{variables['version']['value']}\033[0m\nfrom: [www.github.com/sjapanwala/CarbonScript]")
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
        elif "--update" in sys.argv:
            update()
            exit(0)
        elif "--logs" in sys.argv:
            subprocess.run(["curl", "-s", "https://raw.githubusercontent.com/sjapanwala/carbonscript/refs/heads/define/updates.txt"])
            exit(0)
        elif "--libutil" in sys.argv:
            if len(sys.argv) < 3:
                print("\033[91mno library name provided\033[0m")
                exit(1)
            download_libs(sys.argv[2:])
            exit(0)
    returncode = 0
    main(returncode)
