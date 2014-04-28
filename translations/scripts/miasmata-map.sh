#!/bin/sh

[ -z "$GIMP" ] && GIMP=gimp

basename=Map_OverlayInfo
blank=../../blanks/maps/${basename}_blank.png
${GIMP} --no-interface --batch '(python-fu-miasmata-map RUN-NONINTERACTIVE "'${blank}'" "'${basename}'" 1)' --batch '(gimp-quit 1)'

# # Map_FilledIn doesn't contain any text, but this version includes some fixes
# # XXX: This is now handled via communitypatch.rs5mod and MiasPatch
# basename=Map_FilledIn
# blank=../../blanks/maps/${basename}.png
# ${GIMP} --no-interface --batch '(python-fu-miasmata-map RUN-NONINTERACTIVE "'${blank}'" "'${basename}'" 0)' --batch '(gimp-quit 1)'
