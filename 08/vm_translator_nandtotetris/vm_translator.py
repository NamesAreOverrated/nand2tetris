from argparse import ArgumentError
from ast import parse
from asyncore import read
from calendar import c
from email.policy import default
from math import fabs
from operator import index
from pprint import pprint
import string
import sys
from tkinter import W
from unicodedata import name
from venv import create


def push_new_line(str):
    global translated_lines
    translated_lines += str+'\n'


def get_next_segment(str, index):
    word = ""
    for c in str[index:]:
        if c == ' ':
            index += 1
            break
        word += c
        index += 1
    word = word.rstrip()
    word = word.replace('\n', '')
    word = word.replace('\t', '')
    word = word.replace('/', '')

    return word, index


def get_file_name(str):
    name = ""
    dot_count = 0
    for c in str:
        if(c == '.'):
            dot_count += 1
    skip_count = 0
    for c in str:
        if c == '.':
            if skip_count == dot_count-1:
                break
            else:
                skip_count += 1
        name += c
    return name


def stack_pop_m():
    push_new_line("@SP")
    push_new_line("M=M-1")
    push_new_line("A=M")


def stack_push_d():
    push_new_line("@SP")
    push_new_line("M=M+1")
    push_new_line("A=M-1")
    push_new_line("M=D")


ram_map = {
    "local": "LCL",
    "argument": "ARG",
    "this": "THIS",
    "that": "THAT"
}

func_local_var_map = {

}


# ram_index_map = {
#     {"local", 300},
#     {"argument", 400},
#     {"THIS", 3000},
#     {"THAT", 3010},
#     {"temp", 5}

# }

args = sys.argv
if len(args) < 3:
    ArgumentError

merge_file_Count = len(args)-2
lines = []
program_line_counts = []
program_name_map = {

}

for i in range(0, merge_file_Count):
    f = open(args[i+1])
    lines_t = f.readlines()
    program_line_counts.append(len(lines_t))
    program_name_map[i] = get_file_name(args[i+1])
    lines.extend(lines_t)
    f.close()


translated_lines = ""

label_count = 0

return_label_count = 0


for line in lines:

    if line.rstrip() == "" or line.startswith("//"):
        continue
    elif line.startswith("function"):
        (function, index) = get_next_segment(line, 0)
        (nameStr, index) = get_next_segment(line, index)
        (localVar, index) = get_next_segment(line, index)
        localVar = int(localVar.rstrip())

        func_local_var_map[nameStr] = localVar

