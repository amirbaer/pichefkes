#!/bin/bash


extensions="HEIC;JPG;JPEG;PNG;MOV;MP4;M4A;PNG"
grep_in_filter=""
grep_out_filter=""

if [[ $# < 2 ]]; then
	echo "usage: $0 <dir> <output file> [<extensions=$extensions>] [<grep_in_filter=$grep_in_filter>] [<grep_out_filter=$grep_out_filter>]"
	echo
	echo "the script reads all the files with a certain extension in a folder,"
	echo "checks each file's size and writes the output to a '|'-separated file"
	exit 1
fi

dir="$1"
output_file="$2"
extensions="${3-$extensions}"
grep_in_filter="${4-$grep_in_filter}"
grep_out_filter="${5-$grep_out_filter}"

work_dir="/tmp/cf-$RANDOM"
mkdir "$work_dir"
echo "work dir: $work_dir"

IFS=$'\n'

e=`echo $extensions | tr ';' '_'`
s0="$work_dir/00_run_params.txt"
s1="$work_dir/01_files.txt"
s2="$work_dir/02_files_sorted_sized.txt"

cat > $s0 <<- EOM
input_dir: $dir
output_file: `realpath $output_file`
extensions: $extensions
grep_in_filter: $grep_in_filter
grep_out_filter: $grep_out_filter
EOM

process_dir () {
	id="$1"
	of1="$2"
	of2="$3"
	category="$4"

	echo -n "reading $category dir [$id]... "

	# find
	find_cmd_exe="/tmp/tmp-find-cmd"
	ext_regex="-iname '*`echo $extensions | sed 's/;/'"'"' -or -iname '"'"'*./g'`'"
	echo 'find "'$dir'" -type f \( '$ext_regex' \)' > $find_cmd_exe
	chmod a+x $find_cmd_exe
	files=`$find_cmd_exe` # couldn't get find to run properly otherwise
	echo "found `echo "$files" | wc -l | awk '{print $1}'` files"

	# filter find
	echo -n "filtering files... "
	if [ ! -z $grep_in_filter ]; then files=`echo "$files" | grep "$grep_in_filter"`; fi
	if [ ! -z $grep_out_filter ]; then files=`echo "$files" | grep -v "$grep_out_filter"`; fi
	echo "`echo "$files" | grep -v -e '^$' | wc -l | awk '{print $1}'` files left after filter"

	if [ ! -z "$files" ]; then
		echo "getting real paths... "
		for item in $files; do
			realpath "$item" >> "$of1"
			echo -n "."
		done
		echo
	else
		echo "no files left after filter -> quitting"
		exit
	fi

	echo "gathering file metadata..."
	for f in `cat $of1`; do
		b=$(basename "$f")
		pd=$(basename $(dirname "$f"))
		fs=$(du -k "$f" | awk '{print $1}')
		fco=$(exiftool "$f" | grep 'Content Identifier' | awk '{print $4}') #cut -d ':' -f 2 | tr -d ' ')
		echo "$pd|$b|$fs|$fco|$f" >> "$of2" # NOTE: this directly affects the parsing the complementary python script
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
