#!/bin/bash
R=/tmp/reuse-probe; V=$1
{ for s in Q1-default Q2-version E1-esm; do for n in 1 2; do echo "$V $s $n"; done; done; } | xargs -P 6 -n 3 $R/run_one.sh
echo "BATCH $V COMPLETE"