current_line = 0
current_program = 0
# program_name = get_file_name(args[len(args)-1])
print(len(program_line_counts))
print(program_line_counts)
program_name = ""
for line in lines:
    current_line += 1
    if current_line-1 == program_line_counts[current_program] and current_program < len(program_line_counts):
        current_program += 1
        current_line = 0
        print(program_name_map[current_program])
    program_name = program_name_map[current_program]
    if line.rstrip() == "" or line.startswith("//"):
        continue
    if line.startswith("pop") or line.startswith("push"):
        index = 0
        (action, index) = get_next_segment(line, index)
        (segment, index) = get_next_segment(line, index)
        (value, index) = get_next_segment(line, index)
        value = int(value)
        if action == "push":
            if ram_map.__contains__(segment):
                push_new_line(f"@{ram_map[segment]}")
                push_new_line("A=M")
                while value > 0:
                    push_new_line("A=A+1")
                    value -= 1
                push_new_line("D=M")
            else:
                match segment:
                    case "constant":
                        push_new_line(f"@{value}")
                        push_new_line("D=A")
                    case "static":
                        push_new_line(f"@{program_name}.{value}")
                        push_new_line("D=M")
                    case "temp":
                        push_new_line(f"@{(5+value)}")
                        push_new_line("D=M")
                    case "pointer":
                        if(value == 0):
                            push_new_line("@THIS")
                            # push_new_line(f"@{3000+value}")
                            push_new_line("D=M")
                        else:
                            push_new_line("@THAT")
                            # push_new_line(f"@{3010+value}")
                            push_new_line("D=M")
            stack_push_d()
        else:
            stack_pop_m()
            push_new_line("D=M")
            if ram_map.__contains__(segment):
                push_new_line(f"@{ram_map[segment]}")
                push_new_line("A=M")
                while value > 0:
                    push_new_line("A=A+1")
                    value -= 1

                # push_new_line(f"@{(ram_map[segment])+value}")
                # push_new_line("@"+(ram_map[segment]))
                # push_new_line("A=M")
                # while value > 0:
                #     push_new_line("A=A+1")
                #     value -= 1
                push_new_line("M=D")
            else:
                match segment:
                    case "constant":
                        push_new_line(f"@{value}")
                        push_new_line("M=D")
                    case "static":
                        push_new_line(f"@{program_name}.{value}")
                        push_new_line("M=D")
                    case "temp":
                        push_new_line(f"@{(5+value)}")
                        push_new_line("M=D")
                    case "pointer":
                        if(value == 0):
                            push_new_line("@THIS")
                            # push_new_line(f"@{3000+value}")
                            push_new_line("M=D")
                        else:
                            push_new_line("@THAT")
                            # push_new_line(f"@{3010+value}")
                            push_new_line("M=D")

    elif line.startswith("function"):

        (function, index) = get_next_segment(line, 0)
        (nameStr, index) = get_next_segment(line, index)

        push_new_line(f"({nameStr})")  # declare function start position

    elif line.startswith("call"):
        (function, index) = get_next_segment(line, 0)
        (nameStr, index) = get_next_segment(line, index)
        (arg_count, index) = get_next_segment(line, index)
        arg_count = int(arg_count.rstrip())

        # store currentStack and argStart
        push_new_line("@SP")
        push_new_line("D=M")
        push_new_line("@TEMP1")
        push_new_line("M=D")
        i = 0
        while(i < arg_count):
            push_new_line("M=M-1")
            i += 1

        # push_new_line(f"@{line_count+40+5+arg_count}")  # line_count +1
        push_new_line(f"@RETURN{return_label_count}")  # line_count +1
        push_new_line("D=A")  # line_count+2
        stack_push_d()  # line_count + 6

        push_new_line("@LCL")
        push_new_line("D=M")
        stack_push_d()  # 12

        push_new_line("@ARG")
        push_new_line("D=M")
        stack_push_d()  # 18

        push_new_line("@THIS")
        push_new_line("D=M")
        stack_push_d()  # 24

        push_new_line("@THAT")
        push_new_line("D=M")
        stack_push_d()  # 30

        # ARG pointer
        push_new_line("@TEMP1")
        push_new_line("D=M")
        push_new_line("@ARG")
        push_new_line("M=D")

        # # localVar
        push_new_line("@SP")
        push_new_line("D=M")
        push_new_line("@LCL")
        push_new_line("M=D")
        push_new_line("@SP")
        i = 0
        while(i < func_local_var_map[nameStr]):
            push_new_line("M=M+1")
            i += 1

        push_new_line("@LCL")
        push_new_line("A=M")
        i = 0
        while(i < func_local_var_map[nameStr]):
            push_new_line("M=0")
            push_new_line("A=A+1")
            i += 1
        # push_new_line("@SP")
        # i = 0
        # while(i < func_local_var_map[nameStr]):
        #     push_new_line("M=M+1")
        #     i += 1

        push_new_line(f"@{nameStr}")
        push_new_line("0;JMP")
        push_new_line(f"(RETURN{return_label_count})")
        return_label_count += 1
        continue
    elif line.startswith("return"):

        stack_pop_m()
        push_new_line("D=M")
        push_new_line("@RETURNTEMP")
        push_new_line("M=D")

        push_new_line("@ARG")
        push_new_line("D=M")
        push_new_line("@ARGTEMP")
        push_new_line("M=D")

        push_new_line("@LCL")
        push_new_line("D=M")
        push_new_line("@SP")
        push_new_line("M=D")

        stack_pop_m()
        push_new_line("D=M")
        push_new_line("@THAT")
        push_new_line("M=D")

        stack_pop_m()
        push_new_line("D=M")
        push_new_line("@THIS")
        push_new_line("M=D")

        stack_pop_m()
        push_new_line("D=M")
        push_new_line("@ARG")
        push_new_line("M=D")

        stack_pop_m()
        push_new_line("D=M")
        push_new_line("@LCL")
        push_new_line("M=D")

        stack_pop_m()
        push_new_line("D=M")
        push_new_line("@RETURNLABELTEMP")
        push_new_line("M=D")

        push_new_line("@ARGTEMP")
        push_new_line("D=M")
        push_new_line("@SP")
        push_new_line("M=D")
        push_new_line("@RETURNTEMP")
        push_new_line("D=M")
        stack_push_d()

        push_new_line("@RETURNLABELTEMP")
        push_new_line("A=M")

        push_new_line("0;JMP")

        continue
    elif line.startswith("label") or line.startswith("if-goto") or line.startswith("goto"):
        (action, index) = get_next_segment(line, 0)
        (value, index) = get_next_segment(line, index)
        value = value.rstrip()
        # label
        match action.rstrip():
            case "label":
                push_new_line(f"({value})")
            case "if-goto":
                stack_pop_m()
                push_new_line("D=M")
                push_new_line(f"@{value}")
                push_new_line("D;JNE")
            case "goto":
                push_new_line(f"@{value}")
                push_new_line("0;JMP")

    else:

        stack_pop_m()
        push_new_line("D=M")
        match line.rstrip():
            case "neg":
                push_new_line("D=-D")
                stack_push_d()
                continue
            case "not":
                push_new_line("D=!D")
                stack_push_d()
                continue

        stack_pop_m()
        match line.rstrip():
            case "add":
                push_new_line("D=D+M")
                stack_push_d()
            case "sub":
                push_new_line("D=M-D")
                stack_push_d()
            case "and":
                push_new_line("D=M&D")
                stack_push_d()
            case "or":
                push_new_line("D=M|D")
                stack_push_d()
            case "eq":
                push_new_line("D=D-M")
                push_new_line(f"@LABEL{label_count}")
                push_new_line("D;JEQ")
                push_new_line("D=0")
                push_new_line(f"@ENDLABEL{label_count}")
                push_new_line("0;JMP")
                push_new_line(f"(LABEL{label_count})")
                push_new_line("D=-1")
                push_new_line(f"(ENDLABEL{label_count})")
                stack_push_d()
                label_count += 1
            case "lt":
                push_new_line("D=D-M")
                push_new_line(f"@LABEL{label_count}")
                push_new_line("D;JGT")
                push_new_line("D=0")
                push_new_line(f"@ENDLABEL{label_count}")
                push_new_line("0;JMP")
                push_new_line(f"(LABEL{label_count})")
                push_new_line("D=-1")
                push_new_line(f"(ENDLABEL{label_count})")
                stack_push_d()
                label_count += 1
            case "gt":
                push_new_line("D=D-M")
                push_new_line(f"@LABEL{label_count}")
                push_new_line("D;JLT")
                push_new_line("D=0")
                push_new_line(f"@ENDLABEL{label_count}")
                push_new_line("0;JMP")
                push_new_line(f"(LABEL{label_count})")
                push_new_line("D=-1")
                push_new_line(f"(ENDLABEL{label_count})")
                stack_push_d()
                label_count += 1

push_new_line("(END)")
push_new_line("@END")
push_new_line("0;JMP")

f = open(args[len(args)-1], "w")
f.write(translated_lines)
f.close()
