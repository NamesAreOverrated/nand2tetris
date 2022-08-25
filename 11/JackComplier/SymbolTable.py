from msilib import Table
from symtable import Symbol
from typing_extensions import Self


class SymbolTable:

    class Table:
        class Symbol:
            name = ""
            type = ""
            kind = ""
            index = 0

            def __init__(self, name, type, kind, index) -> None:
                self.name = name
                self.type = type
                self.kind = kind
                self.index = index
                pass
        pass  # symbol

        __kind_dict = {
            "STATIC": 0,
            "FIELD": 0,
            "ARG": 0,
            "VAR": 0

        }
        __symbols_dict = {

        }

        def __init__(self) -> None:
            pass

        def define(self, name, type, kind):
            self.__kind_dict[kind] += 1
            index = self.__kind_dict[kind]
            self.__symbols_dict[name] = Symbol(name, type, kind, index)
            pass

        def reset(self):
            for key in self.__kind_dict.keys:
                self.__kind_dict[key] = 0
            self.__symbols_dict.clear()
            pass

        def get_var_count(self, kind):
            return self.__kind_dict[kind]

        def get_kind_of(self, name):
            return self.__symbols_dict[name].kind

        def get_type_of(self, name):
            return self.__symbols_dict[name].type

        def get_index_of(self, name):
            return self.__symbols_dict[name].index

        def is_defined(self, name):
            return self.__symbols_dict.__contains__(name)

        pass
    pass  # Table

    __class_table = Table()
    __subroutine_table = None

    def start_subroutine(self):
        if self.__subroutine_table == None:
            self.__subroutine_table = Table()
        else:
            self.__subroutine_table.reset()

    def get_var_count(self, kind):
        if not self.__subroutine_table == None:
            return self.__subroutine_table.get_var_count(kind)
        return self.__class_table.get_var_count(kind)

    def get_kind_of(self, name):
        if not self.__subroutine_table == None and self.__subroutine_table.is_defined(name):
            return self.__subroutine_table.get_kind_of(name)
        return self.__class_table.get_kind_of(name)

    def get_type_of(self, name):
        if not self.__subroutine_table == None and self.__subroutine_table.is_defined(name):
            return self.__subroutine_table.get_type_of(name)
        return self.__class_table.get_type_of(name)

    def get_index_of(self, name):
        if not self.__subroutine_table == None and self.__subroutine_table.is_defined(name):
            return self.__subroutine_table.get_index_of(name)
        return self.__class_table.get_index_of(name)
