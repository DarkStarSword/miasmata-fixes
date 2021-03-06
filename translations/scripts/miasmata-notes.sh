#!/bin/sh

[ -z "$GIMP" ] && GIMP=gimp

# for note in NOTE_0 NOTE_10 NOTE_11 NOTE_12 NOTE_13 NOTE_14 NOTE_15 NOTE_16 NOTE_17 NOTE_1 NOTE_2 NOTE_3 NOTE_4 NOTE_5 NOTE_7 NOTE_8 NOTE_9 Note_A1 NOTE_A2 NOTE_A3 NOTE_A4 NOTE_A5 NOTE_A6 NOTE_A7 NOTE_A8 NOTE_A9 NOTE_AA NOTE_BB NOTE_CC NOTE_DD NOTE_EE NOTE_FF NOTE_GG NOTE_HH NOTE_II NOTE_JJ NOTE_KK NOTE_LL NOTE_MM NOTE_NN NOTE_OO NOTE_PP NOTE_QQ NOTE_RR NOTE_SS NOTE_TT NOTE_UU NOTE_VV NOTE_WW NOTE_XX NOTE_YY NOTE_ZZ
for note in "$@"
do
	if [ -f "${note}_tweaked.xcf" ]; then
		echo "OVERRIDING ${note} with ${note}_tweaked.xcf!"
		${GIMP} --no-interface --batch '(python-fu-miasmata-to-dds-jpg RUN-NONINTERACTIVE "'${note}_tweaked.xcf'" "'${note}'" 0)' --batch '(gimp-quit 1)'
	else
		blank=../../blanks/notes/${note}_blank.xcf
		${GIMP} --no-interface --batch '(python-fu-miasmata-note RUN-NONINTERACTIVE "'${note}'" "'${blank}'" "'${note}'")' --batch '(gimp-quit 1)'
	fi
done

in_world=../../blanks/in_world/
${GIMP} --no-interface --batch '(python-fu-miasmata-notes-in-world RUN-NONINTERACTIVE "'${in_world}'")' --batch '(gimp-quit 1)'
