#!/bin/sh

[ -z "$GIMP" ] && GIMP=gimp

for tab in Lab Notes Status; do
	basename=TABS_${tab}
	blank=../../blanks/tabs/${basename}.xcf
	${GIMP} --no-interface --batch '(python-fu-miasmata-journal-tabs RUN-NONINTERACTIVE "'${basename}.txt'" "'${blank}'" "'${basename}'")' --batch '(gimp-quit 1)'
done
