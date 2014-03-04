#!/bin/sh

[ -z "$GIMP" ] && GIMP=gimp

for textfile in *.txt
do
	basename=$(basename "$textfile" ".txt")
	blank=$(dirname "$textfile")/../../blanks/index/${basename}_blank.png
	${GIMP} --no-interface --batch '(python-fu-miasmata-index RUN-NONINTERACTIVE "'${textfile}'" "'${blank}'" "'${basename}'")' --batch '(gimp-quit 1)'
done
