""" compile LDraw library to OpenSCAD """

import os
import time


def readfile(index, library_root, i):
    """ Read LDraw file from library """
    path, base = find_part(index, i)
    with open(os.path.join(library_root, path, base) + '.dat',
              encoding="utf-8", errors='replace') as file:
        lines = file.readlines()
    payload = []
    for line in lines:
        params = line.split()
        if not params:
            continue
        if ((params[0] == "0" and len(params) >= 2 and params[1] == "BFC" or
             params[0] in ["1", "3", "4"])):
            payload.append(params)
    return payload


def main():
    """ The main entry point """
    library_root = os.path.join('lib', 'ldraw')
    index = index_library(library_root)
    os.makedirs(os.path.join('openscad'), exist_ok=True)
    indexlength = len(index)
    step = 0
    starttime = time.time()
    for indexpos, i in enumerate(index):
        if step == 0:
            cache = {}
            step = 1000
        step -= 1
        path, base = find_part(index, i)
        if path == 'parts':
            eta = round((time.time()-starttime)/indexpos*indexlength/60) \
                    if indexpos else '?'
            print(f'Compiling {base} ({indexpos+1}/{indexlength} - '
                  f'ETA: {eta} min)...')
            data = compilefile(index, cache, library_root, i)
            trans = [[[pnt[0]*2/5, pnt[2]*2/5, -pnt[1]*2/5]
                      for pnt in data[0]], data[1]]
            formated = ('function ldraw_{}() =\n  [{}];\n'.
                        format(i.lower().split('.', 1)[0].
                               replace('\\', '__').replace('-', '_'),
                               formatpoly(dedup(stringify(trans)),
                                          indent=3)))
            with open(os.path.join('openscad', base) + '.scad', 'w',
                      encoding='utf-8') as fdw:
                fdw.write(formated)


def index_library(library_root):
    """ Scan LDraw library for files to compile """
    index = {}
    for sub_path in ['parts', 'p']:
        whole_path = os.path.join(library_root, sub_path)
        for item in os.listdir(whole_path):
            if item.endswith('.dat'):
                index[item] = [sub_path, os.path.splitext(item)[0]]
    special_subs = {
        's': os.path.join('parts', 's'),
        '48': os.path.join('p', '48'),
        '8': os.path.join('p', '8')
    }
    for prefix, s_path in special_subs.items():
        for item in os.listdir(os.path.join(library_root, s_path)):
            if item.endswith('.dat'):
                index[prefix + '\\'+item] = [s_path, os.path.splitext(item)[0]]
    return index


def find_part(index, part_name):
    """ Find the path and file name for module """
    filename = index[part_name.lower()]
    return filename


def compilefile(index, cache, library_root, part_name):
    """ Compile LDraw file """
    key = part_name.lower()
    if key in cache:
        return cache[key]
    payload = readfile(index, library_root, part_name)
    for i in payload:
        if i[0] == '1':
            compilefile(index, cache, library_root, i[14])
    points = []
    faces = []
    cw = False
    invertnext = False
    for i in payload:
        offset = len(points)
        if i[0] == '0':
            invertnext = False
            if len(i) >= 2 and i[1] == 'BFC':
                for bfc in i[2:]:
                    if bfc == 'INVERTNEXT':
                        invertnext = True
                    elif bfc == 'CCW':
                        cw = False
                    elif bfc == 'CW':
                        cw = True
        elif i[0] == '1':
            cdata = compilefile(index, cache, library_root, i[14])
            mat = [float(j) for j in i[2:14]]
            for j in cdata[0]:
                points += [[mat[3]*j[0] + mat[4]*j[1] + mat[5]*j[2] + mat[0],
                            mat[6]*j[0] + mat[7]*j[1] + mat[8]*j[2] + mat[1],
                            mat[9]*j[0] + mat[10]*j[1] + mat[11]*j[2]+mat[2]]]
            for j in cdata[1]:
                face = [x+offset for x in j]
                faces += [face if ((
                    + mat[3]*mat[7]*mat[11]
                    + mat[4]*mat[8]*mat[9]
                    + mat[5]*mat[6]*mat[10]
                    - mat[5]*mat[7]*mat[9]
                    - mat[4]*mat[6]*mat[11]
                    - mat[3]*mat[8]*mat[10]) > 0) != invertnext
                    else list(reversed(face))]
            invertnext = False
        elif i[0] == '3':
            points += [[float(x) for x in i[2:5]],
                       [float(x) for x in i[5:8]],
                       [float(x) for x in i[8:11]]]
            if cw:
                faces += [list(range(offset, offset+3))]
            else:
                faces += [list(reversed(range(offset, offset+3)))]
            invertnext = False
        elif i[0] == '4':
            points += [[float(x) for x in i[2:5]],
                       [float(x) for x in i[5:8]],
                       [float(x) for x in i[8:11]],
                       [float(x) for x in i[11:14]]]
            if cw:
                faces += [list(range(offset, offset+4))]
            else:
                faces += [list(reversed(range(offset, offset+4)))]
            invertnext = False
    cache[key] = [points, faces]
    return cache[key]


def stringify(poly):
    """ Convert points to strings """
    return [[f'[{p[0]:f}, {p[1]:f}, {p[2]:f}]' for p in poly[0]], poly[1]]


def dedup(poly):
    """ Duplicate point elimination """
    points = []
    pos = []
    for pnt in poly[0]:
        found = False
        for cnt, ref in enumerate(points):
            if pnt == ref:
                pos.append(cnt)
                found = True
                break
        if not found:
            pos.append(len(points))
            points.append(pnt)
    return [points, [[pos[p] for p in face] for face in poly[1]]]


def formatpoly(poly, indent=0):
    """ Format a polyhedron data structure """
    return (
        '[' +
        (',\n '+' '*indent).join(poly[0]) +
        '],\n'+' '*indent+'[' +
        (',\n '+' '*indent).join(['['+', '.join([str(r) for r in f])+']'
                                  for f in poly[1]]) +
        ']')


if __name__ == '__main__':
    main()
