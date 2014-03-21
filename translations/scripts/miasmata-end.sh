#!/bin/sh

[ -z "$GIMP" ] && GIMP=gimp

for slide in A B C D K
do
	first=0
	[ "$slide" = "A" ] && first=1
	${GIMP} --no-interface --batch '(python-fu-miasmata-end-slide RUN-NONINTERACTIVE "End1_'${slide}'.txt" "End1_'${slide}'" '${first}')' --batch '(gimp-quit 1)'
done

for slide in E F
do
	# Credits
	echo
done

for slide in H I J
do
	# Special Thanks To...
	echo
done
