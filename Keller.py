import sys
import os
import re
import math
import itertools
import subprocess
import collections

import igraph

class KellerOutputManager:
    def __init__(self, upper_bound, clauses, nvars, pprsearch, ppr2drat):
        self.fmtstr = "%s.%0" + str(upper_bound) + "d"
        self.clauses = clauses
        self.nvars = nvars
        self.noutputs = {}
        self.pprsearch = pprsearch
        self.ppr2drat = ppr2drat

    def new_output(self, label):
        if label in self.noutputs:
            self.noutputs[label] += 1
        else:
            self.noutputs[label] = 0

        return self.fmtstr % (label, self.noutputs[label])

    def write_cnf(self, filename):
        with open(filename, 'w') as cnffile:
            print("p cnf %d %d" % (self.nvars, len(self.clauses)), file=cnffile)

            for l in self.clauses:
                cnffile.write(l)

class KellerOutput:
    def __init__(self, manager, label):
        self.manager = manager
        self.label = self.manager.new_output(label)
        self.outfile = None

    def __enter__(self):
        self.manager.write_cnf("%s.cnf" % self.label)

        if self.manager.pprsearch is None:
            self.outfile = open("%s.ippr" % self.label, 'w')
        elif self.manager.ppr2drat is None:
            self.outfile = open("%s.ppr" % self.label, 'w')
        else:
            self.outfile = open("%s.drat" % self.label, 'w')

        if self.manager.pprsearch is not None:
            self.pprsearch = subprocess.Popen([self.manager.pprsearch, "%s.cnf" % self.label],
                                              stdout=subprocess.PIPE if self.manager.ppr2drat is not None else self.outfile,
                                              stdin=subprocess.PIPE,
                                              stderr=subprocess.DEVNULL,
                                              universal_newlines=True)

            if self.manager.ppr2drat is not None:
                self.ppr2drat = subprocess.Popen([self.manager.ppr2drat, "%s.cnf" % self.label, "-"],
                                                 stdin=self.pprsearch.stdout,
                                                 stdout=self.outfile,
                                                 universal_newlines=True)

            self.infile = self.pprsearch.stdin
        else:
            self.infile = self.outfile

        return self

    def __exit__(self, extype, exvalue, tb):
        if self.manager.pprsearch is not None:
            self.pprsearch.stdin.close()

        if self.manager.ppr2drat is not None:
            assert(self.ppr2drat.wait() == 0)
            self.ppr2drat.__exit__(extype, exvalue, tb)

        if self.manager.pprsearch is not None:
            assert(self.pprsearch.wait() == 0)
            self.pprsearch.__exit__(extype, exvalue, tb)

        self.outfile.__exit__(extype, exvalue, tb)

    def add_rat(self, clause):
        clause_line = "%s 0" % " ".join([str(l) for l in clause])
        
        print(clause_line, file=self.infile)
        self.manager.clauses.append("%s\n" % clause_line)

    def add_ippr(self, clause, cube):
        clause_line = "%s" % " ".join([str(l) for l in clause])

        print("%s %s 0" % (clause_line, " ".join([str(l) for l in cube])), file=self.infile)
        self.manager.clauses.append("%s 0\n" % clause_line)

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

def ippr_clause_and_cube(assignment, canonical, variables, n, s, condition=[]):
    assert(len(assignment) == len(canonical))

    for diff in range(0, len(assignment)):
        if canonical[diff] != assignment[diff]:
            break

    assert(diff < len(assignment))
    clause = assignment2vars(assignment, variables, n, s)
    cube = assignment2vars(canonical, variables, n, s)

    for i in range(0, s):
        if clause[s * diff + i] == -cube[s * diff + i]:
            break

    assert(i < s)
    clause.insert(0, clause[s * diff + i])
    del clause[s * diff + i + 1]
    clause += condition
    cube.insert(0, cube[s * diff + i])
    del cube[s * diff + i + 1]
    cube += condition

    return ([-l for l in clause], cube)

def tautological_assignments(dnf, i1, i2, j, trails, tautology):
    if j >= len(dnf[i1]):
        tautology.append(list(itertools.chain.from_iterable(trails)))

        return

    trail = [dnf[i1][j]]

    for i in range(i1, i2):
        if dnf[i][j] not in trail:
            tautological_assignments(dnf, i1, i, j + 1, trails + [trail], tautology)

            i1 = i
            trail[-1] = -trail[-1]

            trail.append(dnf[i][j])

    del trail[-1]
    tautological_assignments(dnf, i1, i2, j + 1, trails + [trail], tautology)

