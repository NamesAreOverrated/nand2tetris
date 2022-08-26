from operator import truediv


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
        is_skip_newline_stop = False
        start_index = self.current_index
        self.next_index = self.current_index
        token = None
        is_str = False
        skip_count = 0
        for c in self.file[start_index:]:
            self.next_index += 1
            if skip_count > 0:
                skip_count -= 1
                continue
            if is_str:
                current_str += c
                is_started = True
                if c == '"':
                    is_str = False
                    break
                continue
            if c == '/' and not is_skip:
                if is_started:
                    break
                if self.file[self.next_index] == '/':
                    is_skip_newline_stop = True
                    is_skip = True
                    skip_count = 1
                    continue
                elif (self.file[self.next_index] == '*' and self.file[self.next_index+1] == '*'):
                    is_skip_newline_stop = False
                    is_skip = True
                    skip_count = 2
                    continue

            if c == '\n':
                if is_started:
                    break
                if is_skip and is_skip_newline_stop:
                    is_skip = False
                continue

            if is_skip and not is_skip_newline_stop and c == '*':
                if self.file[self.next_index] == '/':

                    is_skip = False
                    skip_count = 1
                    continue
                else:
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
                value=current_str[1:len(current_str)-2], type="stringConstant")

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
