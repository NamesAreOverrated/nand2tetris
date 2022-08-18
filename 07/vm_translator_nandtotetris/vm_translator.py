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
from venv import create


def push_new_line(str):
    global translated_lines
    global line_count
    translated_lines += str+'\n'
    line_count += 1


def get_next_segment(str, index):
    word = ""
    for c in str[index:]:
        if c == ' ':
            index += 1
            break
        word += c
        index += 1

    return word, index


def get_file_name(str):
    name = ""
    for c in str:
        if c == ".":
            break
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
    "local": 1,
    "argument": 2,
    "this": 3,
    "that": 4
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

f = open(args[1])
lines = f.readlines()
f.close()


translated_lines = ""
line_count = 0

label_count = 0

program_name = get_file_name(args[1])
for line in lines:
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

    else:
        stack_pop_m()
        push_new_line("D=M")
        match line.rstrip():
            case "neg":
                push_new_line("D=!D")
                stack_push_d()
                continue
            case "not":
                push_new_line("D=-D")
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

f = open(args[2], "w")
f.write(translated_lines)
f.close()
