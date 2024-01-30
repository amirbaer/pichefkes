#!/bin/bash


#-- Constants --#

VOICE_MEMOS_FOLDER="$HOME/Library/Group Containers/group.com.apple.VoiceMemos.shared/Recordings"
VOICE_MEMOS_DB="$VOICE_MEMOS_FOLDER/CloudRecordings.db"
VOICE_MEMOS_SQL_QUERY="select ZPATH, ZEVICTIONDATE, ZENCRYPTEDTITLE from ZCLOUDRECORDING order by ZPATH;"


#-- Functions --#

# Set title in metadata
function audio-set-title-from-filename-noext () { exiftool -q -overwrite_original_in_place '-Title<${Filename;s/\.[^.]*$//}' -ext m4a "$1" ; }


#-- Usage --#

if [[ $# == 0 ]] || [[ $# > 2 ]]; then
    echo "usage: $0 <output folder> [<tail>]"
    echo "this script copies all(*) of your iphone voice memos into a folder naming them by date & title"
    echo "(*) or only last <tail> (#) of memos"
    exit 1
fi


#-- Main --#

output_folder="$1"

tmp_file="/tmp/voice-memos-$RANDOM"
sep="^"


# Read recording entries from DB
sqlite3 -separator "$sep" "$VOICE_MEMOS_DB" "$VOICE_MEMOS_SQL_QUERY" > "$tmp_file"

# Tail
if [[ $# == 2 ]]; then
    echo "$(tail -$2 $tmp_file)" > $tmp_file
fi

# Iterate recording entries
truncated_names=()
IFS=$'\n'
for line in `cat "$tmp_file"`; do

	# Parse results
    IFS="$sep" read -r -a memo <<< "$line"  # /Users/amirbaer/Library/Application Support/com.apple.voicememos/Recordings/20211230 183846-EEAF5AE7.m4a:::birthday conversation/discussion
    filename="${memo[0]}"   # 20211230 183846-EEAF5AE7.m4a
    full_path="$VOICE_MEMOS_FOLDER/$filename"   # /Users/amirbaer/Library/Application Support/com.apple.voicememos/Recordings/20211230 183846-EEAF5AE7.m4a
    deleted_date="${memo[1]}"   # 689583291.009771 [or empty if not deleted]
    name="${memo[@]: -1:1}"   # birthday conversation/discussion
    name="${name//\//-}"   # replace slash: birthday conversation-discussion

	# Deleted recording -> skip
	if ! [[ -z "$deleted_date" ]]; then
		echo -n "x"
		continue
	fi

	#-- Handle datetime

    rdatetime="${filename:0:15}"
    formatted_datetime="${rdatetime:0:4}-${rdatetime:4:2}-${rdatetime:6:2}--${rdatetime:9:2}-${rdatetime:11:2}-${rdatetime:13}"


	#-- Extract extension

    IFS=" " read -r -a filename_arr <<< "$filename"
    id_ext="${filename_arr[1]}"     # "183846-EEAF5AE7.m4a"
    ext="${id_ext##*.}"


	#-- Final copy & rename

	# truncate names which are too long (macos limits file names to 255 characters)
	is_truncated=false
	if [[ ${#name} -ge 200 ]]; then
		truncated+=("${formatted_datetime} $name")
		name="${name:0:200}..."
		is_truncated=true
	fi

    new_name="${formatted_datetime} $name.$ext"   # 2021-12-30--14-52-13 birthday conversation.mp4
    cp "$full_path" "$output_folder/$new_name"
	audio-set-title-from-filename-noext "$output_folder/$new_name"

	if ! $is_truncated; then
		echo -n "."
	else
		echo -n "t"
	fi

done

if [[ ${#truncated[@]} -gt 0 ]]; then
	echo
	echo
	echo "truncated names:"
    for item in "${truncated[@]}"; do
        echo "$item" >> "$output_folder/truncated.txt"
    done
	cat "$output_folder/truncated.txt"
fi


echo
echo "done."

