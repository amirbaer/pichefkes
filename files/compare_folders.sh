#!/bin/bash

if [[ $# != 2 ]]; then
	echo "usage: $0 <source dir> <dest dir>"
	exit 1
fi

source_dir="$1"
dest_dir="$2"

work_dir="/tmp/cf-$RANDOM"
mkdir "$work_dir"
echo "work dir: $work_dir"

IFS=$'\n'

s1="$work_dir/01_source_heic.txt"
s2="$work_dir/02_source_sorted_sized_heic.txt"
d1=`echo $s1 | sed 's/source/dest/g'`
d2=`echo $s1 | sed 's/source/dest/g'`

process_dir () {
	id="$1"
	of1="$2"
	of2="$3"
	category="$4"

	# TODO: this only looks at HEIC files, we will need MOV videos and perhaps other file types as well
	echo -n "reading $category dir... "
	find "$id" -type f -iname '*.HEIC' -exec realpath {} ';' > "$of1"
	echo "found `wc -l $of1 | awk '{print $1}'` files"

	echo "checking file sizes..."
	for f in `cat $of1`; do
		b=$(basename "$f")
		pd=$(basename $(dirname "$f"))
		fs=$(du -k "$f" | awk '{print $1}')
		echo "$pd|$b|$fs|$f" >> "$of2"
		echo -n "."
	done

	echo
	echo "sorting file list..."
	sort -o "$of2"{,}
}

process_dir "$source_dir" "$s1" "$s2" "source"
process_dir "$dest_dir" "$d1" "$d2" "dest"



# Now we need to figure out how to compare these two lists
# Well let's run the script first and see the lists

echo "done"
