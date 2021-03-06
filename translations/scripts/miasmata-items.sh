#!/bin/sh

[ -z "$GIMP" ] && GIMP=gimp

# for file in *.txt
for file in Tags.txt Lab_SampleTrays.txt Lab_DarkBottle.txt Lab_BlueBottle.txt
do
	basename=$(echo "$file" | sed 's/\.[^\.]\+$//')
	blank=../../blanks/items/${basename}_blank.png
	${GIMP} --no-interface --batch '(python-fu-miasmata-item RUN-NONINTERACTIVE "'${basename}'" "'${blank}'" "'${basename}'")' --batch '(gimp-quit 1)'
done