if __name__ == "__main__":
    s = int(sys.argv[1])
    basename = sys.argv[2]
    pprsearch_binary = None if len(sys.argv) < 5 else sys.argv[4]
    ppr2drat_binary = None if len(sys.argv) < 6 else sys.argv[5]
    values = list(range(0, s))
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
    nvars = None
    currentclauses = []
    dnf = []
    # Problematic case for s>3
    problematic = [0, 1, 1, 0, 0, 1]
    assert(len(problematic) == len(level1vars))
    problematicvars = [convert(level1vars[i][0], level1vars[i][1], problematic[i], n, s) for i in range(0, len(level1vars))] + [convert(l2v[0], l2v[1], 0, n, s) for l2v in level2vars]
    srclasses = shift_right_families(list(range(0, 3)), 3)
    w2coordinates = [(2, 4), (2, 5), (2, 6)]

    with subprocess.Popen([sys.argv[3], "7", str(s)], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, universal_newlines=True) as KellerEncode:
        m = re.match("p cnf (\d+) \d+", KellerEncode.stdout.readline().strip())
        nvars = int(m.group(1))

        for l in KellerEncode.stdout:
            currentclauses.append(l)

    output_manager = KellerOutputManager(int(math.ceil(math.log10(s ** 8))), currentclauses, nvars, pprsearch_binary, ppr2drat_binary)

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

    with KellerOutput(output_manager, basename) as current_output:
        # These clauses are RAT so we can output them straight up
        for e in [((19, 5), (35, 4)), ((35, 6), (67, 5)), ((67, 4), (19, 6))]:
            current_output.add_rat([convert(i[0], i[1], 1, n, s) for i in e])

        # Force c_{19,6} to be 1
        current_output.add_ippr([convert(level1vars[1][0], level1vars[1][1], 1, n, s), -convert(level1vars[4][0], level1vars[4][1], 1, n, s)], [convert(level1vars[1][0], level1vars[1][1], 1, n, s), -convert(level1vars[4][0], level1vars[4][1], 1, n, s)])

    # Problematic case for s > 3
    with KellerOutput(output_manager, basename) as current_output:
        negproblematicvars = [-l for l in problematicvars]

        # Sort coordinates 2 and 3 of w2
        current_output.add_ippr([convert(2, 2, 0, n, s), -convert(2, 3, 0, n, s)] + negproblematicvars, [convert(2, 2, 0, n, s), -convert(2, 3, 0, n, s)] + problematicvars)

        # All values greater than 1 in the 2nd and 3rd coordinates of w2 can be mapped to 1
        for i in (2, 3):
            for j in range(2, s):
                current_output.add_ippr([-convert(2, i, j, n, s), convert(2, i, j - 1, n, s)] + negproblematicvars, [-convert(2, i, j, n, s), convert(2, i, 1, n, s)] + problematicvars)

        # All values greater than 2 in the last coordinates of w2 can be mapped to 2
        for i in range(4, n):
            for j in range(3, s):
                current_output.add_ippr([-convert(2, i, j, n, s), convert(2, i, j - 1, n, s)] + negproblematicvars, [-convert(2, i, j, n, s), convert(2, i, 2, n, s)] + problematicvars)

    # Break symmetries in the last 3 coordinates of w2
    for srclass in srclasses:
        if len(srclasses[srclass]) > 0:
            with KellerOutput(output_manager, basename) as current_output:
                for blockedassignment in srclasses[srclass]:
                    clause, cube = ippr_clause_and_cube(blockedassignment, srclass, w2coordinates, n, s, condition=problematicvars)

                    current_output.add_ippr(clause, cube)

    for cls1 in level1classes:
        if len(level1classes[cls1]) > 0:
            with KellerOutput(output_manager, basename) as current_output:
                for a1 in level1classes[cls1]:
                    clause, cube = ippr_clause_and_cube(a1, cls1, level1vars, n, s)

                    current_output.add_ippr(clause, cube)

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
                with KellerOutput(output_manager, basename) as current_output:
                    for a2 in seen[cls2]:
                        clause, cube = ippr_clause_and_cube(a2, cls2[1], level2vars, n, s)

                        current_output.add_ippr(clause, cube)
    
                ncnfs += 1

    # Write the final CNF
    output_manager.write_cnf("%s.cnf" % basename)

    for cls1 in level1classes:
        cls1vars = [convert(level1vars[i][0], level1vars[i][1], cls1[i], n, s) for i in range(0, len(cls1))]

        for cls2 in level2assignments:
            cls2vars = [convert(level2vars[i][0], level2vars[i][1], cls2[i], n, s) for i in range(0, len(cls2))]

            dnf.append(cls1vars + cls2vars)

    dnf = sorted(dnf)
    problematicdnf = []
    tautology = []
    subtautology = []

    assert(dnf[0] == problematicvars)

    for w2first2 in ((0, 0), (0, 1), (1, 1)):
        w2first2vars = [convert(2, 2, w2first2[0], n, s), convert(2, 3, w2first2[1], n, s)]

        for w2next3  in srclasses:
            w2next3vars = [convert(2, 4 + i, w2next3[i], n, s) for i in range(0, len(w2next3))]

            problematicdnf.append(w2first2vars + w2next3vars)

    tautological_assignments(dnf, 0, len(dnf), 0, [], tautology)
    tautological_assignments(problematicdnf, 0, len(problematicdnf), 0, [tautology[0]], subtautology)

    with open("%s.dnf" % basename, 'w') as dnffile:
        for t in subtautology:
            print("a %s 0" % " ".join([str(l) for l in t]), file=dnffile)

        for t in tautology[1:]:
            print("a %s 0" % " ".join([str(l) for l in t]), file=dnffile)
