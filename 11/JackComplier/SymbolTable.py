
class _Symbol:

    def __init__(self, name, type, kind, index) -> None:
        self.name = name
        self.type = type
        self.kind = kind
        self.index = index
        pass
    pass  # symbol


class _Table:

    def __init__(self) -> None:
        self.__symbols_dict = {}
        self.__kind_dict = {
            "static": 0,
            "local": 0,
            "argument": 0,
            "field": 0
        }
        pass

    def define(self, name, type, kind):
        index = self.__kind_dict[kind]
        self.__kind_dict[kind] += 1
        self.__symbols_dict[name] = _Symbol(name, type, kind, index)
        pass

    def reset(self):
        for key in self.__kind_dict.keys():
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
        return name in self.__symbols_dict

    def print_table(self):
        for s in self.__symbols_dict:
            print("table: "+s)
    pass  # Table


class SymbolTable:

    def __init__(self) -> None:
        self.__class_table = _Table()
        self.__subroutine_table = None
        pass

    def define(self, name, type, kind):
        if not self.__subroutine_table == None:
            self.__subroutine_table.define(name, type, kind)

            print(f"sub define {name} | {type} {kind}")
            return
        self.__class_table.define(name, type, kind)
        print(f"class define {name} | {type} {kind}")
        pass

    def start_subroutine(self):
        if self.__subroutine_table == None:
            self.__subroutine_table = _Table()
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

    def is_in_subroutine_table(self, name):
        if self.__subroutine_table == None or not self.__subroutine_table.is_defined(name):
            return False
        return True

    def is_in_class_table(self, name):
        return self.__class_table.is_defined(name)

    def print_tables(self):
        print("class table")
        self.__class_table.print_table()
        if not self.__subroutine_table == None:
            print("subroutine table")
            self.__subroutine_table.print_table()
