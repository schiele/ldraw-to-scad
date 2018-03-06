import os
import argparse
import queue

class Module():
    def __init__(self, filename):
        self.filename = filename
        self.lines = []
        self.module_name = None
        # Name of module only
        self.dependancies = set()

    @staticmethod
    def make_module_name(filename):
        module_name = filename.split('.', 1)[0]
        module_name = module_name.replace('s\\', 's__').replace('-', '_')
        return 'n__' + module_name

    def get_module_name(self):
        if not self.module_name:
            self.module_name = self.make_module_name(self.filename)
        return self.module_name

    def add_lines(self, lines):
        self.lines = lines

    def get_lines(self):
        if self.filename == '__main__':
            return self.lines
        else:
            return self.get_module_code()

    def get_module_code(self):
        func_lines = ['  {}'.format(line) 
            for line in self.lines]

        return [
            "module {}() {{".format(self.get_module_name())
        ] + func_lines + [
            "}"
        ]


class LDrawModuleConverter:
    def __init__(self):
        # Ref name: module class
        self.modules = {}
        # Ref - queue of names only
        self.modules_queue = queue.Queue()
        # Path search
        self.index = {}

    def process_lines(self, module, lines, indent=0):
        result = []
        [result.extend(self.convert_line(module, line, indent=indent)) for line in lines]
        module.add_lines(result)

    def process_main(self, input_lines):
        main_module = Module('__main__')
        self.modules[main_module.get_module_name()] = main_module
        self.modules_queue.put(main_module)
        self.process_lines(main_module, input_lines)
        print("Main module lines is", len(main_module.lines))
        completed = []
        while not self.modules_queue.empty():
            # Get the next queued module
            current_module = self.modules_queue.get()
            # Has it been done?
            if current_module.get_module_name() in completed:
                continue
            # Have we loaded it?
            if not current_module.lines:
                print("Main module lines is", len(main_module.lines))
                with open(current_module.filename) as fd:
                    lines = fd.readlines()
                self.process_lines(current_module, lines)
            # Check - have we covered it dependancies
            new_dependancy = False
            for dep in current_module.dependancies:
                if dep not in completed:
                    self.modules_queue.put(self.modules[dep])
                    self.modules_queue.put(current_module)
                    new_dependancy = True
            if not new_dependancy:
                # Ok - ready to go - add to completed
                completed.append(current_module.get_module_name())
        # Now we can create output lines - starting at the top
        # of completed modules.
        output_lines = []
        [output_lines.extend(self.modules[module_name].get_lines())
            for module_name in completed]
        return output_lines

    def make_colour(self, colour_index):
        return "color(lego_colours[{0}])".format(colour_index)

    def handle_type_1_line(self, module, colour_index, x, y, z, a, b, c, d, e, f, g, h, i, filename):
        module_name = Module.make_module_name(filename)
        # Is this a new module?
        if module_name not in self.modules:
            # Create it
            self.modules[module_name] = Module(filename)
        # Add to deps
        module.dependancies.add(module_name)
        
        return [
            self.make_colour(colour_index),
            "  multmatrix([",
            "    [{0}, {1}, {2}, {3}],".format(a, b, c, x),
            "    [{0}, {1}, {2}, {3}],".format(d, e, f, y),
            "    [{0}, {1}, {2}, {3}],".format(g, h, i, z),
            "    [{0}, {1}, {2}, {3}]".format(0, 0, 0, 1),
            "  ])",
            "  {}();".format(module_name)
        ]

    def convert_line(self, module, part_line, indent=0):
        # Preserve blank lines
        part_line = part_line.strip()
        if part_line == '':
            return [part_line]
        try:
            command, rest = part_line.split(maxsplit=1)
        except ValueError:
            command = part_line
            rest = ''
        result = []
        if command == "0":
            result.append("// {}".format(rest))
        elif command == "1":
            try:
                result.extend(self.handle_type_1_line(module, *rest.split()))
            except TypeError:
                raise TypeError("Insufficient arguments in type 1 line", rest)
        elif command == "3":
            colour_index, x1, y1, z1, x2, y2, z2, x3, y3, z3 = rest.split()
            result.append(self.make_colour(colour_index))
            result.append("  polyhedron(points=[")
            result.append("    [{0}, {1}, {2}],".format(x1, y1, z1))
            result.append("    [{0}, {1}, {2}],".format(x2, y2, z2))
            result.append("    [{0}, {1}, {2}]".format(x3, y3, z3))
            result.append("  ], faces = [[0, 1, 2]]);")
        elif command == "4":
            colour_index, x1, y1, z1, x2, y2, z2, x3, y3, z3, x4, y4, z4 = rest.split()
            result.append(self.make_colour(colour_index))
            result.append("  polyhedron(points=[")
            result.append("    [{0}, {1}, {2}],".format(x1, y1, z1))
            result.append("    [{0}, {1}, {2}],".format(x2, y2, z2))
            result.append("    [{0}, {1}, {2}],".format(x3, y3, z3))
            result.append("    [{0}, {1}, {2}]".format(x4, y4, z4))
            result.append("  ], faces = [[0, 1, 2, 3]]);")
        if indent:
            indent_str = ''.join(' ' * indent)
            result = ['{i}{l}'.format(i=indent_str, l=line) for line in result]
        return result

    def index_library(self):
        self.index = {}
        paths = ['.']
        for item in os.listdir('.'):
            if item.endswith('.dat'):
                self.index[item] = item

        library_root = os.path.join('lib', 'ldraw')
        for sub_path in ['parts', 'p']:
            whole_path = os.path.join(library_root, sub_path) 
            for item in os.listdir(whole_path):
                if item.endswith('.dat'):
                    self.index[item] = os.path.join(whole_path, item)
        s_path = os.path.join(library_root, 'parts', 's') 
        for item in os.listdir(s_path):
            if item.endswith('.dat'):
                self.index['s\\'+item] = os.path.join(s_path, item)

    def find_part(self, part_name):
        if not self.index:
            self.index_library()
        return self.index[part_name]


