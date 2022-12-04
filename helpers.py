from codeline import CodeLine
from termcolor import colored


def loadScript(file_name):
    
    with open(file_name, "r") as file:
        code_lines = []
        for i, line in enumerate(file):
            if not line:
                continue
            code_lines.append(CodeLine(line, i + 1, code_lines[-1] if code_lines else None))

    return code_lines

def saveScript(code_lines, file_name):
    script = ''
    for code in code_lines:
        script += code.line
    with open(file_name, 'w') as file:
        file.write(script)
    print(colored(f'New file saved to: {file_name}', 'blue'))

def printErrors(code_lines):
    errors_count = 0

    
    for code_line in code_lines:
        if code_line.check_syntax():
            for error in code_line.error_types:
                errors_count += 1
                print(colored(f'Error at line {code_line.line_number}: {error.error_type}', 'red'))
    print(colored(f'In total, there are {errors_count} bug(s) in your script!', 'red'))

def fixErrors(code_lines):
    for code_line in code_lines:
        if code_line.error_types:
            if code_line.fix():
                print(colored(f'Fixed error at line {code_line.line_number}.', 'green'))
    return code_lines