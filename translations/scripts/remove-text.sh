#!/bin/sh

for file in "$@"; do
	basename=$(echo "$file" | sed 's/\.[^\.]\+//')
	echo "$basename"
	gimp --no-interface --batch '(python-fu-miasmata-heal-text RUN-NONINTERACTIVE "'${file}'" "'${basename}_blank'")' --batch '(gimp-quit 1)'
done
