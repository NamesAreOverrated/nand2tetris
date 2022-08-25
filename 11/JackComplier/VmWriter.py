from csv import writer


class VmWriter:

    def __init__(self, output_file_name) -> None:
        self.file_stream = open(output_file_name+".vm", "w")
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
        self.__write_line(command)

    def write_label(self, label):
        self.__write_line(f"({label.upper()})")
        pass

    def write_goto(self, label):
        self.__write_line(f"goto @{label.upper()}")

    def write_if(self, label):
        self.__write_line(f"if-goto @{label.upper()}")

    def write_call(self, name, nArgs):
        self.__write_line(f"call {name} {nArgs}")

    def write_function(self, name, nLocals):
        self.__write_line(f"function {name} {nLocals}")

    def write_return(self):
        self.__write_line("return")

    def close(self):
        self.close()
    pass


pass
