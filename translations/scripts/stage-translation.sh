#!/bin/sh -e

headers=$PWD/miasmata-headers
translation=/var/www/miasmata/fr
staging=$PWD/miasmata-fr

link_dds_files()
{
	src="$1"
	dst="$2"
	pattern="$3"
	[ -z "$pattern" ] && pattern="*.dds"

	for file in $(find "$src" -name "$pattern"); do
		name=$(basename "$file" .dds)
		mkdir -vp "$staging/$dst/$name"
		ln -sv "$headers/$dst/$name/"* "$staging/$dst/$name/"
		ln -sv "$file" "$staging/$dst/$name/02-DATA.dds"
	done
}

rm -frv "$staging"

mkdir -p "$staging/TEX/J2"
for dir in index drugs plants research objectives conditions tabs; do
	link_dds_files "$translation/$dir" "TEX/J2"
done

mkdir -p "$staging/TEX/MENU"
for dir in intro end buttons; do
	link_dds_files "$translation/$dir" "TEX/MENU"
done

for dir in blackboards items; do
	link_dds_files "$translation/$dir" "TEX"
done

link_dds_files "$translation/notes" "TEX/J2" "N*_*.dds"
link_dds_files "$translation/notes" "TEX" "InWorldNotesz_Set*.dds"
link_dds_files "$translation/notes" "TEX" "Notes.dds"
