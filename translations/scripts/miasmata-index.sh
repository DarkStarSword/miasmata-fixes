#!/bin/sh

[ -z "$GIMP" ] && GIMP=gimp

for basename in LIST_TITLE_Notes LIST_TITLE_Research
do
	textfile="$basename".txt
	blank=../../blanks/index/LIST_TITLE_Placeholder.png
	${GIMP} --no-interface --batch '(python-fu-miasmata-index-title RUN-NONINTERACTIVE "'${textfile}'" "'${blank}'" "'${basename}'")' --batch '(gimp-quit 1)'
done

for basename in LIST_00a LIST_00b LIST_0a LIST_0b LIST_10a LIST_10b LIST_11a LIST_11b LIST_12a LIST_12b LIST_13a LIST_13b LIST_14a LIST_14b LIST_15a LIST_15b LIST_16a LIST_16b LIST_17a LIST_17b LIST_18a LIST_18b LIST_19a LIST_19b LIST_1a LIST_1b LIST_20a LIST_20b LIST_21a LIST_21b LIST_22a LIST_22b LIST_23a LIST_23b LIST_24a LIST_24b LIST_25a LIST_25b LIST_26a LIST_26b LIST_27a LIST_27b LIST_28a LIST_28b LIST_29a LIST_29b LIST_2a LIST_2b LIST_30a LIST_30b LIST_31a LIST_31b LIST_32a LIST_32b LIST_33a LIST_33b LIST_34a LIST_34b LIST_3a LIST_3b LIST_4a LIST_4b LIST_5a LIST_5b LIST_6a LIST_6b LIST_7a LIST_7b LIST_8a LIST_8b LIST_9a LIST_9b LIST_A LIST_B LIST_C LIST_D LIST_E LIST_F LIST_H LIST_IAmCured LIST_I LIST_J LIST_NoResult LIST_Note0 LIST_Note10 LIST_Note11 LIST_Note12 LIST_Note13 LIST_Note14 LIST_Note15 LIST_Note16 LIST_Note17 LIST_Note18 LIST_Note1 LIST_Note2 LIST_Note3 LIST_Note4 LIST_Note5 LIST_Note7 LIST_Note8 LIST_Note9 LIST_NoteA1 LIST_NoteA2 LIST_NoteA3 LIST_NoteA4 LIST_NoteA5 LIST_NOTEA6 LIST_NoteA7 LIST_NoteA8 LIST_NoteA9 LIST_NoteAA LIST_NoteBB LIST_NoteCC LIST_NoteDD LIST_NoteEE LIST_NoteFF LIST_NoteGG LIST_NoteHH LIST_NoteII LIST_NoteJJ LIST_NoteKK LIST_NoteLL LIST_NoteMM LIST_NoteNN LIST_NoteOO LIST_NotePP LIST_NoteQQ LIST_NoteRR LIST_NoteSS LIST_NoteTT LIST_NoteUU LIST_NoteVV LIST_NoteWW LIST_NoteXX LIST_NoteYY LIST_NoteZZ LIST_X LIST_Y LIST_Z List_K
do

	textfile="$basename".txt
	blank=../../blanks/index/${basename}_blank.png
	${GIMP} --no-interface --batch '(python-fu-miasmata-index RUN-NONINTERACTIVE "'${textfile}'" "'${blank}'" "'${basename}'")' --batch '(gimp-quit 1)'
done
