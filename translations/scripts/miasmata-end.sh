#!/bin/sh

[ -z "$GIMP" ] && GIMP=gimp

for slide in A # B C D K # Others will need special handling
do
	${GIMP} --no-interface --batch '(python-fu-miasmata-end-slide RUN-NONINTERACTIVE "End1_'${slide}'.txt" "End1_'${slide}'")' --batch '(gimp-quit 1)'
done
