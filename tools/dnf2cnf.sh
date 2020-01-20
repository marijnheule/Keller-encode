#!/bin/bash

# Contrary to what the name suggests, this does NOT transform a DNF
# into a CNF. It merely rewrites the cubes in the format the tautology
# tool expects.

nvars=$(head -1 $1 | awk '{ print $3}');
nclauses=$(cat $1 | wc -l);
echo "p cnf $nvars $nclauses"
sed 's/^a //' $1
