import re
import sys
import os
import ast

BLANK_LINES = 0


def check_s001_line_length(path, string, number):
    if len(string) >= 80:
        return f'{path}: Line {number}: S001 Too long'
    return None


def check_s002_indentation(path, string, number):
    indentation = re.match(r'^\s+', string.rstrip())
    if indentation:
        # print(number, len(indentation.group()))
        if len(indentation.group()) % 4 != 0:
            return f'{path}: Line {number}: S002 Indentation is not a multiple of four'
        return None


def check_s003_semicolons(path, string, number):
    unnecessary_semicolon = False
    if '#' in string:
        str_list = string.split('#')
        if ';' in str_list[0]:
            unnecessary_semicolon = True
    elif '"' in string:
        ind_1 = string.find('"')
        ind_2 = string.rfind('"')
        if ';' in string[:ind_1] or ';' in string[ind_2:]:
            unnecessary_semicolon = True
    elif "'" in string:
        ind_1 = string.find("'")
        ind_2 = string.rfind("'")
        if ';' in string[:ind_1] or ';' in string[ind_2:]:
            unnecessary_semicolon = True
    elif ';' in string:
        unnecessary_semicolon = True
    '''accept_template = r'(.+)?((#.+)|(\'.+\')|(\".+\"))(.+)?'
    match_result = re.match(accept_template, string)
    if match_result and match_result.group(6) and ';' in match_result.group(6):
        print(match_result.group(6))
        unnecessary_semicolon = True
    elif not match_result and ';' in string:
        unnecessary_semicolon = True'''
    if unnecessary_semicolon:
        return f'{path}: Line {number}: S003 Unnecessary semicolon'
    return None


def check_s004_spaces_before_inline_comments(path, string, number):
    error = False
    if '#' in string:
        hash_index = string.index('#')
        if hash_index != 0:
            if hash_index == 1:
                error = True
            elif string[hash_index - 1] != ' ' or string[hash_index - 2] != ' ':
                error = True
    if error:
        return f'{path}: Line {number}: S004 At least two spaces required before inline comments'
    return None


def check_s005_todo(path, string, number):
    if re.search('#.+TODO', string, flags=re.IGNORECASE):
        return f'{path}: Line {number}: S005 TODO found'
    return None


def check_s006_blank_lines(path, string, number):
    global BLANK_LINES
    error = False
    if string.rstrip():
        # print(number, string.rstrip(), BLANK_LINES)
        if BLANK_LINES > 2:
            b_lines = BLANK_LINES
            BLANK_LINES = 0
            return f'{path}: Line {number}: S006 More than two blank lines used before this line'
        BLANK_LINES = 0
    else:
        # print(number)
        BLANK_LINES += 1
    return None


def check_s007_spaces_class_func_names(path, string, number):
    class_func_match = re.match(r'(\s+)?(class|def)(\s+)(.+)(\(|:)', string)
    if class_func_match:
        if len(class_func_match.group(3)) > 1:
            return f"{path}: Line {number}: S007 Too many spaces after '{class_func_match.group(2)}'"
    return None


def check_s008_class_name_camel_case(path, string, number):
    class_match = re.match(r'class(\s+)(.+)(\(|:)?', string)
    class_name_match = re.match(r'class(\s+)(([A-Z][a-z]+)+)', string)
    if class_match and not class_name_match:
        return f"{path}: Line {number}: S008 Class name '{class_match.group(2)}' should use CamelCase"
    return None


def check_s009_func_name_shake_case(path, string, number):
    func_match = re.match(r'(\s+)?def(\s+)(.+)\(', string)
    func_name_match = re.match(r'(\s+)?def(\s+)([a-z0-9_]+)\(', string)
    if func_match and not func_name_match:
        return f"{path}: Line {number}: S009 Function name '{func_match.group(3)}' should use snake_case"
    return None


def check_s010_arg_name_snake_case(path):
    code = open(path).read()
    tree = ast.parse(code)
    nodes = ast.walk(tree)
    s = []
    error = False
    for node in nodes:
        if isinstance(node, ast.FunctionDef):
            for argument_name in [a.arg for a in node.args.args]:
                if re.match(r'^[A-Z]', argument_name):
                    error = True
                    s.append(f"{path}: Line {node.lineno}: S010 Argument name {argument_name} should be written in snake_case")
    if error:
        return s
    return None


def check_s011_var_snake_case(path):
    code = open(path).read()
    tree = ast.parse(code)
    nodes = ast.walk(tree)
    s = []
    s_temp = []
    error = False
    for node in nodes:
        if isinstance(node, ast.Name):
            variable_name = node.id
            if re.match(r'^[A-Z]', variable_name):
                error = True
                temp = f'S011 Variable {variable_name} in function should be snake_case'
                if temp not in s_temp:
                    s_temp.append(temp)
                    s.append(f"{path}: Line {node.lineno}: S011 Variable {variable_name} in function should be snake_case")
    if error:
        return s
    return None


def check_s012_default_arg_mutable(path):
    code = open(path).read()
    tree = ast.parse(code)
    nodes = ast.walk(tree)
    s = []
    error = False
    for node in nodes:
        if isinstance(node, ast.FunctionDef):
            for var in node.args.defaults:
                if isinstance(var, ast.List):
                    error = True
                    s.append(f"{path}: Line {node.lineno}: S012 Default argument value is mutable")
    if error:
        return s
    return None


def check_file(path):
    result_list = []
    with open(path, 'r') as fh:
        line_number = 1
        for line in fh:
            result_list.append(check_s001_line_length(path, line, line_number))
            result_list.append(check_s002_indentation(path, line, line_number))
            result_list.append(check_s003_semicolons(path, line, line_number))
            result_list.append(check_s004_spaces_before_inline_comments(path, line, line_number))
            result_list.append(check_s005_todo(path, line, line_number))
            result_list.append(check_s006_blank_lines(path, line, line_number))
            result_list.append(check_s007_spaces_class_func_names(path, line, line_number))
            result_list.append(check_s008_class_name_camel_case(path, line, line_number))
            result_list.append(check_s009_func_name_shake_case(path, line, line_number))
            line_number += 1
    result = check_s010_arg_name_snake_case(path)
    if result:
        result_list.extend(result)
    result = check_s011_var_snake_case(path)
    if result:
        result_list.extend(result)
    result = check_s012_default_arg_mutable(path)
    if result:
        result_list.extend(result)
    result_list = [(int(re.search(r'Line\s(\d+)', elem).group(1)), elem) for elem in result_list if elem is not None]
    for elem in sorted(result_list):
        print(elem[1])


def file_manager(path):
    if os.path.isfile(path):
        check_file(path)
    elif os.path.isdir(path):
        for root, d_names, f_names in os.walk(path):
            for name in f_names:
                if name.endswith('py'):
                    new_path = os.path.join(root, name)
                    check_file(new_path)


if __name__ == "__main__":
    args = sys.argv
    my_path = args[1]
    file_manager(my_path)
