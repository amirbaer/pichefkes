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

read_dir () {
	d="$1"
	f1="$2"
	f2="$3"
	category="$4"

	# TODO: this only looks at HEIC files, we will need MOV videos and perhaps other file types as well
	echo -n "reading $category dir... "
	find "$d" -type f -iname '*.HEIC' -exec realpath {} ';' > "$s1"
	echo "found `wc -l $s1 | awk '{print $1}'` files"

	echo "checking file sizes..."
	for f in `cat $s1`; do
		b=$(basename "$f")
		pd=$(basename $(dirname "$f"))
		fs=$(du -k "$f" | awk '{print $1}')
		echo "$pd|$b|$fs|$f" >> "$s2"
		echo -n "."
	done

	echo
	echo "sorting file list..."
	sort -o "$s2"{,}
}


exit

for i in `find "$dest_dir" -type f -iname '*.HEIC' -exec realpath {} ';'`; do du "$i"; done | sort -n > "$work_dir/01b_dest_sorted_heic.txt"

# Now we need to figure out how to compare these two lists
# Well let's run the script first and see the lists

echo "done"
