#!/bin/bash
R=/tmp/reuse-probe; V=$1
{ for s in M1-links M2-vcf M3-frontmatter; do for n in 1 2; do echo "$V $s $n"; done; done; } | xargs -P 6 -n 3 $R/run_one_hook.sh
echo "BATCH $V COMPLETE"
