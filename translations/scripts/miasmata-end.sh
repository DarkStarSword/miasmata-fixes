#!/bin/sh

[ -z "$GIMP" ] && GIMP=gimp

for slide in A B C D K
do
	first=0
	[ "$slide" = "A" ] && first=1
	${GIMP} --no-interface --batch '(python-fu-miasmata-end-slide RUN-NONINTERACTIVE "End1_'${slide}'.txt" "End1_'${slide}'" '${first}')' --batch '(gimp-quit 1)'
done

for slide in F G G_modA G_modB
do
	${GIMP} --no-interface --batch '(python-fu-miasmata-end-slide-credits RUN-NONINTERACTIVE "End1_'${slide}'.txt" "End1_'${slide}'")' --batch '(gimp-quit 1)'
done

for slide in H I J
do
	blank=../../blanks/end/End1_${slide}_blank.png
	[ ! -f "$blank" ] && blank=
	${GIMP} --no-interface --batch '(python-fu-miasmata-end-slide-thanks RUN-NONINTERACTIVE "End1_'${slide}'.txt" "End1_'${slide}'" "'${blank}'")' --batch '(gimp-quit 1)'
done
