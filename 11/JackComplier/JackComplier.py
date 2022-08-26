import os
import sys
from CompilationEngine import CompilationEngine
from VmWriter import VmWriter
from Tokenizer import Tokenizer


args = sys.argv
if len(args) < 2:
    raise ValueError("not enough arguments!")

name = args[1]

files = []
files.append(args[1])

is_dir = not name.endswith(".jack")

if is_dir:
    files.clear()
    for file in os.listdir(name):
        if file.endswith(".jack"):
            files.append(os.path.join(name, file))


for file in files:
    f = open(file)
    content = f.read()
    f.close()
    vm_writer = None
    if is_dir:
        base = os.path.basename(file)
        file_name = os.path.splitext(base)[0]
        vm_writer = VmWriter(os.path.join(name, (file_name+".vm")))
    else:
        vm_writer = VmWriter(file.replace(".jack", ".vm"))

    print("start compile: "+file)

    tokenizer = Tokenizer(content)
    complier = CompilationEngine(tokenizer, vm_writer)
    complier.compile()
