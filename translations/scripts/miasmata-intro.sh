#!/bin/sh

[ -z "$GIMP" ] && GIMP=gimp

for slide in A B C D E F G
do
	${GIMP} --no-interface --batch '(python-fu-miasmata-intro-slide RUN-NONINTERACTIVE "Intro_'${slide}'.txt" "Intro_'${slide}'")' --batch '(gimp-quit 1)'
done
