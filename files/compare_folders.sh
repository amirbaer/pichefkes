#!/bin/bash

#TODO: since this script only creates the index list, there's not really a point in always running it on two directories at a time
# I think I might change the interface and logic to run on one dir at a time

if [[ $# < 2 ]]; then
	echo "usage: $0 <dir> <output file> [<extension=HEIC>]"
	echo
	echo "the script reads all the files with a certain extension in a folder,"
	echo "checks each file's size and writes the output to a '|'-separated file"
	exit 1
fi

dir="$1"
output_file="$2"
extension="${3-HEIC}"

work_dir="/tmp/cf-$RANDOM"
mkdir "$work_dir"
echo "work dir: $work_dir"

IFS=$'\n'

s1="$work_dir/01_source_$extension.txt"
s2="$work_dir/02_source_sorted_sized_$extension.txt"

process_dir () {
	id="$1"
	of1="$2"
	of2="$3"
	category="$4"

	echo -n "reading $category dir [$id]... "
	find "$id" -type f -iname "*.$extension" -exec realpath {} ';' > "$of1"
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
	echo -n "sorting file list... "
	sort -o "$of2"{,}
	echo "done"
}

process_dir "$dir" "$s1" "$s2" "source"
cp "$s2" "$output_file"

# Now we need to figure out how to compare these two lists

echo
echo "all done, output files:"
find "$work_dir" -type f -exec realpath {} ';' | sort -n
