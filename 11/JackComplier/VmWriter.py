from csv import writer


class VmWriter:

    __op_actions = {'+': 'add',
                    '-': 'sub',
                    '*': 'call Math.multiply 2',
                    '/': 'call Math.divide 2',
                    '&': 'and',
                    '|': 'or',
                    '<': 'lt',
                    '>': 'gt',
                    '=': 'eq',
                    '-': 'neg',
                    '~': 'not',
                    }

    def __init__(self, output_file_name) -> None:
        output_file_name = output_file_name if output_file_name.endswith(
            ".vm") else output_file_name+".vm"
        self.file_stream = open(output_file_name, "w")
        pass

    def __write_line(self, str):
        self.file_stream.write(str+'\n')

    def write_push(self, segment, index):
        self.__write_line(f"push {segment} {index}")
        pass

    def write_pop(self, segment, index):
        self.__write_line(f"pop {segment} {index}")
        pass

    def write_arithmetic(self, command):
        print(f"Write : {self.__op_actions[command]}")
        self.__write_line(self.__op_actions[command])

    def write_label(self, label):
        self.__write_line(f"label {label.upper()}")
        pass

    def write_goto(self, label):
        self.__write_line(f"goto {label.upper()}")

    def write_if_goto(self, label):
        self.__write_line(f"if-goto {label.upper()}")

    def write_call(self, name, nArgs):
        self.__write_line(f"call {name} {nArgs}")

    def write_function(self, name, nLocals):
        self.__write_line(f"function {name} {nLocals}")

    def write_new_line(self):
        self.__write_line("")

    def write_return(self):
        self.__write_line("return")

    def close(self):
        self.close()
    pass


pass
