import math
from pydoc import classname
from unicodedata import name
from SymbolTable import SymbolTable
from VmWriter import VmWriter


def xml_wrapper(tag, strs, indent):
    output = ""
    for i in range(0, indent):
        output += ' '

    if isinstance(strs, str):
        strs = strs.strip()
        strs = strs.rstrip()
        if strs.startswith('<'):
            space = ""
            for _ in range(0, indent+1):
                space += ' '
            strs = '\n' + space+strs+'\n'
            space = space[1:]
            output += f"<{tag}> {strs}{space}</{tag}>"+'\n'
            return output

    output += f"<{tag}> {strs} </{tag}>"+'\n'

    return output


class CompilationEngine:

    def __init__(self, tokenizer, vm_writer) -> None:
        self.__class_name = ''
        self.__label_count = 0
        self.__symbolTable = SymbolTable()
        self.tokenizer = tokenizer
        self.__vm_writer = vm_writer
        pass

    def compile(self):
        return self.compile_class()

    def compile_class(self):
        if(self.tokenizer.has_more_tokens()):
            # class
            self.tokenizer.advance()

            self.tokenizer.advance()
            # name
            self.__class_name = self.tokenizer.token_value()
            print(self.__class_name)
            self.tokenizer.advance()

            # {
            self.tokenizer.advance()
            while(self.tokenizer.has_more_tokens()):
                match self.tokenizer.token_value():
                    case "static" | "field":
                        self.compile_class_var_dec()
                        pass
                    case "constructor" | "function" | "method":
                        self.compile_subroutine_dec()
                        pass
                    case '}':
                        return
                pass
        pass

    def compile_class_var_dec(self):
        # field/static

        kind = self.tokenizer.token_value()

        self.tokenizer.advance()
        # type

        type = self.tokenizer.token_value()

        self.tokenizer.advance()
        # name
        name = self.tokenizer.token_value()
        self.tokenizer.advance()

        self.__symbolTable.define(name, type, kind)

        while (self.tokenizer.token_value() == ','):
            # ,
            self.tokenizer.advance()
            # name
            name = self.tokenizer.token_value()
            self.__symbolTable.define(name, type, kind)

            self.tokenizer.advance()

        # ;
        self.tokenizer.advance()
        pass

    def compile_subroutine_dec(self):

        self.__symbolTable.start_subroutine()

        # method/function

        type = self.tokenizer.token_value()
        if self.tokenizer.token_value() == "method":
            self.__symbolTable.define(
                name="this", type=self.__class_name, kind="argument")
            pass

        self.tokenizer.advance()
        # void
        self.tokenizer.advance()
        # name
        name = self.tokenizer.token_value()

        self.tokenizer.advance()
        # (

        self.tokenizer.advance()

        # parameterList
        self.compile_parameter_list()

        # )
        self.tokenizer.advance()

        # subroutineBody

        self.compile_subroutine_body(type, name)

        self.__vm_writer.write_new_line()
        pass

    def compile_parameter_list(self):

        if self.tokenizer.token_value() == ')':
            return

        # type
        type = self.tokenizer.token_value()
        self.tokenizer.advance()
        # name
        name = self.tokenizer.token_value()
        self.__symbolTable.define(name, type, "argument")
        self.tokenizer.advance()

        while self.tokenizer.token_value() == ',':
            # ,
            self.tokenizer.advance()
            # type
            type = self.tokenizer.token_value()
            self.tokenizer.advance()
            # name
            name = self.tokenizer.token_value()
            self.__symbolTable.define(name, type, "argument")
            self.tokenizer.advance()

        pass

    def compile_subroutine_body(self, subroutine_type, subroutine_name):
        nLocals = 0
        # {
        self.tokenizer.advance()
        # var
        while self.tokenizer.token_value() == "var":
            nLocals += self.compile_var_dec()
            pass

        self.__vm_writer.write_function(
            self.__class_name+'.'+subroutine_name, nLocals)

        if subroutine_type == 'constructor':
            subroutine_name = 'new'
            self.__vm_writer.write_push(
                "constant", self.__symbolTable.get_class_var_count("field"))
            self.__vm_writer.write_call(
                "Memory.alloc", 1)
            self.__vm_writer.write_pop("pointer", 0)

        elif subroutine_type == "method":
            self.__vm_writer.write_push('argument', 0)
            self.__vm_writer.write_pop('pointer', 0)

        # statements
        self.compile_statements()

        # }
        self.tokenizer.advance()
        pass

    def compile_var_dec(self):
        count = 0
        # var
        self.tokenizer.advance()
        # type
        type = self.tokenizer.token_value()
        self.tokenizer.advance()
        # name
        name = self.tokenizer.token_value()
        self.__symbolTable.define(name, type, "local")
        self.tokenizer.advance()
        count += 1

        while self.tokenizer.token_value() == ',':
            # ,
            self.tokenizer.advance()
            # name
            name = self.tokenizer.token_value()
            self.__symbolTable.define(name, type, "local")

            self.tokenizer.advance()
            count += 1

        # ;
        self.tokenizer.advance()

        return count

    def compile_statements(self):

        while(self.tokenizer.has_more_tokens()):

            match(self.tokenizer.token_value()):
                case "let":
                    self.compile_let_statement()
                    pass
                case "if":
                    self.compile_if_statement()
                    pass
                case "while":
                    self.compile_while_statement()
                    pass
                case "do":
                    self.compile_do_statement()
                    pass
                case "return":
                    self.compile_return_statement()
                    pass
                case _:
                    return
        pass

    def compile_if_statement(self):
        # if
        self.tokenizer.advance()
        # (
        self.tokenizer.advance()

        # expression
        self.compile_expression()

        # )
        self.tokenizer.advance()
        # {
        self.tokenizer.advance()

        label_count = self.__label_count
        self.__label_count += 1

        self.__vm_writer.write_if_goto(f'if{label_count}')
        self.__vm_writer.write_goto(f'else{label_count}')
        self.__vm_writer.write_label(f'if{label_count}')

        # statements
        self.compile_statements()
        self.__vm_writer.write_goto(f'end{label_count}')
        # }
        self.__vm_writer.write_label(f'else{label_count}')

        self.tokenizer.advance()
        if(self.tokenizer.token_value() == "else"):
            # else
            self.tokenizer.advance()
            # {
            self.tokenizer.advance()
            # statements
            self.compile_statements()
            # }
            self.tokenizer.advance()
        self.__vm_writer.write_label(f"end{label_count}")

        pass

    def compile_while_statement(self):
        # while
        self.tokenizer.advance()
        # (
        self.tokenizer.advance()
        label_count = self.__label_count
        self.__label_count += 1

        self.__vm_writer.write_label(f'while{label_count}')
        # expression
        self.compile_expression()
        self.__vm_writer.write_if_goto(f'if{label_count}')
        self.__vm_writer.write_goto(f'else{label_count}')
        self.__vm_writer.write_label(f'if{label_count}')

        # )
        self.tokenizer.advance()
        # {
        self.tokenizer.advance()
        # statement
        self.compile_statements()
        self.__vm_writer.write_goto(f'while{label_count}')
        # }
        self.__vm_writer.write_label(f'else{label_count}')
        self.tokenizer.advance()

    def compile_do_statement(self):
        # do
        self.tokenizer.advance()
        # name
        name = self.tokenizer.token_value()
        nArgs = 0
        self.tokenizer.advance()

        if(self.tokenizer.token_value() == '.'):
            if(self.__symbolTable.is_defined(name)):
                self.write_push_identifier(name)
                nArgs += 1
                # .
                self.tokenizer.advance()
                # name
                name = self.__symbolTable.get_type_of(
                    name)+"."+self.tokenizer.token_value()
                self.tokenizer.advance()
            else:
                # .
                self.tokenizer.advance()
                # name
                name += f".{self.tokenizer.token_value()}"
                self.tokenizer.advance()
        else:
            self.__vm_writer.write_push("pointer", 0)
            name = self.__class_name+"."+name
            nArgs += 1

        # (
        self.tokenizer.advance()

        # expressionList
        if self.tokenizer.token_value() != ')':
            nArgs += self.compile_expression_list()

        # )
        self.tokenizer.advance()

        # ;
        self.tokenizer.advance()

        self.__vm_writer.write_call(name, nArgs)
        self.__vm_writer.write_pop("temp", 0)

    def compile_return_statement(self):
        # return
        self.tokenizer.advance()
        # expression
        if self.tokenizer.token_value() != ';':

            self.compile_expression()
        else:
            self.write_push_int(0)

        # ;
        self.tokenizer.advance()

        self.__vm_writer.write_return()
        pass

    def compile_let_statement(self):
        # let
        self.tokenizer.advance()
        # name
        name = self.tokenizer.token_value()
        is_array = False
        self.tokenizer.advance()

        if self.tokenizer.token_value() == '[':
            is_array = True

            # [
            self.tokenizer.advance()
            # expression
            self.compile_expression()
            # ]

            self.write_push_identifier(name)
            # add the value of base array address and new address
            self.__vm_writer.write_arithmetic('+')

            self.tokenizer.advance()

        # =
        self.tokenizer.advance()
        # expression
        self.compile_expression()

        # ;
        self.tokenizer.advance()

        if not is_array:
            if self.__symbolTable.is_in_subroutine_table(name):
                self.__vm_writer.write_pop(self.__symbolTable.get_kind_of(
                    name), self.__symbolTable.get_index_of(name))
            else:
                if self.__symbolTable.get_kind_of(name) == "static":
                    self.__vm_writer.write_pop(
                        "static", self.__symbolTable.get_index_of(name))
                else:
                    self.__vm_writer.write_pop(
                        "this", self.__symbolTable.get_index_of(name))
        else:
            self.__vm_writer.write_pop("temp", 0)
            self.__vm_writer.write_pop("pointer", 1)
            self.__vm_writer.write_push("temp", 0)
            self.__vm_writer.write_pop("that", 0)

    def compile_expression(self):
        self.compile_term()

        while True:
            match self.tokenizer.token_value():
                case '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=':
                    # op
                    op = self.tokenizer.token_value()
                    self.tokenizer.advance()

                    self.compile_term()
                    self.__vm_writer.write_arithmetic(op)

                case _:
                    return

        return output

    def compile_term(self):

        # expression
        if self.tokenizer.token_value() == '(':
            # (
            self.tokenizer.advance()

            # expression
            self.compile_expression()

            # )
            self.tokenizer.advance()
            pass
        # unaryOP term
        elif (self.tokenizer.token_value() == '~') or (self.tokenizer.token_value() == '-'):

            op = self.tokenizer.token_value()
            self.tokenizer.advance()
            self.compile_term()
            self.__vm_writer.write_arithmetic(op)

            pass
        else:
            # name
            name = self.tokenizer.token_value()
            token_type = self.tokenizer.token_type()
            self.tokenizer.advance()

            # varName[expressionList]
            if self.tokenizer.token_value() == '[':

                # [
                self.tokenizer.advance()

                # expression
                self.compile_expression()

                self.write_push_identifier(name)
                # add the value of base array address and new address
                self.__vm_writer.write_arithmetic('+')
                self.__vm_writer.write_pop("pointer", 1)
                self.__vm_writer.write_push("that", 0)
                # ]
                self.tokenizer.advance()

            elif (self.tokenizer.token_value() == '(') or (self.tokenizer.token_value() == '.'):
                # subroutineCall
                nArgs = 0

                if(self.tokenizer.token_value() == '.'):
                    if(self.__symbolTable.is_defined(name)):
                        self.write_push_identifier(name)
                        nArgs += 1
                        # .
                        self.tokenizer.advance()
                        name = self.__symbolTable.get_type_of(
                            name)+"."+self.tokenizer.token_value()
                        self.tokenizer.advance()

                    else:
                        # .
                        self.tokenizer.advance()
                        # name
                        name += "."+self.tokenizer.token_value()
                        self.tokenizer.advance()
                else:
                    self.__vm_writer.write_push("pointer", 0)
                    name = self.__class_name+"."+name
                    nArgs += 1

                # (
                self.tokenizer.advance()
                # expressionList
                if self.tokenizer.token_value() != ')':
                    nArgs += self.compile_expression_list()
                # )
                self.__vm_writer.write_call(name, nArgs)
                self.tokenizer.advance()
                pass
            else:
                match token_type:
                    case "stringConstant":
                        self.write_push_string(name)
                        pass
                    case "integerConstant":
                        self.write_push_int(name)
                        pass
                    case 'identifier':
                        self.write_push_identifier(name)
                        pass
                    case _:
                        match name:
                            case "this":
                                self.__vm_writer.write_push("pointer", 0)
                            case "true":
                                self.write_push_int(1)
                            case _:
                                self.write_push_int(0)
                        pass

                pass
        pass

    def compile_expression_list(self):

        nArg = 0

        self.compile_expression()
        nArg += 1
        while self.tokenizer.token_value() == ',':
            # ,
            self.tokenizer.advance()
            # expression
            self.compile_expression()
            nArg += 1

        return nArg

    def write_push_string(self, s):
        self.write_push_int(len(s))
        self.__vm_writer.write_call('String.new', 1)

        for c in s:
            self.write_push_int(ord(c))
            self.__vm_writer.write_call('String.appendChar', 2)
        pass

    def write_push_int(self, n):
        self.__vm_writer.write_push('constant', n)

    def write_push_identifier(self, name):

        if self.__symbolTable.is_in_subroutine_table(name):
            self.__vm_writer.write_push(self.__symbolTable.get_kind_of(
                name), self.__symbolTable.get_index_of(name))
        elif self.__symbolTable.get_kind_of(name) == "static":
            self.__vm_writer.write_push(
                "static", self.__symbolTable.get_index_of(name))

        else:
            self.__vm_writer.write_push(
                "this", self.__symbolTable.get_index_of(name))
        pass
