#!/bin/bash
# Copyright 2011 bicycle trading, llc.

mysqldump \
--no-create-info \
--tab=/tmp/fx \
--tz-utc \
--force \
--ignore-table=fx_15sec.collect \
--ignore-table=fx_15sec.collect_IB_errors \
fx_15sec

for i in `ls *_tks.txt`; do sort -nk1 $i > $i.sorted; done

for i in `ls *_tks.txt.sorted`; do rename 's/\_tks\.txt\.sorted/\.tks/' $i; done

for i in `ls *.tks`; do date_to_ts.py $i > $i.ts; done

for i in `ls *.tks`; do rename -f 's/\.tks/\.tks\.orig/' $i; done

for i in `ls *.tks.ts`; do rename -f 's/\.tks\.ts/\.tks/' $i; done
