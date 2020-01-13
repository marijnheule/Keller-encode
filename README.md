# Keller-encode
Code related to Keller's conjecture

## Quick Start Guide
The wrapper Python script requires the `python-igraph` package, you can install it with 

```bash
$ pip3 install --user python-igraph
```

To compile all the necessary tools, run

```bash
$ make all
```

To generate the files and proofs for the cases s = {3,4,6}, special targets can be invoked, e.g.:

```bash
$ make s3
```

## Compilation Details
One of the required packages is CryptoMiniSat 5, which in turn requires [CMake](https://cmake.org/) for compilation. To specify special arguments for CMake, use the `CMAKEARGS` variable, e.g.:

```bash
$ make cryptominisat-build/pycryptosat CMAKEARGS="-DCMAKE_C_COMPILER=gcc -DCMAKE_CXX_COMPILER=g++"
```

One can specify the location of the Boost installation in order to compile the `pprsearch` tool:

```bash
$ make tools/pprsearch/pprsearch BOOST_ROOT=/path/to/boost
```
