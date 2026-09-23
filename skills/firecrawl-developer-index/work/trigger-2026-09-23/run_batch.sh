#!/bin/bash
# usage: run_batch.sh VARIANT
R=/tmp/reuse-probe; V=$1
{ for s in P1-cron P2-retry P3-links P4-vcard; do for n in 1 2; do echo "$V $s $n"; done; done
  for s in N1-rename N2-bug; do echo "$V $s 1"; done; } | xargs -P 5 -n 3 $R/run_one.sh
echo "BATCH $V COMPLETE"
