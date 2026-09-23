#!/bin/bash
R=/tmp/reuse-probe; V=$1
{ for s in A1-jobs A2-emails; do for n in 1 2; do echo "$V $s $n"; done; done; } | xargs -P 4 -n 3 $R/run_one.sh
echo "BATCH $V COMPLETE"
