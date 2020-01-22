import sys
import os
import re
import math
import itertools
import subprocess
import collections

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
    m = igraph.Graph(nrows + ncols + nrows * ncols + ncols * (s - 2) + 3)
    colors = [0] * nrows + [1] * ncols + [2] * (nrows * ncols) + [3] * (ncols * (s - 2))
    expanded = list(assignment)

    colors.append(3 + ncols) # 0
    colors.append(4 + ncols) # 1
    colors.append(5 + ncols) # s + 1

    for r in range(0, nrows):
        expanded.insert(r * ncols + r, s + 1)

    assert(len(expanded) == nrows * ncols)

    for c in range(0, ncols):
        for i in range(0, s - 2):
            for j in range(i + 1, s - 2):
                m.add_edge(nrows + ncols + nrows * ncols + c * (s -2) + i, nrows + ncols + nrows * ncols + c * (s -2) + j)

    for r in range(0, nrows):
        for c in range(0, ncols):
            v = expanded[r * ncols + c]

            m.add_edge(nrows + ncols + r * ncols + c, r)
            m.add_edge(nrows + ncols + r * ncols + c, nrows + c)

            if v in [0, 1]:
                m.add_edge(nrows + ncols + r * ncols + c, nrows + ncols + nrows * ncols + ncols * (s - 2) + v)
            elif v == s + 1:
                m.add_edge(nrows + ncols + r * ncols + c, nrows + ncols + nrows * ncols + ncols * (s - 2) + 2)
            else:
                m.add_edge(nrows + ncols + r * ncols + c, nrows + ncols + nrows * ncols + c * (s - 2) + (v - 2))

    return m, colors

