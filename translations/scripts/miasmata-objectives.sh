#!/bin/sh

[ -z "$GIMP" ] && GIMP=gimp

for file in OBJNOTE_*.txt; do
	basename=$(echo "$file" | sed 's/\.[^\.]\+//')
	blank=../../blanks/objectives/OBJNOTE_A_Placeholder1.png
	if [ "$basename" = "OBJNOTE_F_A3" \
			-o "$basename" = "OBJNOTE_G_A2" \
			-o "$basename" = "OBJNOTE_H_A4" ]; then
		blank=../../blanks/objectives/OBJNOTE_G_Placeholder1.png
	fi
	${GIMP} --no-interface --batch '(python-fu-miasmata-objective-note RUN-NONINTERACTIVE "'${basename}.txt'" "'${blank}'" "'${basename}'")' --batch '(gimp-quit 1)'
done

basename=STATUS_RightPage
blank=../../blanks/objectives/${basename}_blank.png
${GIMP} --no-interface --batch '(python-fu-miasmata-objective-page RUN-NONINTERACTIVE "'${basename}.txt'" "'${blank}'" "'${basename}'")' --batch '(gimp-quit 1)'

basename=OBJECTIVE_A_Placeholder
blank=../../blanks/objectives/${basename}_blank.png
${GIMP} --no-interface --batch '(python-fu-miasmata-objective RUN-NONINTERACTIVE "'${basename}'" "'${blank}'" "'${basename}'")' --batch '(gimp-quit 1)'

for objective in A B C D E F G H
do
	for state in Finished Open; do
		objective_name=OBJECTIVE_${objective}
		output_basename=OBJECTIVE_${objective}_${state}
		blank=../../blanks/objectives/${output_basename}_blank.png
		${GIMP} --no-interface --batch '(python-fu-miasmata-objective RUN-NONINTERACTIVE "'${objective_name}'" "'${blank}'" "'${output_basename}'")' --batch '(gimp-quit 1)'
	done
done
