#!/bin/bash


#-- Functions --#

# Exiftool extractors
function _exiftool_extract_date_original() { i=$(</dev/stdin); echo "$i" | grep 'Date/Time Original' | awk '{print $4}' | tr ':' '-' | tr -d "Z" ; }
function _exiftool_extract_date_media() { i=$(</dev/stdin); echo "$i" | grep 'Media Create Date' | awk '{print $5}' | tr ':' '-' | tr -d "Z" ; }
function _exiftool_extract_datetime_original() { i=$(</dev/stdin); echo "$i" | grep 'Date/Time Original' | awk '{print $4,$5}' | tr ':' '-' | tr -d "Z" | sed 's/ /--/g' ; }
function _exiftool_extract_datetime_media() { i=$(</dev/stdin); echo "$i" | grep 'Media Create Date' | awk '{print $5,$6}' | tr ':' '-' | tr -d "Z" | sed 's/ /--/g' ; }

# Date extraction
function audio-get-creation-date-original() { exiftool "$1" | _exiftool_extract_date_original ; }
function audio-get-creation-date-media() { exiftool "$1" | _exiftool_extract_date_media ; }
function audio-get-creation-date() { et=$(exiftool "$1"); res=$(echo "$et" | _exiftool_extract_date_original); if [[ -z "$res" ]]; then res=$(echo "$et" | _exiftool_extract_date_media); fi; echo $res ; }

# Datetime extraction
function audio-get-creation-datetime-original() { exiftool "$1" | _exiftool_extract_datetime_original ; }
function audio-get-creation-datetime-media() { exiftool "$1" | _exiftool_extract_datetime_media ; }
function audio-get-creation-datetime() { et=$(exiftool "$1"); res=$(echo "$et" | _exiftool_extract_datetime_original); if [[ -z "$res" ]]; then res=$(echo "$et" | _exiftool_extract_datetime_media); fi; echo $res ; }

# Convert date based on timezone
function date-math() { date -v "${1}H" -j -f "%Y-%m-%d--%H-%M-%S" "$2" +"%Y-%m-%d--%H-%M-%S" ; } # +2 2021-01-04--14-52-18 -> 2021-01-04--16-52-18
function date-convert-tz() { date=`echo "${1:0:20}"`; tz=`echo "${1:20:3}"`; date-math $tz "$date" ; } # 2021-01-04--14-52-18+02:00 -> 2021-01-04--16-52-18

# Set title in metadata
function audio-set-title-from-filename-noext () { exiftool -q -overwrite_original_in_place '-Title<${Filename;s/\.[^.]*$//}' -ext m4a "$1" ; }



#-- Usage --#

if [[ $# == 0 ]] || [[ $# > 2 ]]; then
    echo "usage: $0 <output folder> [<tail>]"
    echo "this script copies all(*) of your iphone voice memos into a folder naming them by date & title"
    echo "(*) or only last <tail> (#) of memos"
	echo
	echo "CONFIGURATION"
	echo '$VM_TZ - automatically convert UTC dates with no explicit timezone; example values: +2, -3 [default: no]'
	echo '$VM_TZ_SUFFIX - add a timezone suffix to datetime strings; value is disregarded, just needs to have some value'
    exit 1
fi



#-- Main --#

echo "Run configuration:"
echo "VM_TZ= `if ! [ -z $VM_TZ ]; then echo echo $VM_TZ; else echo no; fi`"
echo "VM_TZ_SUFFIX=`if ! [ -z ${VM_TZ_SUFFIX} ]; then echo yes; else echo no; fi`"
echo

output_folder="$1"

tmp_file="/tmp/voice-memos-$RANDOM"
sep=";"


# Read recording entries from DB
sqlite3 -separator "$sep" "$HOME/Library/Application Support/com.apple.voicememos/Recordings/CloudRecordings.db" "select ZPATH, ZEVICTIONDATE, ZCUSTOMLABEL from ZCLOUDRECORDING order by ZPATH;" > "$tmp_file"

# Tail
if [[ $# == 2 ]]; then
    echo "$(tail -$2 $tmp_file)" > $tmp_file
fi

# Iterate recording entries
IFS=$'\n'
for line in `cat "$tmp_file"`; do

	# Parse results
    IFS="$sep" read -r -a memo <<< "$line"  # /Users/amirbaer/Library/Application Support/com.apple.voicememos/Recordings/20211230 183846-EEAF5AE7.m4a:::birthday conversation/discussion
    path="${memo[0]}"   # /Users/amirbaer/Library/Application Support/com.apple.voicememos/Recordings/20211230 183846-EEAF5AE7.m4a
    deleted_date="${memo[1]}"   # 689583291.009771 [or empty if not deleted]
    name="${memo[@]: -1:1}"   # birthday conversation/discussion
    name="${name//\//-}"   # replace slash: birthday conversation-discussion

	# Deleted recording -> skip
	if ! [[ -z "$deleted_date" ]]; then
		echo -n "x"
		continue
	fi


	#-- Handle datetime

	datetime=$(audio-get-creation-datetime "$path")
	tz_suffix="${datetime:20:3}"
	
	# Date contains timezone -> parse & convert
	if ! [[ -z "${tz_suffix}" ]]; then # has a +02 timezone suffix
		processed_datetime=`date-convert-tz "$datetime"`;
		tz_suffix="_UTC$tz_suffix"

	# No timezone -> add suffix to indicate UTC
	else
		# If this variable is set
		if ! [ -z ${VM_TZ} ]; then
			processed_datetime=`date-math $VM_TZ $datetime`;
			tz_suffix="_UTC$VM_TZ"
		else
			processed_datetime="${datetime}";
			tz_suffix="_UTC"
		fi
	fi

	# Add timezone suffix
	if ! [ -z ${VM_TZ_SUFFIX} ]; then
		processed_datetime="${processed_datetime}${tz_suffix}";
	fi


	#-- Extract extension

    filename="`basename "$path"`" # "20211230 183846-EEAF5AE7.m4a"
    IFS=" " read -r -a filename_arr <<< "$filename"
    id_ext="${filename_arr[1]}"     # "183846-EEAF5AE7.m4a"
    ext="${id_ext##*.}"


	#-- Final copy & rename

    new_name="${processed_datetime} $name.$ext"   # 2021-12-30--14-52-13 birthday conversation.mp4
    cp "$path" "$output_folder/$new_name"
	audio-set-title-from-filename-noext "$output_folder/$new_name"
    echo -n "."

done

echo
echo "done."

