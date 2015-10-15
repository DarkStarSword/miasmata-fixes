#!/bin/sh

[ -z "$GIMP" ] && GIMP=gimp

for file in "$@"
do
	dir=$(dirname "$file")
	out="$dir/$(basename "$file" .dds).jpg"
	echo "$out"
	${GIMP} --no-interface --batch '(let* ( (image (car (gimp-file-load RUN-NONINTERACTIVE "'$file'" "'$file'"))) (drawable (car (gimp-image-merge-visible-layers image CLIP-TO-IMAGE))) ) (file-jpeg-save RUN-NONINTERACTIVE image drawable "'$out'" "'$out'" 0.9 0.0 1 0 "" 0 1 0 1) )' --batch '(gimp-quit 1)'
done
