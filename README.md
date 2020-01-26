# Keller-encode
Code related to Keller's conjecture

## Quick Start Guide
The wrapper Python script requires the `python-igraph` package, you
can install it with

```bash
$ pip3 install --user python-igraph
```

To compile all the necessary tools, run

```bash
$ make all
```

To generate the files and proofs for the cases s = {3,4,6}, special
targets can be invoked, e.g.:

```bash
$ make s3
```

## Compilation Details
One can specify the location of the Boost installation in order to
compile the `pprsearch` tool:

```bash
$ make tools/pprsearch/pprsearch BOOST_ROOT=/path/to/boost
```

## ACL2 Verified Checker

The proofs of unsatisfiability can be verified using
drat-trim. Alternatively, you can use the ACL2 verified checker for
these proofs. To build the ACL2 checker you will need a Common Lisp
implementation. This build has been tested with Steel Bank Common Lisp
(sbcl) and Clozure (ccl).

Targets are provided for getting the sources, certifying the checker
and building a binary for it:

```bash
$ make acl2-8.2/books/projects/sat/lrat/cube/cube-check
```

The default Common Lisp implementation is sbcl. You can specify your
own implementation:

```bash
$ make acl2-8.2/books/projects/sat/lrat/cube/cube-check LISP=ccl
```

You can test this installation with the provided examples:

```bash
$ acl2-8.2/books/projects/sat/lrat/cube/cube-check/run.sh examples/<example>.cnf examples/<example>.clrat examples/<example>-out.cnf
```
