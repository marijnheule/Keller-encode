#!/bin/bash

SLURMDIR=$(dirname $0);
TIMELIMIT="48:00:00"
PARTITION="normal"

for i in $(ls -1 s$1*.ippr); do
    basename=$(basename $i .ippr);
    echo $basename;
    pprsearchjid=$(sbatch --parsable -t $TIMELIMIT -N 1 -n 1 -p $PARTITION -o $basename.ppr -e $basename.pprsearch.err "$SLURMDIR/pprsearch.sh" $basename.cnf $i | tail -1);
    ppr2dratjid=$(sbatch -d "after:$pprsearchjid" --parsable -t $TIMELIMIT -N 1 -n 1 -p $PARTITION -o $basename.drat -e $basename.ppr2drat.err "$SLURMDIR/ppr2drat.sh" $basename.cnf $basename.ppr | tail -1);
    sbatch -d "after:$ppr2dratjid" -t $TIMELIMIT -N 1 -n 1 -p $PARTITION -o $basename.log -e $basename.drat-trim.err "$SLURMDIR/drat-trim.sh" $basename.cnf $basename.drat -f;
done
