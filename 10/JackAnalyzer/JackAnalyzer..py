
import sys


class Token:
    def __init__(self, value, type) -> None:
        self.value = value.rstrip()
        self.value = value.strip()
        self.type = type
        pass

    def get_type(self):
        return self.type

    def get_value(self):
        match self.type:
            case "integerConstant":
                return int(self.value)
            case _:
                return str(self.value)
        pass

    pass


class Tokenizer:

    keyword_map = set(
        ["class",
         "constructor",
         "function",
         "method",
         "field",
         "static",
         "var",
         "int",
         "char",
         "boolean",
         "void",
         "true",
         "false",
         "null",
         "this",
         "let",
         "do",
         "if",
         "else",
         "while",
         "return"]
    )
    symbol_set = set(
        ['{',
         '}',
         '(',
         ')',
         '[',
         ']',
         ',',
         '.',
         ';',
         '+',
         '-',
         '*',
         '/',
         '&',
         '|',
         '<',
         '>',
         '=',
         '~']
    )

    def __init__(self, file) -> None:
        self.file = file
        self.current_index = 0
        self.current_token = None

        self.next_index = 0
        self.next_token = None
        self.is_peeked = False
        pass

    def has_more_tokens(self):
        current_str = ""
        is_started = False
        is_skip = False
        start_index = self.current_index
        self.next_index = self.current_index
        token = None
        is_str = False
        for c in self.file[start_index:]:
            self.next_index += 1
            if is_str:
                current_str += c
                is_started = True
                if c == '"':
                    is_str = False
                    break
                continue
            if c == '/':
                if is_started:
                    break
                if self.file[self.next_index] == '/' or (self.file[self.next_index] == '*' and self.file[self.next_index+1] == '*'):
                    is_skip = True
                    continue
            if c == '\n':
                if is_started:
                    break
                if is_skip:
                    is_skip = False
                continue

            if is_skip:
                continue

            if(c == ' ' or c == '\t'):
                if is_started:
                    break
                continue
            if c == '"':
                is_str = True

            if(self.symbol_set.__contains__(c)):
                if is_started:
                    self.next_index -= 1
                    break
                token = Token(value=c, type="symbol")
                self.is_peeked = True
                self.next_token = token
                return not (self.next_token == None)
            current_str += c
            is_started = True
            pass
        current_str = current_str.strip()
        current_str = current_str.rstrip()
        if len(current_str) == 0:
            self.next_token = None
            self.is_peeked = True
            return False
        if self.keyword_map.__contains__(current_str):
            token = Token(value=current_str, type="keyword")
        elif(current_str.startswith('"') and current_str.endswith('"')):
            token = Token(
                value=current_str[1:len(current_str)-2], type="StringConstant")

        elif current_str.isnumeric():
            token = Token(
                value=current_str, type="integerConstant")
        elif not current_str[0].isnumeric():
            token = Token(value=current_str, type="identifier")

        self.next_token = token
        self.is_peeked = True
        return not (self.next_token == None)

    def advance(self):
        if self.is_peeked:
            self.current_token = self.next_token
            self.current_index = self.next_index
        else:
            if self.has_more_tokens():
                self.current_token = self.next_token
                self.current_index = self.next_index
            else:
                self.current_token = None
        self.is_peeked = False
        pass

    def token_type(self):
        return self.current_token.get_type()

    def token_value(self):
        return self.current_token.get_value()


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
    def __init__(self, tokenizer) -> None:
        self.tokenizer = tokenizer
        pass

    def compile(self):
        return self.compile_class()

    def compile_class(self):

        output = ""
        if(self.tokenizer.has_more_tokens()):
            # class
            self.tokenizer.advance()
            output += xml_wrapper(tag=self.tokenizer.token_type(),
                                  strs=self.tokenizer.token_value(), indent=0)
            self.tokenizer.advance()
            # name
            output += xml_wrapper(tag=self.tokenizer.token_type(),
                                  strs=self.tokenizer.token_value(), indent=0)
            self.tokenizer.advance()

            # {
            output += xml_wrapper(tag=self.tokenizer.token_type(),
                                  strs=self.tokenizer.token_value(), indent=0)
            self.tokenizer.advance()
            while(self.tokenizer.has_more_tokens()):
                match self.tokenizer.token_value():
                    case "static" | "field":
                        output += xml_wrapper(tag="classVarDec",
                                              strs=self.compile_class_var_dec(indent_value=2), indent=1)
                        pass
                    case "constructor" | "function" | "method":
                        output += xml_wrapper("subroutineDec",
                                              self.compile_subroutine_dec(indent_value=2), 1)
                        pass
                    case '}':
                        output += xml_wrapper(self.tokenizer.token_type(),
                                              self.tokenizer.token_value(), 0)
                        return output

            pass

        return output

    def compile_class_var_dec(self, indent_value):
        output = ""
        print("classVarDec")
        # type
        output += xml_wrapper(self.tokenizer.token_type(),
                              self.tokenizer.token_value(), indent_value)

        self.tokenizer.advance()
        # name
        output += xml_wrapper(self.tokenizer.token_type(),
                              self.tokenizer.token_value(), indent_value)

        self.tokenizer.advance()
        while (self.tokenizer.token_value() == ','):
            # ,
            output += xml_wrapper(self.tokenizer.token_type(),
                                  self.tokenizer.token_value(), indent_value)
            self.tokenizer.advance()
            # name
            output += xml_wrapper(self.tokenizer.token_type(),
                                  self.tokenizer.token_value(), indent_value)
            self.tokenizer.advance()

        # ;
        output += xml_wrapper(self.tokenizer.token_type(),
                              self.tokenizer.token_value(), indent_value)
        self.tokenizer.advance()

        return output

    def compile_subroutine_dec(self, indent_value):
        output = ""
        print("subroutineDec")

        # method/function
        output += xml_wrapper(self.tokenizer.token_type(),
                              self.tokenizer.token_value(), indent_value)

        # void
        self.tokenizer.advance()
        output += xml_wrapper(self.tokenizer.token_type(),
                              self.tokenizer.token_value(), indent_value)

        # name
        self.tokenizer.advance()
        output += xml_wrapper(self.tokenizer.token_type(),
                              self.tokenizer.token_value(), indent_value)
        self.tokenizer.advance()

        # (
        output += xml_wrapper(self.tokenizer.token_type(),
                              self.tokenizer.token_value(), indent_value)

        self.tokenizer.advance()

        # parameterList
        output += xml_wrapper("parameterList",
                              self.compile_parameter_list(indent_value+1), indent_value)

        # )
        output += xml_wrapper(self.tokenizer.token_type(),
                              self.tokenizer.token_value(), indent_value)
        self.tokenizer.advance()

        # subroutineBody
        output += xml_wrapper("subroutineBody",
                              self.compile_subroutine_body(indent_value+1), indent_value)
        return output

    def compile_parameter_list(self, indent_value):

        output = ""
        print("parameter_list")
        if self.tokenizer.token_value() == ')':
            return output

        # type
        output += xml_wrapper(self.tokenizer.token_type(),
                              self.tokenizer.token_value(), indent_value)
        self.tokenizer.advance()
        # name
        output += xml_wrapper(self.tokenizer.token_type(),
                              self.tokenizer.token_value(), indent_value)
        self.tokenizer.advance()

        while self.tokenizer.token_value() == ',':

            # ,
            output += xml_wrapper(self.tokenizer.token_type(),
                                  self.tokenizer.token_value(), indent_value)
            self.tokenizer.advance()
            # type
            output += xml_wrapper(self.tokenizer.token_type(),
                                  self.tokenizer.token_value(), indent_value)
            self.tokenizer.advance()
            # name
            output += xml_wrapper(self.tokenizer.token_type(),
                                  self.tokenizer.token_value(), indent_value)
            self.tokenizer.advance()

        return output

    def compile_subroutine_body(self, indent_value):
        output = ""
        print("subroutine_body")
        # {
        output += xml_wrapper(self.tokenizer.token_type(),
                              self.tokenizer.token_value(), indent_value)
        self.tokenizer.advance()
        while self.tokenizer.token_value() == "var":
            output += xml_wrapper("varDec",
                                  self.compile_var_dec(indent_value+1), indent_value)
            pass

        output += xml_wrapper("statements",
                              self.compile_statements(indent_value+1), indent_value)

        # }
        output += xml_wrapper(self.tokenizer.token_type(),
                              self.tokenizer.token_value(), indent_value)
        self.tokenizer.advance()
        return output

    def compile_var_dec(self, indent_value):
        print("varDec")
        output = ""
        # var
        output += xml_wrapper(self.tokenizer.token_type(),
                              self.tokenizer.token_value(), indent_value)
        self.tokenizer.advance()
        # type
        output += xml_wrapper(self.tokenizer.token_type(),
                              self.tokenizer.token_value(), indent_value)
        self.tokenizer.advance()
        # name
        output += xml_wrapper(self.tokenizer.token_type(),
                              self.tokenizer.token_value(), indent_value)
        self.tokenizer.advance()
        while self.tokenizer.token_value() == ',':
            # ,
            output += xml_wrapper(self.tokenizer.token_type(),
                                  self.tokenizer.token_value(), indent_value)
            self.tokenizer.advance()
            # name
            output += xml_wrapper(self.tokenizer.token_type(),
                                  self.tokenizer.token_value(), indent_value)
            self.tokenizer.advance()

        # ;
        output += xml_wrapper(self.tokenizer.token_type(),
                              self.tokenizer.token_value(), indent_value)

        self.tokenizer.advance()

        return output

    def compile_statements(self, indent_value):
        print("statement")
        output = ""

        while(self.tokenizer.has_more_tokens()):

            match(self.tokenizer.token_value()):
                case "let":
                    output += xml_wrapper("letStatement",
                                          self.compile_let_statement(indent_value+1), indent_value)
                    pass
                case "if":
                    output += xml_wrapper("ifStatement",
                                          self.compile_if_statement(indent_value+1), indent_value)
                    pass
                case "while":
                    output += xml_wrapper("whileStatement",
                                          self.compile_while_statement(indent_value+1), indent_value)
                    pass
                case "do":
                    output += xml_wrapper("doStatement",
                                          self.compile_do_statement(indent_value+1), indent_value)
                    pass
                case "return":
                    output += xml_wrapper("returnStatement",
                                          self.compile_return_statement(indent_value+1), indent_value)
                    pass
                case _:
                    print("statement exit value:" +
                          self.tokenizer.token_value())

                    return output

        return output

    def compile_if_statement(self, indent_value):
        print("ifStatement")
        output = ""
        # if
        output += xml_wrapper(self.tokenizer.token_type(),
                              self.tokenizer.token_value(), indent_value)
        self.tokenizer.advance()
        # (
        output += xml_wrapper(self.tokenizer.token_type(),
                              self.tokenizer.token_value(), indent_value)
        self.tokenizer.advance()

        # expression
        output += xml_wrapper("expression",
                              self.compile_expression(indent_value=indent_value+1), indent_value)

        # )
        output += xml_wrapper(self.tokenizer.token_type(),
                              self.tokenizer.token_value(), indent_value)
        self.tokenizer.advance()
        # {
        output += xml_wrapper(self.tokenizer.token_type(),
                              self.tokenizer.token_value(), indent_value)
        self.tokenizer.advance()

        # statements
        output += xml_wrapper("statements",
                              self.compile_statements(indent_value=indent_value+1), indent_value)

        # }
        output += xml_wrapper(self.tokenizer.token_type(),
                              self.tokenizer.token_value(), indent_value)

        self.tokenizer.advance()
        if(self.tokenizer.token_value() == "else"):
            # else
            output += xml_wrapper(self.tokenizer.token_type(),
                                  self.tokenizer.token_value(), indent_value)
            self.tokenizer.advance()
            # {
            output += xml_wrapper(self.tokenizer.token_type(),
                                  self.tokenizer.token_value(), indent_value)
            self.tokenizer.advance()
            # statements
            output += xml_wrapper("statements",
                                  self.compile_statements(indent_value=indent_value+1), indent_value)
            # }
            output += xml_wrapper(self.tokenizer.token_type(),
                                  self.tokenizer.token_value(), indent_value)
            self.tokenizer.advance()

        return output

    def compile_while_statement(self, indent_value):
        print("whileStatement")
        output = ""
        # while
        output += xml_wrapper(self.tokenizer.token_type(),
                              self.tokenizer.token_value(), indent_value)
        self.tokenizer.advance()
        # (
        output += xml_wrapper(self.tokenizer.token_type(),
                              self.tokenizer.token_value(), indent_value)
        self.tokenizer.advance()
        # expression
        output += xml_wrapper("expression",
                              self.compile_expression(indent_value=indent_value+1), indent_value)
        # )
        output += xml_wrapper(self.tokenizer.token_type(),
                              self.tokenizer.token_value(), indent_value)
        self.tokenizer.advance()

        # {

        output += xml_wrapper(self.tokenizer.token_type(),
                              self.tokenizer.token_value(), indent_value)
        self.tokenizer.advance()
        # statement
        output += xml_wrapper("statements",
                              self.compile_statements(indent_value=indent_value+1), indent_value)

        # }
        output += xml_wrapper(self.tokenizer.token_type(),
                              self.tokenizer.token_value(), indent_value)
        self.tokenizer.advance()

        print("while end: " + self.tokenizer.token_value())

        return output

    def compile_do_statement(self, indent_value):
        print("doStatement")
        output = ""
        # do
        output += xml_wrapper(self.tokenizer.token_type(),
                              self.tokenizer.token_value(), indent_value)
        self.tokenizer.advance()
        # name
        output += xml_wrapper(self.tokenizer.token_type(),
                              self.tokenizer.token_value(), indent_value)
        self.tokenizer.advance()

        if(self.tokenizer.token_value() == '.'):
            output += xml_wrapper(self.tokenizer.token_type(),
                                  self.tokenizer.token_value(), indent_value)
            self.tokenizer.advance()
            # name
            output += xml_wrapper(self.tokenizer.token_type(),
                                  self.tokenizer.token_value(), indent_value)
            self.tokenizer.advance()
        # (
        output += xml_wrapper(self.tokenizer.token_type(),
                              self.tokenizer.token_value(), indent_value)
        self.tokenizer.advance()

        # expressionList
        if self.tokenizer.token_value() != ')':
            output += xml_wrapper("expressionList",
                                  self.compile_expression_list(indent_value=indent_value+1), indent_value)
        # )
        output += xml_wrapper(self.tokenizer.token_type(),
                              self.tokenizer.token_value(), indent_value)
        self.tokenizer.advance()

        # ;
        output += xml_wrapper(self.tokenizer.token_type(),
                              self.tokenizer.token_value(), indent_value)
        self.tokenizer.advance()

        return output

    def compile_return_statement(self, indent_value):
        print("returnStatement")
        output = ""
