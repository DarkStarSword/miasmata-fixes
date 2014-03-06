#!/bin/sh -e

headers=$PWD/miasmata-headers
translation=/var/www/miasmata/fr
staging=$PWD/miasmata-fr

link_dds_files()
{
	src="$1"
	dst="$2"

	for file in $(find "$src" -name "*.dds"); do
		name=$(basename "$file" .dds)
		mkdir -vp "$staging/$dst/$name"
		ln -sv "$headers/$dst/$name/"* "$staging/$dst/$name/"
		ln -sv "$file" "$staging/$dst/$name/02-DATA.dds"
	done
}

rm -frv "$staging"

mkdir -p "$staging/TEX/J2"
for dir in index drugs plants research; do
	link_dds_files "$translation/$dir" "TEX/J2"
done

mkdir -p "$staging/TEX/MENU"
for dir in intro end; do
	link_dds_files "$translation/$dir" "TEX/MENU"
done

for dir in blackboards; do
	link_dds_files "$translation/$dir" "TEX"
done
