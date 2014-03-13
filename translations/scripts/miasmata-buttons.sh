#!/bin/sh

[ -z "$GIMP" ] && GIMP=gimp

for button in yes no; do
	for sel in sel bkg; do
		basename=${button}_${sel}
		blank=../../blanks/buttons/${basename}_blank.png
		${GIMP} --no-interface --batch '(python-fu-miasmata-button RUN-NONINTERACTIVE "'${button}.txt'" "'${blank}'" "'${basename}'")' --batch '(gimp-quit 1)'
	done
done
