import os

def include(tp, comp, path):
    return '{} <{}.scad>'.format(tp, os.path.relpath(os.path.join(*comp), path))

def process_lines(index, fn, path, lines):
    filedep = set()
    result = []
    for line in lines:
        result.extend(convert_line(filedep, line))
    return [include('include', ['colors'], path)] + \
           [include('use', find_part(index, f), path) for f in filedep] + \
           [ "module {}() {{".format(make_module_name(fn)) ] + \
           ['  {}'.format(line) for line in result] + \
           [ "}" ]

def make_module_name(filename):
    module_name = filename.lower().split('.', 1)[0]
    module_name = module_name.replace('\\', '__').replace('-', '_')
    return 'ldraw_lib__' + module_name

def main():
    library_root = os.path.join('lib', 'ldraw')
    index = index_library(library_root)
    for i in index:
        path, base = find_part(index, i)
        with open(os.path.join(library_root, path, base) + '.dat', errors='replace') as fd:
            lines = fd.readlines()
        result = process_lines(index, i, path, lines)
        os.makedirs(os.path.join('openscad', path), exist_ok=True)
        with open(os.path.join('openscad', path, base) + '.scad', 'w') as fdw:
            fdw.write('\n'.join(result))

def make_colour(colour_index):
    return "color(lego_colours[{0}])".format(colour_index)


def convert_line(filedep, part_line):
    result = [ "// {}".format(part_line.rstrip()) ]
    params = part_line.split()
    if not params:
        return result
    if params[0] in ["1", "3", "4"]:
        result.append(make_colour(params[1]))
    if params[0] == "1":
        filedep.add(params[14])
        result.append(("  multmatrix([[{3}, {4}, {5}, {0}], [{6}, {7}, {8}, {1}],"
         " [{9}, {10}, {11}, {2}], [0, 0, 0, 1]]) {12}();"
         ).format(*params[2:14],make_module_name(params[14])))
    elif params[0] == "3":
        result.append(("  polyhedron([[{0}, {1}, {2}], [{3}, {4}, {5}],"
            " [{6}, {7}, {8}]], [[2, 1, 0]]);").format(*params[2:11]))
    elif params[0] == "4":
        result.append(("  polyhedron([[{0}, {1}, {2}], [{3}, {4}, {5}],"
            " [{6}, {7}, {8}], [{9}, {10}, {11}]], [[3, 2, 1, 0]]);"
            ).format(*params[2:14]))
    return result

def index_library(library_root):
    index = {}
    for sub_path in ['parts', 'p']:
        whole_path = os.path.join(library_root, sub_path) 
        for item in os.listdir(whole_path):
            if item.endswith('.dat'):
                index[item] = [sub_path, os.path.splitext(item)[0]]
    special_subs = {
        's': os.path.join('parts', 's'),
        '48' : os.path.join('p', '48'),
        '8' : os.path.join('p', '8')
    }
    for prefix, s_path in special_subs.items():
        for item in os.listdir(os.path.join(library_root, s_path)):
            if item.endswith('.dat'):
                index[prefix + '\\'+item] = [s_path, os.path.splitext(item)[0]]
    return index

def find_part(index, part_name):
    try:
        filename = index[part_name]
    except KeyError:
        filename = index[part_name.lower()]
    return filename


if __name__ == '__main__':
    main()
