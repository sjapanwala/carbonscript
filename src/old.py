
"""
def fi(tokens):
    global fi_code
    if len(tokens) < 1:
        print("\033[91mif:params error: \033[0mnot enough params provided")
        return 5

    condition_validity = tokens[0] == True

    # Grab code block
    if_instructions = []
    brace_count = 0a

    if file_mode:
        with open(file_path, "r") as file:
            lines = file.readlines()

        found_block = False
        for line in lines:
            line_stripped = line.strip()

            if not found_block and line_stripped.startswith("if") and "{" in line_stripped:
                found_block = True
                brace_count += 1
                continue

            if found_block:
                brace_count += line_stripped.count("{")
                brace_count -= line_stripped.count("}")

                if brace_count <= 0:
                    break

                if_instructions.append(line_stripped)
    else:
        brace_count = 1
        while brace_count > 0:
            file_input = input("if;> ")
            if not file_input.strip():
                continue
            brace_count += file_input.count("{")
            brace_count -= file_input.count("}")
            if brace_count > 0 or (file_input.strip() != "}" and brace_count == 0):
                if_instructions.append(file_input)
    
    func_ignore.extend(if_instructions)
    print(f"if:{if_instructions}")
    if condition_validity:
        for instr in if_instructions:
            returncode = func_caller(tokenization(instr))
            if returncode not in (0, 2):
                return returncode
        fi_code = 0  # success
    else:
        fi_code = 1  # failed

    return 0


def elsefi(tokens):
    global fi_code

    if len(tokens) < 1:
        print("\033[91melsefi:params error: \033[0mnot enough params provided")
        return 5


    condition_validity = tokens[0] == True
    elsefi_instructions = []
    brace_count = 0

    if file_mode:
        with open(file_path, "r") as file:
            lines = file.readlines()

        found_block = False
        for line in lines:
            line_stripped = line.strip()

            # Look for the start of an elsefi block
            if not found_block and line_stripped.startswith("ifelse") and "{" in line_stripped:
                found_block = True
                brace_count += 1
                continue

            if found_block:
                elsefi_instructions.append(line_stripped)
                brace_count += line_stripped.count("{")
                brace_count -= line_stripped.count("}")

                if brace_count <= 0:
                    break
    else:
        brace_count = 1
        while brace_count > 0:
            file_input = input("ifelse;> ")
            if not file_input.strip():
                continue
            elsefi_instructions.append(file_input)
            brace_count += file_input.count("{")
            brace_count -= file_input.count("}")

    func_ignore.extend(elsefi_instructions)
    print(f"ifelse:{elsefi_instructions}")
    if fi_code != 1:
        fi_code = 1
        return 0  
    if condition_validity:
        for instr in elsefi_instructions:
            returncode = func_caller(tokenization(instr))
            if returncode not in (0, 2):
                return returncode
        fi_code = 0
    return 0

def default(tokens):
    global fi_code

    if fi_code != 1:
        return 0  # Skip if previous condition already succeeded or not in a chain

    if len(tokens) < 1 and not file_mode:
        print("\033[91mdefault:params error: \033[0mnot enough params provided")
        return 5

    default_instructions = []
    brace_count = 0

    if file_mode:
        with open(file_path, "r") as file:
            lines = file.readlines()

        found_block = False
        for line in lines:
            line_stripped = line.strip()

            if not found_block and line_stripped.startswith("default") and "{" in line_stripped:
                found_block = True
                brace_count += 1
                continue

            if found_block:
                default_instructions.append(line_stripped)
                brace_count += line_stripped.count("{")
                brace_count -= line_stripped.count("}")

                if brace_count <= 0:
                    break
    else:
        brace_count = 1
        while brace_count > 0:
            file_input = input("default;> ")
            if not file_input.strip():
                continue
            default_instructions.append(file_input)
            brace_count += file_input.count("{")
            brace_count -= file_input.count("}")

    func_ignore.extend(default_instructions)
    print(f"[DEBUG] default block collected: {default_instructions}")

    for instr in default_instructions:
        returncode = func_caller(tokenization(instr))
        if returncode not in (0, 2):
            return returncode

    # End of conditional chain
    return 0
"""
