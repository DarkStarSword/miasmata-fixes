#!/bin/sh

[ -z "$GIMP" ] && GIMP=gimp

basename=LIST_NoteDD
textfile="$basename".txt
blank=../../../../../translations/blanks/index/${basename}_blank.png
${GIMP} --no-interface --batch '(python-fu-miasmata-index RUN-NONINTERACTIVE "'${textfile}'" "'${blank}'" "'${basename}'")' --batch '(gimp-quit 1)'
mv -f "$basename.dds" 02-DATA.dds
