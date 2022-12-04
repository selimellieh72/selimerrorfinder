import re
import keyword
import builtins

from syntax_error import SyntaxError

VALID_KEYWORDS = ['for', 'if', 'else', 'elif', 'while', 'print', 'range']

class CodeLine:
    defined_variables = []
    def __init__(self, line, line_number, previous_line):
        self.line = line
        self.line_number = line_number
        self.error_types = []
        self.previous_line = previous_line

    def check_syntax(self):
        has_error = False
        check_methods = [
                    self.__check_missing_colon,
                    self.__check_missing_indentation,
                    self.__check_unmatched_quotes,
                    self.__check_missing_parenthesis,

                    self.__check_invalid_assignment,
                    self.__check_invalid_variable_name,
                    self.__check_invalid_multiplication,
                    self.__check_in_use_with_for,
                    self.__check_undefined_variable,
                    self.__check_comparaison_operator,
                    self.__check_for_invalid_keywords,
                    self.__check_comma_float,
                    self.__check_invalid_else_clause,
                    self.__check_incorrect_parameters_seperator,
                   
                ]
        for check in check_methods:
            if check():
                has_error = True
        return has_error

        

    def __check_missing_indentation(self):
    
        if self.previous_line and re.match(r'def|for|while|if|else|elif', self.previous_line.line):
            match = re.match(r'^\s+', self.line)
            if not match:
                self.error_types.append(SyntaxError("Missing indentation", self.__fix_missing_indentation)) 
                return True
        return False

    def __check_missing_colon(self):
        pattern = r'(?:\s*|^)(?:def|for|while|if|else|elif)\s+[^:]+$'
        match = re.match(pattern, self.line)
   
        if match:
            self.error_types.append(SyntaxError("Missing colon", self.__fix_missing_colon))
            return True

        return False

    def __check_missing_parenthesis(self):
        count = 0
        for c in self.line:
            if c == '(':
                count += 1
            if c == ')':
                count -= 1
        if count != 0:
            self.error_types.append(SyntaxError("Missing parenthesis", self.__fix_missing_parenthesis))
            return True

        return False

    def __check_invalid_assignment(self):
        if not re.match(r'(?:\s*|^)(if|for|while|elif|else)', self.line):

            pattern = r'\b[a-zA-Z_]\w*\s*(==|!=|:)\s*\w*'
            match = re.search(pattern, self.line)
            if match:
                self.error_types.append(SyntaxError("Invalid assignment operator", lambda: self.__fix_invalid_assignment(match)))
                return True

        return False

    def __check_invalid_variable_name(self):

        pattern = r'\s*([\w]+)\s*(?=\=)'
        match = re.search(pattern, self.line)
        var_name = match.group(1).strip() if match else None
        
        if match and not var_name.isdigit() and not keyword.iskeyword(var_name) and not var_name in dir(builtins):
            if not var_name.isidentifier():
                self.error_types.append(SyntaxError("Invalid variable name", lambda: self.__fix_invalid_variable_name(var_name)))
                return True
            CodeLine.defined_variables.append(var_name)
        
        return False
    
    def __check_undefined_variable(self):
        skip_if_present = ['Invalid assignment operator' , 'Incorrect use of multiplication operator']
        if any(x in list(map(lambda error: error.error_type, self.error_types)) for x in skip_if_present):
            return False


        pattern = r'(?:^|\s|\()([a-zA-Z_][\w]*)(?!\s*[\'\"])(?=\s|$|\))'


        for var_name in re.findall(pattern, self.line):
            if not var_name.strip().lower() in dir(builtins) and not keyword.iskeyword(var_name.strip().lower()) and var_name not in CodeLine.defined_variables:

                self.error_types.append(SyntaxError("Undefined variable", lambda: None, False))
                return True


        return False

    def __check_unmatched_quotes(self):
        if self.line.count("'") % 2 == 1 or self.line.count('"') % 2 == 1:
            self.error_types.append(SyntaxError("Unmatched quotes", self.__fix_unmatched_quotes))
            return True
        return False

    def __check_comparaison_operator(self):
        if not re.match(r"^(if|elif|while)\s", self.line):
            return False

    
        if re.search(r"==|!=|<|>|<=|>=", self.line):
            return False


        self.error_types.append(SyntaxError("Missing comparison operator", self.__fix_comparaison_operator))
        return True


    def __check_in_use_with_for(self):
        if self.line.strip().startswith('for'):
            self.defined_variables.append(self.line.split()[1])
            match = re.match(r'(?:\s*|^)for\b(?!.*\bin\b)', self.line)
            if match:
                
                self.error_types.append(SyntaxError('In keyword must be used with a for loop', self.__fix_in_use_with_for))
                return True
            
        return False
    


    def __check_for_invalid_keywords(self):
        invalid_keyword_pattern = re.compile(r'\b(' + '|'.join(VALID_KEYWORDS) + r')\b', re.IGNORECASE)

        match = invalid_keyword_pattern.search(self.line)

        if match and self.line[match.start():match.end()] not in VALID_KEYWORDS:
            self.error_types.append(SyntaxError("Invalid keyword", self.__fix_invalid_keywords))
            return True

        return False

    def __check_comma_float(self):
        match = re.search(r'[+-]?\d+\,\d*', self.line)
        if match:
            self.error_types.append(SyntaxError("Invalid floating point number", self.__fix_comma_float))
            return True

        return False

    def __check_invalid_multiplication(self):
        pattern = r'\d+\s*x\s*\d+'
        match = re.search(pattern, self.line)
        if match:
            self.error_types.append(SyntaxError('Incorrect use of multiplication operator', self.__fix_invalid_multiplication))
            return True

        return False

    def __check_invalid_else_clause(self):
    
        pattern = r'\belse\s*\w+:?'
        match = re.match(pattern, self.line)
        if match:
          
            self.error_types.append(SyntaxError("Invalid else clause", self.__fix_invalid_else_clause))
            return True

        return False

    def __check_incorrect_parameters_seperator(self):
        pattern = r";(?!.*\'|.*\")"
        match = re.search(pattern, self.line)
        if match:
            self.error_types.append(SyntaxError('Invalid use of parameters/objects seperator', self.__fix_incorrect_parameters_seperator))
            return True
        return False
                
    def fix(self):
        fixed = False
        for error in self.error_types:
            if error.is_fixable:
                error.fix()
                fixed = True
        return fixed

    def __fix_missing_indentation(self):
        self.line = '\t' + self.line

    def __fix_missing_colon(self):
        self.line = self.line.strip() + ':\n' 

    def __fix_invalid_assignment(self, match):
        self.line = self.line.replace(match.group(1), '=')
    def __fix_invalid_variable_name(self, var_name):
        self.line = self.line.replace(var_name, re.sub('\W|^(?=\d)','_', var_name))

    def __fix_comparaison_operator(self):
        variable, constant = self.line.split("=")
        self.line = f"{variable} == {constant}"

    def __fix_in_use_with_for(self):
        self.line = re.sub(r"^\s*for\s+(\S+)\s+(.+):$", r"for \1 in \2:", self.line)
    
    def __fix_invalid_keywords(self):

        for keyword in VALID_KEYWORDS:
            self.line = re.sub(rf"\b{keyword}\b", keyword, self.line, flags=re.IGNORECASE)

    def __fix_comma_float(self):
        self.line =  re.sub(r"([+-]?\d+),(\d+)", r"\1.\2", self.line)

    def __fix_invalid_multiplication(self):
        self.line = re.sub(r"(\d+\s*)x(\s*\d+)", r"\1*\2", self.line)

    def __fix_invalid_else_clause(self):
        self.line = 'else:\n'
    
    def __fix_incorrect_parameters_seperator(self):
        self.line = re.sub(r'(.*);(.*)', r'\1,\2', self.line)

    def __fix_missing_parenthesis(self):
        left_count = 0
        right_count = 0
        for c in self.line:
            if c == '(':
                left_count += 1
            elif c == ')':
                right_count += 1
        if left_count > right_count:
            self.line = self.line.strip() + ')' * (left_count - right_count) + '\n'
        elif right_count > left_count:
            self.line = '(' * (right_count - left_count) + self.line

    def __fix_unmatched_quotes(self):
        if self.line.count("'") % 2 == 1:
            self.line = self.line.strip() + "'" + '\n'
        if self.line.count('"') % 2 == 1:
            self.line = self.line.strip() + '"' + '\n'