def level2_graph(assignment, s):
    g = igraph.Graph(2 * s - 1 + len(assignment))

    for i in range(0, len(assignment) // 2):
        g.add_edge(2 * s + 2 * i - 1, assignment[2 * i])
        g.add_edge(2 * s + 2 * i, s + assignment[2 * i + 1] - 1 if assignment[2 * i + 1] > 0 else 0)

    for i in range(0, (len(assignment) // 2) - 1):
        g.add_edge(2 * s + 2 * i - 1, 2 * s + 2 * (i + 1) - 1)
        g.add_edge(2 * s + 2 * i, 2 * s + 2 * (i + 1))

    return g

def shift_right_families(values, k):
    alltuples = set()
    families = {}

    for a in itertools.product(*[values] * k):
        if a not in alltuples:
            d = collections.deque(a)
            localclass = set()

            for i in range(0, len(a)):
                d.rotate()
                localclass.add(tuple(d))
                alltuples.add(tuple(d))

            localclass.remove(a)
            families[a] = list(localclass)

    return families

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

def output_ippr(assignment, canonical, variables, n, s, outf, condition=[]):
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

    clause += condition
    cube += condition

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
    fmtstr = "%s.%0" + str(int(math.ceil(math.log10(s ** 8)))) + "d.%s"
    seen = []
    level1classes = {}
    ncnfs = 0
    n = 7
    level1vars = [(3 + 2 ** (n - 3), 5), (3 + 2 ** (n - 3), 6),
                  (3 + 2 ** (n - 2), 4), (3 + 2 ** (n - 2), 6),
                  (3 + 2 ** (n - 1), 4), (3 + 2 ** (n - 1), 5)]
    level2vars = [(3, 2), (3, 3),
                  (3 + 2 ** (n - 3), 2), (3 + 2 ** (n - 3), 3),
                  (3 + 2 ** (n - 2), 2), (3 + 2 ** (n - 2), 3),
                  (3 + 2 ** (n - 1), 2), (3 + 2 ** (n - 1), 3)]
    dnf = []
    # Problematic case for s>3
    problematic = [0, 1, 1, 0, 0, 1]
    assert(len(problematic) == len(level1vars))
    problematicvars = [convert(level1vars[i][0], level1vars[i][1], problematic[i], n, s) for i in range(0, len(level1vars))] + [convert(l2v[0], l2v[1], 0, n, s) for l2v in level2vars]
    srclasses = shift_right_families(list(range(0, 3)), 3)
    w2coordinates = [(2, 4), (2, 5), (2, 6)]

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

        # Force c_{19,6} to be 1
        if assignment[1] != 1:
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

    nvars = None
    currentclauses = []

    with open(cnffilename, 'r') as origcnf:
        m = re.match("p cnf (\d+) \d+", origcnf.readline().strip())
        nvars = int(m.group(1))

        for l in origcnf:
            currentclauses.append(l)

    with open("%s.ippr" % basename, 'w') as initialippr:
                # These clauses are RAT so we can output them straight up
                for e in [((19, 5), (35, 4)), ((35, 6), (67, 5)), ((67, 4), (19, 6))]:
                    print("%s 0" % " ".join([str(convert(i[0], i[1], 1, n, s)) for i in e]), file=initialippr)
                    currentclauses.append("%s 0\n" % " ".join([str(convert(i[0], i[1], 1, n, s)) for i in e]))

                # Force c_{19,6} to be 1
                print("%d %d %d %d 0" % (convert(level1vars[1][0], level1vars[1][1], 1, n, s), -convert(level1vars[4][0], level1vars[4][1], 1, n, s), convert(level1vars[1][0], level1vars[1][1], 1, n, s), -convert(level1vars[4][0], level1vars[4][1], 1, n, s)), file=initialippr)
                currentclauses.append("%d %d 0\n" % (convert(level1vars[1][0], level1vars[1][1], 1, n, s), -convert(level1vars[4][0], level1vars[4][1], 1, n, s)))

    with open(fmtstr % (basename, ncnfs, "cnf"), 'w') as currentcnf:
        write_cnf(currentclauses, currentcnf, nvars)

        with open(fmtstr % (basename, ncnfs, "ippr"), 'w') as problematicippr:
                # Problematic case for s > 3
                # Sort coordinates 2 and 3 of w2
                print("%d %d %s %d %d %s 0" % (convert(2, 2, 0, n, s), -convert(2, 3, 0, n, s), " ".join([str(-l) for l in problematicvars]), convert(2, 2, 0, n, s), -convert(2, 3, 0, n, s), " ".join([str(l) for l in problematicvars])), file=problematicippr)
                currentclauses.append("%d %d %s 0\n" % (convert(2, 2, 0, n, s), -convert(2, 3, 0, n, s), " ".join([str(-l) for l in problematicvars])))

                # All values greater than 1 in the 2nd and 3rd coordinates of w2 can be mapped to 1
                for i in (2, 3):
                    for j in range(2, s):
                        print("%d %d %s %d %d %s 0" % (-convert(2, i, j, n, s), convert(2, i, j - 1, n, s), " ".join([str(-l) for l in problematicvars]), -convert(2, i, j, n, s), convert(2, i, 1, n, s), " ".join([str(l) for l in problematicvars])), file=problematicippr)
                        currentclauses.append("%d %d %s 0\n" % (-convert(2, i, j, n, s), convert(2, i, j - 1, n, s), " ".join([str(-l) for l in problematicvars])))

                # All values greater than 2 in the last coordinates of w2 can be mapped to 2
                for i in range(4, n):
                    for j in range(3, s):
                        print("%d %d %s %d %d %s 0" % (-convert(2, i, j, n, s), convert(2, i, j - 1, n, s), " ".join([str(-l) for l in problematicvars]), -convert(2, i, j, n, s), convert(2, i, 2, n, s), " ".join([str(l) for l in problematicvars])), file=problematicippr)
                        currentclauses.append("%d %d %s 0\n" % (-convert(2, i, j, n, s), convert(2, i, j - 1, n, s), " ".join([str(-l) for l in problematicvars])))

    ncnfs += 1

    # Break symmetries in the last 3 coordinates of w2
    for srclass in srclasses:
        if len(srclasses[srclass]) > 0:
            with open(fmtstr % (basename, ncnfs, "cnf"), 'w') as currentcnf:
                write_cnf(currentclauses, currentcnf, nvars)

                with open(fmtstr % (basename, ncnfs, "ippr"), 'w') as srclassippr:
                    for blockedassignment in srclasses[srclass]:
                        output_ippr(blockedassignment, srclass, w2coordinates, n, s, srclassippr, condition=problematicvars)
                        currentclauses.append("%s %s 0\n" % (" ".join([str(-v) for v in assignment2vars(blockedassignment, w2coordinates, n, s)]), " ".join([str(-l) for l in problematicvars])))

            ncnfs += 1

    for cls1 in level1classes:
        if len(level1classes[cls1]) > 0:
            with open(fmtstr % (basename, ncnfs, "cnf"), 'w') as currentcnf:
                write_cnf(currentclauses, currentcnf, nvars)

                with open(fmtstr % (basename, ncnfs, "ippr"), 'w') as level1ippr:
                            for a1 in level1classes[cls1]:
                                output_ippr(a1, cls1, level1vars, n, s, level1ippr)
                                currentclauses.append("%s 0\n" % " ".join([str(-v) for v in assignment2vars(a1, level1vars, n, s)]))

            ncnfs += 1

    # Level 2 symmetry breaking: coordinates 2 and 3 of w{3,19,35,67}
    gcolor = [0] + [1] * (2 * (len(values) - 1))
    level2assignments = [[]]

    for l in range(0, len(level2vars) // 2):
        seen = {}
        gcolor += [2 + l, 2 + l]

        while len(level2assignments[0]) == 2 * l:
            for newassignment in itertools.product(values, values):
                assignment = level2assignments[0] + list(newassignment)
                g = level2_graph(assignment, s)
                repeated = False

                for cls in seen:
                    if g.isomorphic_vf2(cls[0], color1=gcolor, color2=gcolor):
                        seen[cls].append(assignment)
                        repeated = True

                        break

                if not repeated:
                    seen[(g, tuple(assignment))] = []
                    level2assignments.append(assignment)

            del level2assignments[0]

        for cls2 in seen:
            if len(seen[cls2]) > 0:
                with open(fmtstr % (basename, ncnfs, "cnf"), 'w') as currentcnf:
                    write_cnf(currentclauses, currentcnf, nvars)

                    with open(fmtstr % (basename, ncnfs, "ippr"), 'w') as level2ippr:
                                for a2 in seen[cls2]:
                                    output_ippr(a2, cls2[1], level2vars, n, s, level2ippr)
                                    currentclauses.append("%s 0\n" % " ".join([str(-v) for v in assignment2vars(a2, level2vars, n, s)]))

                ncnfs += 1

    for cls1 in level1classes:
        cls1vars = [convert(level1vars[i][0], level1vars[i][1], cls1[i], n, s) for i in range(0, len(cls1))]

        for cls2 in level2assignments:
            cls2vars = [convert(level2vars[i][0], level2vars[i][1], cls2[i], n, s) for i in range(0, len(cls2))]

            dnf.append(cls1vars + cls2vars)

    dnf = sorted(dnf)
    problematicdnf = []

    assert(dnf[0] == problematicvars)

    for w2first2 in ((0, 0), (0, 1), (1, 1)):
        w2first2vars = [convert(2, 2, w2first2[0], n, s), convert(2, 3, w2first2[1], n, s)]

        for w2next3  in srclasses:
            w2next3vars = [convert(2, 4 + i, w2next3[i], n, s) for i in range(0, len(w2next3))]

            problematicdnf.append(w2first2vars + w2next3vars)

    with open("%s.dnf" % basename, 'w') as dnffile:
        print_assignments(sorted(problematicdnf), 0, len(problematicdnf), 0, [[v] for v in dnf[0]], dnffile)
        del dnf[0]
        print_assignments(dnf, 0, len(dnf), 0, [], dnffile)