# return
        output += xml_wrapper(self.tokenizer.token_type(),
                              self.tokenizer.token_value(), indent_value)
        self.tokenizer.advance()
        # expression
        if self.tokenizer.token_value() != ';':
            output += xml_wrapper("expression",
                                  self.compile_expression(indent_value=indent_value+1), indent_value)

        # ;
        output += xml_wrapper(self.tokenizer.token_type(),
                              self.tokenizer.token_value(), indent_value)
        self.tokenizer.advance()

        return output

    def compile_let_statement(self, indent_value):
        print("letStatement")
        output = ""
        # let
        output += xml_wrapper(self.tokenizer.token_type(),
                              self.tokenizer.token_value(), indent_value)
        self.tokenizer.advance()
        # name
        output += xml_wrapper(self.tokenizer.token_type(),
                              self.tokenizer.token_value(), indent_value)
        self.tokenizer.advance()

        if self.tokenizer.token_value() == '[':
            # [
            output += xml_wrapper(self.tokenizer.token_type(),
                                  self.tokenizer.token_value(), indent_value)
            self.tokenizer.advance()
            # expression
            output += xml_wrapper("expression",
                                  self.compile_expression(indent_value=indent_value+1), indent_value)
            # ]
            output += xml_wrapper(self.tokenizer.token_type(),
                                  self.tokenizer.token_value(), indent_value)
            self.tokenizer.advance()

        # =
        output += xml_wrapper(self.tokenizer.token_type(),
                              self.tokenizer.token_value(), indent_value)
        self.tokenizer.advance()
        # expression
        output += xml_wrapper("expression",
                              self.compile_expression(indent_value=indent_value+1), indent_value)

        # ;
        output += xml_wrapper(self.tokenizer.token_type(),
                              self.tokenizer.token_value(), indent_value)
        self.tokenizer.advance()
        return output

    def compile_expression(self, indent_value):
        print("expression")
        output = ""
        output += xml_wrapper("term",
                              self.compile_term(indent_value=indent_value+1), indent_value)

        while True:
            match self.tokenizer.token_value():
                case '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=':
                    # op
                    output += xml_wrapper(self.tokenizer.token_type(),
                                          self.tokenizer.token_value(), indent_value)
                    self.tokenizer.advance()

                    output += xml_wrapper("term",
                                          self.compile_term(indent_value=indent_value+1), indent_value)
                case _:
                    return output

        return output

    def compile_term(self, indent_value):
        output = ""
        print("term")
        # expression
        if self.tokenizer.token_value() == '(':
            # (
            output += xml_wrapper(self.tokenizer.token_type(),
                                  self.tokenizer.token_value(), indent_value)
            self.tokenizer.advance()

            # expression
            output += xml_wrapper("expression",
                                  self.compile_expression(indent_value=indent_value+1), indent_value)

            # )
            output += xml_wrapper(self.tokenizer.token_type(),
                                  self.tokenizer.token_value(), indent_value)
            self.tokenizer.advance()
            pass
        # unaryOP term
        elif (self.tokenizer.token_value() == '~') or (self.tokenizer.token_value() == '-'):
            output += xml_wrapper(self.tokenizer.token_type(),
                                  self.tokenizer.token_value(), indent_value)
            self.tokenizer.advance()
            output += xml_wrapper("term",
                                  self.compile_term(indent_value=indent_value+1), indent_value)

            pass
        else:
            # name
            output += xml_wrapper(self.tokenizer.token_type(),
                                  self.tokenizer.token_value(), indent_value)
            self.tokenizer.advance()

            # varName[expressionList]
            if self.tokenizer.token_value() == '[':
                # [
                output += xml_wrapper(self.tokenizer.token_type(),
                                      self.tokenizer.token_value(), indent_value)
                self.tokenizer.advance()
                # expression
                output += xml_wrapper("expression",
                                      self.compile_expression(indent_value=indent_value+1), indent_value)

                # ]
                output += xml_wrapper(self.tokenizer.token_type(),
                                      self.tokenizer.token_value(), indent_value)
                self.tokenizer.advance()
            elif (self.tokenizer.token_value() == '(') or (self.tokenizer.token_value() == '.'):
                # subroutineCall

                if(self.tokenizer.token_value() == '.'):
                    output += xml_wrapper(self.tokenizer.token_type(),
                                          self.tokenizer.token_value(), indent_value)
                    self.tokenizer.advance()
                    # name
                    output += xml_wrapper(self.tokenizer.token_type(),
                                          self.tokenizer.token_value(), indent_value)
                    self.tokenizer.advance()

                # (
                output += xml_wrapper(self.tokenizer.token_type(),
                                      self.tokenizer.token_value(), indent_value)
                self.tokenizer.advance()
                # expressionList

                if self.tokenizer.token_value() != ')':
                    output += xml_wrapper("expressionList",
                                          self.compile_expression_list(indent_value=indent_value+1), indent_value)
                # )
                output += xml_wrapper(self.tokenizer.token_type(),
                                      self.tokenizer.token_value(), indent_value)
                self.tokenizer.advance()
                pass

        return output

    def compile_expression_list(self, indent_value):

        print("expressionList")
        output = ""

        output += xml_wrapper("expression",
                              self.compile_expression(indent_value=indent_value+1), indent_value)
        while self.tokenizer.token_value() == ',':
            # ,
            output += xml_wrapper(self.tokenizer.token_type(),
                                  self.tokenizer.token_value(), indent_value)
            self.tokenizer.advance()
            # expression
            output += xml_wrapper("expression",
                                  self.compile_expression(indent_value=indent_value+1), indent_value)

        return output
        pass

    pass


args = sys.argv
if len(args) < 2:
    raise ValueError('not enough arguments')
f = open(args[1])
tokenizer = Tokenizer(file=f.read())
f.close()

c = CompilationEngine(tokenizer)


f = open(args[2], "w")
f.write(c.compile())
f.close()


# while tokenizer.has_more_tokens():
#     tokenizer.advance()
#     print(f"{tokenizer.current_token.get_type()} : {tokenizer.current_token.get_value()}")
