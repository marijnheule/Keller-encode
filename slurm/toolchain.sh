#!/bin/bash

tools/pprsearch/pprsearch $1.cnf $1.ippr >$1.ppr 2>$1.pprsearch.err;
tools/ppr2drat $1.cnf $1.ppr > $1.drat;
drat-trim/drat-trim $1.cnf $1.drat -f;
