#!/bin/sh

[ -z "$GIMP" ] && GIMP=gimp

for drug in A B C D E F H I J X Y Z
do
	basename=Plant_$drug
	blank=../../blanks/drugs/${basename}_blank.xcf
	${GIMP} --no-interface --batch '(python-fu-miasmata-drug RUN-NONINTERACTIVE "template.txt" "'${basename}.txt'" "'${blank}'" "'${basename}'")' --batch '(gimp-quit 1)'
done
