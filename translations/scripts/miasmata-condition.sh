#!/bin/sh

[ -z "$GIMP" ] && GIMP=gimp

# Two letter status:
for drug in AdrenalineStimulant HerculeanTonic MentalStimulant
do
	basename=Condition_${drug}_Active
	strip=$(echo "$basename" | sed 's/_[^_]\+$//')
	blank=../../blanks/conditions/${strip}_blank.png
	${GIMP} --no-interface --batch '(python-fu-miasmata-condition-small RUN-NONINTERACTIVE "'${basename}.txt'" "'${blank}'" "'${basename}'")' --batch '(gimp-quit 1)'
done

# Large status messages:
for condition in A B ClarityTonic; do
	for file in Condition_${condition}_*.txt; do
		basename=$(echo "$file" | sed 's/\.[^\.]\+$//')
		strip=$(echo "$basename" | sed 's/_[^_]\+$//')
		blank=../../blanks/conditions/${strip}_blank.png
		${GIMP} --no-interface --batch '(python-fu-miasmata-condition-active RUN-NONINTERACTIVE "'${basename}.txt'" "'${blank}'" "'${basename}'")' --batch '(gimp-quit 1)'
	done
done

# x:y divided conditions:
for condition in Primary Strength Endurance Perception; do
	for file in Condition_${condition}_*.txt; do
		basename=$(echo "$file" | sed 's/\.[^\.]\+$//')
		strip=$(echo "$basename" | sed 's/_[^_]\+$//')
		blank=../../blanks/conditions/${strip}_blank.png
		${GIMP} --no-interface --batch '(python-fu-miasmata-condition-split RUN-NONINTERACTIVE "'${basename}.txt'" "'${blank}'" "'${basename}'")' --batch '(gimp-quit 1)'
	done
done

basename=STATUS_LeftPage
blank=../../blanks/conditions/${basename}_blank.png
${GIMP} --no-interface --batch '(python-fu-miasmata-condition-page RUN-NONINTERACTIVE "'${basename}.txt'" "'${blank}'" "'${basename}'")' --batch '(gimp-quit 1)'
