#!/bin/bash

if [[ $# == 0 ]] || [[ $# > 2 ]]; then
    echo "usage: $0 <output folder> [<tail>]"
    echo "this script copies all(*) of your iphone voice memos into a folder naming them by date & title"
    echo "(*) or only last <tail> (#) of memos"
    exit 1
fi

output_folder="$1"

tmp_file="/tmp/voice-memos-$RANDOM"
sep=";"

sqlite3 -separator "$sep" "$HOME/Library/Application Support/com.apple.voicememos/Recordings/CloudRecordings.db" "select ZPATH, ZCUSTOMLABEL from ZCLOUDRECORDING order by ZPATH;" > "$tmp_file"

if [[ $# == 2 ]]; then
    echo "$(tail -$2 $tmp_file)" > $tmp_file
fi

IFS=$'\n'
for line in `cat "$tmp_file"`; do
    IFS="$sep" read -r -a memo <<< "$line"  # /Users/amirbaer/Library/Application Support/com.apple.voicememos/Recordings/20211230 183846-EEAF5AE7.m4a:::birthday conversation/discussion
    path="${memo[0]}"   # /Users/amirbaer/Library/Application Support/com.apple.voicememos/Recordings/20211230 183846-EEAF5AE7.m4a
    name="${memo[@]: -1:1}"   # birthday conversation/discussion
    name="${name//\//-}"   # replace slash: birthday conversation-discussion

    filename="`basename "$path"`" # "20211230 183846-EEAF5AE7.m4a"
    IFS=" " read -r -a filename_arr <<< "$filename"
    date="${filename_arr[0]}"   # "20211230"
    id_ext="${filename_arr[1]}"     # "183846-EEAF5AE7.m4a"
    ext="${id_ext##*.}"

    new_name="${date:0:4}-${date:4:2}-${date:6:2} $name.$ext"   # 2021-12-30 birthday conversation.mp4
    cp "$path" "$output_folder/$new_name"
    echo -n "."

done

echo
echo "done."

