#!/bin/bash

SLURMDIR=$(dirname $0);
TIMELIMIT="48:00:00"
PARTITION="normal"

for i in $(ls -1 s$1*.ippr); do
    basename=$(basename $i .ippr);
    echo $basename;
    sbatch -t $TIMELIMIT -N 1 -n 1 -p $PARTITION -o $basename.log "$SLURMDIR/toolchain.sh" $basename;
done
