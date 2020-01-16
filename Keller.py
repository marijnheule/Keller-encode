import sys
import os
import re
import math
import itertools
import subprocess

import igraph

table = {}

def convert(w, i, c, n, s):
    assert(w >= 0 and w < (2**n))
    assert(i >= 0 and i < n)
    assert(c >= 0 and c < s)
    return s*n*w + s*i + c + 1

def matrix_graph(assignment, s):
    nrows = 3
    ncols = 3
    nsymbols = s + 1
    m = igraph.Graph(nrows + ncols + nrows * ncols + nsymbols)
    colors = [0] * nrows + [1] * ncols + [2] * (nrows * ncols) + [3 + i for i in range(0, nsymbols)]
    expanded = list(assignment)

    for r in range(0, nrows):
        expanded.insert(r * ncols + r, s)

    assert(len(expanded) == nrows * ncols)

    for r in range(0, nrows):
        for c in range(0, ncols):
            m.add_edge(nrows + ncols + r * ncols + c, r)
            m.add_edge(nrows + ncols + r * ncols + c, nrows + c)
            m.add_edge(nrows + ncols + r * ncols + c, nrows + ncols + nrows * ncols + expanded[r * ncols + c])

    return m, colors

def level2_graph(assignment, s):
    g = igraph.Graph(s + len(assignment))

    for i in range(0, len(assignment) // 2):
        g.add_edge(s + 2 * i, assignment[2 * i])
        g.add_edge(s + 2 * i + 1, assignment[2 * i + 1])

    for i in range(0, (len(assignment) // 2) - 1):
        g.add_edge(s + 2 * i, s + 2 * (i + 1))
        g.add_edge(s + 2 * i + 1, s + 2 * (i + 1) + 1)

    return g

def assignment2vars(a, ws, n, s):
    result = []

    for i in range(0, len(a)):
        for c in range(0, s):
            if c == a[i]:
                result.append(convert(ws[i][0], ws[i][1], c, n, s))
            else:
                result.append(-convert(ws[i][0], ws[i][1], c, n, s))

    return result

def parse_clause_line(l):
    ints = list(map(int, l.strip().split()))

    assert(ints[-1] == 0)
    del ints[-1]

    return ints

def write_cnf(clauses, outf, nvars):
    print("p cnf %d %d" % (nvars, len(clauses)), file=outf)

    for l in clauses:
        outf.write(l)

    outf.flush()

def output_ippr(assignment, canonical, variables, s, outf):
    assert(len(assignment) == len(canonical))

    for diff in range(0, len(assignment)):
        if canonical[diff] != assignment[diff]:
            break

    assert(diff < len(assignment))
    clause = assignment2vars(assignment, variables, n, s)
    cube = assignment2vars(canonical, variables, n, s)

    for i in range(0, s):
        if clause[s * diff + i] == -cube[s * diff + i]:
            firstlit = cube[s * diff + i]

            break

    del cube[s * diff + i]
    del clause[s * diff + i]

    print("%d %s %d %s 0" % (firstlit, " ".join([str(-v) for v in clause]), firstlit, " ".join([str(v) for v in cube])), file=outf)

def print_assignments(dnf, i1, i2, j, trails, outf):
    if j >= len(dnf[i1]):
        outf.write("a ")

        for t in trails:
            if len(t) > 0:
                outf.write(" ".join([str(l) for l in t]))
                outf.write(" ")

        outf.write("0\n")

        return

    trail = [dnf[i1][j]]

    for i in range(i1, i2):
        if dnf[i][j] not in trail:
            print_assignments(dnf, i1, i, j + 1, trails + [trail], outf)

            i1 = i
            trail[-1] = -trail[-1]

            trail.append(dnf[i][j])

    del trail[-1]
    print_assignments(dnf, i1, i2, j + 1, trails + [trail], outf)

if __name__ == "__main__":
    s = int(sys.argv[1])
    values = list(range(0, s))
    output = """
7 %d
3
0 0 0 0 0 0 0
%d 1 0 0 0 0 0
%d %d -1 -1 1 1 1
""" % (s, s, s, s + 1)
    basename = sys.argv[2]
    cnffilename = "%s.cnf" % basename
    seen = []
    level1classes = {}
    ncnfs = 1
    n = 7
    level1vars = [(3 + 2 ** (n - 3), 5), (3 + 2 ** (n - 3), 6),
                  (3 + 2 ** (n - 2), 4), (3 + 2 ** (n - 2), 6),
                  (3 + 2 ** (n - 1), 4), (3 + 2 ** (n - 1), 5)]
    level2vars = [(3, 2), (3, 3),
                  (3 + 2 ** (n - 3), 2), (3 + 2 ** (n - 3), 3),
                  (3 + 2 ** (n - 2), 2), (3 + 2 ** (n - 2), 3),
                  (3 + 2 ** (n - 1), 2), (3 + 2 ** (n - 1), 3)]
    dnf = []

    for i in range(0, 2 ** n):
        for j in range(0, n):
            for k in range(0, s):
                v = convert(i, j, k, n, s)
                table[v] = (i, j, k)

    with open(cnffilename, 'w') as cnffile:
        with subprocess.Popen([sys.argv[3], "7", str(s)], stdin=subprocess.PIPE, stdout=cnffile, stderr=subprocess.DEVNULL, universal_newlines=True) as cnfgen6:
            print(output, file=cnfgen6.stdin)
            cnfgen6.stdin.close()

    for assignment in itertools.product(*[values] * len(level1vars)):
        assert(len(level1vars) == 6)
        if ((assignment[0] != 1) and (assignment[2] != 1)) or ((assignment[3] != 1) and (assignment[5] != 1)) or ((assignment[4] != 1) and (assignment[1] != 1)):
            continue

        m, mcolor = matrix_graph(assignment, s)
        repeated = False

        for mm, ncolor, nass in seen:
            if mm.isomorphic_vf2(m, color1=ncolor, color2=mcolor):
                repeated = True
                level1classes[nass].append(assignment)

                break

        if not repeated:
            seen.append((m, mcolor, assignment))
            level1classes[assignment] = []

    assert(sum([len(x) for x in level1classes.values()]) + len(level1classes) == pow(2 * s - 1, 3))

    seen = {}
    gcolor = [0] + [1] * (len(values) - 1)

    for l in range(0, len(level2vars) // 2):
        gcolor += [2 + l] * 2

    for assignment in itertools.product(*[values] * len(level2vars)):
        repeated = False
        g = level2_graph(assignment, s)

        for cls in seen:
            if g.isomorphic_vf2(cls[0], color1=gcolor, color2=gcolor):
                seen[cls].append(assignment)
                repeated = True

                break

        if not repeated:
            seen[(g, assignment)] = []

    fmtstr = "%s.%0" + str(int(math.ceil(math.log10(len(seen))))) + "d.%s"
    nvars = None
    currentclauses = []

    with open(cnffilename, 'r') as origcnf:
        m = re.match("p cnf (\d+) \d+", origcnf.readline().strip())
        nvars = int(m.group(1))

        for l in origcnf:
            currentclauses.append(l)

    with open("%s.drat" % basename, 'w') as level1drat:
        with subprocess.Popen([sys.argv[4], cnffilename], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL, universal_newlines=True) as pprsearch:
            with subprocess.Popen([sys.argv[5], cnffilename, "-"], stdin=pprsearch.stdout, stdout=level1drat, universal_newlines=True) as ppr2drat:
                # These clauses are RAT so we can output them straight up
                for e in [((19, 5), (35, 4)), ((35, 6), (67, 5)), ((67, 4), (19, 6))]:
                    print("%s 0" % " ".join([str(convert(i[0], i[1], 1, n, s)) for i in e]), file=pprsearch.stdin)
                    currentclauses.append("%s 0\n" % " ".join([str(convert(i[0], i[1], 1, n, s)) for i in e]))

                for cls1 in level1classes:
                    for a1 in level1classes[cls1]:
                        output_ippr(a1, cls1, level1vars, s, pprsearch.stdin)
                        currentclauses.append("%s 0\n" % " ".join([str(-v) for v in assignment2vars(a1, level1vars, n, s)]))

                pprsearch.stdin.close()

    for cls2 in seen:
        if len(seen[cls2]) > 0:
            with open(fmtstr % (basename, ncnfs, "cnf"), 'w') as currentcnf:
                write_cnf(currentclauses, currentcnf, nvars)

                with open(fmtstr % (basename, ncnfs, "drat"), 'w') as level2drat:
                    with subprocess.Popen([sys.argv[4], currentcnf.name], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL, universal_newlines=True) as pprsearch:
                        with subprocess.Popen([sys.argv[5], currentcnf.name, "-"], stdin=pprsearch.stdout, stdout=level2drat, universal_newlines=True) as ppr2drat:
                            for a2 in seen[cls2]:
                                output_ippr(a2, cls2[1], level2vars, s, pprsearch.stdin)
                                currentclauses.append("%s 0\n" % " ".join([str(-v) for v in assignment2vars(a2, level2vars, n, s)]))

                            pprsearch.stdin.close()

            ncnfs += 1

    for cls1 in level1classes:
        cls1vars = [convert(level1vars[i][0], level1vars[i][1], cls1[i], n, s) for i in range(0, len(cls1))]

        for cls2 in seen:
            cls2vars = [convert(level2vars[i][0], level2vars[i][1], cls2[1][i], n, s) for i in range(0, len(cls2[1]))]

            dnf.append(cls1vars + cls2vars)

    print_assignments(sorted(dnf), 0, len(dnf), 0, [], sys.stderr)
