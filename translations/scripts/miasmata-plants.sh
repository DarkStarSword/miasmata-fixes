#!/bin/sh

[ -z "$GIMP" ] && GIMP=gimp

for plant in 00 $(seq 0 34)
do
	basename=Plant_$plant
	blank=../../blanks/plants/${basename}_blank.xcf
	${GIMP} --no-interface --batch '(python-fu-miasmata-plant RUN-NONINTERACTIVE "template.txt" "'${basename}.txt'" "'${blank}'" "'${basename}'")' --batch '(gimp-quit 1)'
done
