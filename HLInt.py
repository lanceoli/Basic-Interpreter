class Compiler:

    RESERVED_WORDS = ["if", "else", "output", "integer", "double", "exit"]
    SYMBOLS = [":=", "==", "<", ">", "+", "-", "(", ")", "<<", ";"]

    def __init__(self):
        self.variables = {}
        self.variable_types = {}
        self.pending_if = None
        self.errors = []
        self.nospaces_code = []
        self.reserved_symbols = []

    def remove_spaces(self, code):
        return code.replace(" ", "").replace("\t", "")

    def extract_reserved_and_symbols(self, line):
        words = line.split()
        for word in words:
            for res_word in self.RESERVED_WORDS:
                if res_word in word:
                  self.reserved_symbols.append("Reserved Word: " + res_word)
            for sym in self.SYMBOLS:
                if sym in word:
                  self.reserved_symbols.append("Symbol: " + sym)

    def parse(self, line):
        line_no_spaces = self.remove_spaces(line)
        self.nospaces_code.append(line_no_spaces)
        self.extract_reserved_and_symbols(line)

        # remove the semicolon
        line = line.rstrip(';')

        # variable declaration
        if ':' in line and '=' not in line:
            parts = line.split(':')
            if len(parts) == 2:
                var, var_type = parts
                var = var.strip()
                var_type = var_type.strip().lower()
                if var_type in ['integer', 'double']:
                    self.variable_types[var] = var_type
                    self.variables[var] = None
                else:
                    self.errors.append(f"Error: Unsupported variable type '{var_type}'")
            else:
                self.errors.append(f"Error: Invalid variable declaration '{line}'")

        # variable assignment
        elif ':=' in line:
            parts = line.split(':=')
            if len(parts) == 2:
                var, value = parts
                var = var.strip()
                value = value.strip()
                if var in self.variable_types:
                    if self.variable_types[var] == 'double':
                        try:
                            self.variables[var] = float(value)
                        except ValueError:
                            self.errors.append(f"Error: Invalid value '{value}' for variable '{var}'")
                    elif self.variable_types[var] == 'integer':
                        try:
                            self.variables[var] = int(value)
                        except ValueError:
                            self.errors.append(f"Error: Invalid value '{value}' for variable '{var}'")
                else:
                    self.errors.append(f"Error: Variable '{var}' is not declared")
            else:
                self.errors.append(f"Error: Invalid assignment '{line}'")

        # if statements
        elif line.startswith("if(") and line.endswith(")"):
            condition = line[3:-1].strip()
            self.pending_if = condition

        # handle the statement following an if condition
        elif self.pending_if is not None:
            command = line.strip()
            if self.evaluate_condition(self.pending_if):
                if command.startswith("output<<"):
                    content = command[len("output<<"):].strip()
                    if content.startswith('"') and content.endswith('"'):
                        print(content[1:-1])  # print string without the quotes
                    else:
                        try:
                            result = self.evaluate_expression(content)
                            print(result)
                        except Exception as e:
                            self.errors.append(f"Error: {e}")

            self.pending_if = None

        # output for variables and expressions
        elif line.startswith("output<<"):
            content = line[len("output<<"):].strip()
            if content.startswith('"') and content.endswith('"'):
                print(content[1:-1])  # print string without the quotes
            else:
                try:
                    result = self.evaluate_expression(content)
                    print(result)
                except Exception as e:
                    self.errors.append(f"Error: {e}")

        else:
            self.errors.append(f"Error: Invalid input format '{line}'")

    def evaluate_expression(self, expression):
        if '+' in expression:
            left_var, right_var = expression.split('+')
            left_var = left_var.strip()
            right_var = right_var.strip()
            if left_var in self.variables and right_var in self.variables:
                return self.variables[left_var] + self.variables[right_var]
            else:
                raise ValueError(f"One or both variables '{left_var}' and '{right_var}' are not defined")
        elif '-' in expression:
            left_var, right_var = expression.split('-')
            left_var = left_var.strip()
            right_var = right_var.strip()
            if left_var in self.variables and right_var in self.variables:
                return self.variables[left_var] - self.variables[right_var]
            else:
                raise ValueError(f"One or both variables '{left_var}' and '{right_var}' are not defined")
        else:
            if expression in self.variables:
                return self.variables[expression]
            else:
                raise ValueError(f"Variable '{expression}' is not defined")

    def evaluate_condition(self, condition):
        # evaluate condition
        if '<' in condition:
            left_var, right_value = condition.split('<')
            left_var = left_var.strip()
            right_value = right_value.strip()

            # Check if the right value is a variable or a literal
            if right_value in self.variables:
                right_value = self.variables[right_value]
            else:
                try:
                    right_value = float(right_value)
                except ValueError:
                    raise ValueError(f"Invalid value in condition: '{right_value}'")

            if left_var in self.variables:
                return self.variables[left_var] < right_value
            else:
                raise ValueError(f"Variable '{left_var}' is not defined")

        elif '>' in condition:
            left_var, right_value = condition.split('>')
            left_var = left_var.strip()
            right_value = right_value.strip()

            if right_value in self.variables:
                right_value = self.variables[right_value]
            else:
                try:
                    right_value = float(right_value)
                except ValueError:
                    raise ValueError(f"Invalid value in condition: '{right_value}'")

            if left_var in self.variables:
                return self.variables[left_var] > right_value
            else:
                raise ValueError(f"Variable '{left_var}' is not defined")

        elif '==' in condition:
            left_var, right_value = condition.split('==')
            left_var = left_var.strip()
            right_value = right_value.strip()

            if right_value in self.variables:
                right_value = self.variables[right_value]
            else:
                try:
                    right_value = float(right_value)
                except ValueError:
                    raise ValueError(f"Invalid value in condition: '{right_value}'")

            if left_var in self.variables:
                return self.variables[left_var] == right_value
            else:
                raise ValueError(f"Variable '{left_var}' is not defined")

        else:
            raise ValueError(f"Unsupported condition '{condition}'")

    def run(self):
        line_num = 0
        lines = []
        with open("PROG1.HL") as file:
            lines = file.readlines()

        while line_num < len(lines):
            try:
                line = lines[line_num]

                if line.strip().lower() == "exit":
                    break

                self.parse(line.strip())

                line_num += 1

            except Exception as e:
                self.errors.append(f"Error: {e}")

        with open("NOSPACES.TXT", "w") as nospaces_file:
            nospaces_file.write("\n".join(self.nospaces_code))

        with open("RES_SYM.TXT", "w") as res_sym_file:
            res_sym_file.write("\n".join(self.reserved_symbols))

        # output error
        if self.errors:
            print("ERROR")
            for error in self.errors:
                print(error)
        else:
            print("NO ERROR(S) FOUND")

# run compiler
compiler = Compiler()
compiler.run()
