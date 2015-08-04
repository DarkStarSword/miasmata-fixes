#!/bin/sh -e

headers=$PWD/miasmata-headers
translation=/var/www/html/miasmata/ita
staging=$PWD/miasmata-ita
miasmata_fixes_top=$(readlink -f $(dirname $(readlink -f "$0"))/../../)
mod_name="$1"
mod_version="$2"

if [ -z "$mod_version" ]; then
	echo "usage: $0 name version"
	exit 1
fi

link_dds_files()
{
	src="$1"
	dst="$2"
	pattern="$3"
	[ -z "$pattern" ] && pattern="*.dds"

	for file in $(find "$src" -name "$pattern"); do
		name=$(basename "$file" .dds)
		mkdir -vp "$staging/$dst/$name"
		ln -sfv "$headers/$dst/$name/"* "$staging/$dst/$name/"
		ln -sfv "$file" "$staging/$dst/$name/02-DATA.dds"
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

for dir in blackboards items maps; do
	link_dds_files "$translation/$dir" "TEX"
done

link_dds_files "$translation/notes" "TEX/J2" "N*_*.dds"
link_dds_files "$translation/notes" "TEX" "InWorldNotesz_Set*.dds"
link_dds_files "$translation/notes" "TEX" "Notes.dds"
link_dds_files "$translation/" "TEX/MENU" "copyright.dds"

# Add mod name & version metadata:
mkdir -p "$staging/MIASMOD/MODINFO"
${miasmata_fixes_top}/rs5file.py META 'MIASMOD\MODINFO' > "$staging/MIASMOD/MODINFO/00-HEADER"
echo -n "$mod_name" > "$staging/MIASMOD/MODINFO/01-NAME"
echo -n "$mod_version" > "$staging/MIASMOD/MODINFO/02-VRSN"