class LDrawConverter():
    def __init__(self):
        self.modules = queue.Queue()
        self.index = {}

    def make_colour(self, colour_index):
        return "color(lego_colours[{0}])".format(colour_index)

    def get_modules(self):
        result = []
        for module in self.modules.values():
            result.extend(module)
        return result

    def get_module_name(self, filename):
        module_name = filename.split('.', 1)[0]
        module_name = module_name.replace('s\\', 's__').replace('-', '_')
        module_name = 'n__' + module_name
        return module_name

    def handle_type_1_line(self, colour_index, x, y, z, a, b, c, d, e, f, g, h, i, filename):
        module_name = self.get_module_name(filename)

        if filename not in self.modules:
            path = self.find_part(filename.lower())
            with open(path) as fd:
                module_inner = self.convert_file(fd, indent=2)
            self.modules[filename] = [
                "module {}() {{".format(module_name)
            ] + module_inner + [
                "}"
            ]

        return [
            self.make_colour(colour_index),
            "  multmatrix([",
            "    [{0}, {1}, {2}, {3}],".format(a, b, c, x),
            "    [{0}, {1}, {2}, {3}],".format(d, e, f, y),
            "    [{0}, {1}, {2}, {3}],".format(g, h, i, z),
            "    [{0}, {1}, {2}, {3}]".format(0, 0, 0, 1),
            "  ])",
            "  {}();".format(module_name)
        ]

    def convert_line(self, part_line, indent=0):
        # Preserve blank lines
        part_line = part_line.strip()
        if part_line == '':
            return [part_line]
        try:
            command, rest = part_line.split(maxsplit=1)
        except ValueError:
            command = part_line
            rest = ''
        result = []
        if command == "0":
            result.append("// {}".format(rest))
        elif command == "1":
            result.extend(self.handle_type_1_line(*rest.split()))
        elif command == "3":
            colour_index, x1, y1, z1, x2, y2, z2, x3, y3, z3 = rest.split()
            result.append(self.make_colour(colour_index))
            result.append("  polyhedron(points=[")
            result.append("    [{0}, {1}, {2}],".format(x1, y1, z1))
            result.append("    [{0}, {1}, {2}],".format(x2, y2, z2))
            result.append("    [{0}, {1}, {2}]".format(x3, y3, z3))
            result.append("  ], faces = [[0, 1, 2]]);")
        elif command == "4":
            colour_index, x1, y1, z1, x2, y2, z2, x3, y3, z3, x4, y4, z4 = rest.split()
            result.append(self.make_colour(colour_index))
            result.append("  polyhedron(points=[")
            result.append("    [{0}, {1}, {2}],".format(x1, y1, z1))
            result.append("    [{0}, {1}, {2}],".format(x2, y2, z2))
            result.append("    [{0}, {1}, {2}],".format(x3, y3, z3))
            result.append("    [{0}, {1}, {2}]".format(x4, y4, z4))
            result.append("  ], faces = [[0, 1, 2, 3]]);")
        if indent:
            indent_str = ''.join(' ' * indent)
            result = ['{i}{l}'.format(i=indent_str, l=line) for line in result]
        return result

    def convert_lines(self, lines, indent=0):
        result = []
        [result.extend(self.convert_line(line, indent=indent)) for line in lines]
        return result

    def convert_file(self, fd, indent=0):
        return self.convert_lines(fd.readlines(), indent=indent)


def main():
    parser = argparse.ArgumentParser(description='Convert an LDraw part to OpenSCAD')
    parser.add_argument('ldraw_file', metavar='FILENAME')
    parser.add_argument('output_file', metavar='OUTPUT_FILENAME')
    args = parser.parse_args()
    convert = LDrawConverter()
    with open(args.ldraw_file) as fd:
        result = convert.convert_file(fd)
    with open(args.output_file, 'w') as fdw:
        fdw.write('\n'.join(convert.get_modules()))
        fdw.write('\n'.join(result))



if __name__ == '__main__':
    main()