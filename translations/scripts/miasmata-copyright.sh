#!/bin/sh

[ -z "$GIMP" ] && GIMP=gimp

${GIMP} --no-interface --batch '(python-fu-miasmata-copyright RUN-NONINTERACTIVE "copyright.txt" "copyright")' --batch '(gimp-quit 1)'
