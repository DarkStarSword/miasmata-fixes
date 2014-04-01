#!/bin/sh

[ -z "$GIMP" ] && GIMP=gimp

for basename in RESEARCH_0 Research_K
do
	blank=../../blanks/research/${basename}_blank.xcf
	echo $basename
	${GIMP} --no-interface --batch '(python-fu-miasmata-research2 RUN-NONINTERACTIVE "template.txt" "'${basename}.txt'" "'${blank}'" "'${basename}'")' --batch '(gimp-quit 1)'
done

for research in 00 $(seq 1 34)
do
	basename=RESEARCH_$research
	blank=../../blanks/research/${basename}_blank.xcf
	echo $basename
	${GIMP} --no-interface --batch '(python-fu-miasmata-research RUN-NONINTERACTIVE "template.txt" "'${basename}.txt'" "'${basename}_conclusion.txt'" "'${blank}'" "'${basename}'")' --batch '(gimp-quit 1)'
done
