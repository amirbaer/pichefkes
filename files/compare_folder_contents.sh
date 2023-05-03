#!/bin/bash

usage() {
  echo "Usage: $0 <folder1> <folder2>"
  exit 1
}

if [ "$#" -ne 2 ]; then
  usage
fi

folder1="$1"
folder2="$2"

if [[ ! -d "$folder1" || ! -d "$folder2" ]]; then
  echo "Error: Both arguments must be valid directories."
  usage
fi

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Temporary files for storing missing files
missing_in_folder1_file="/tmp/missing_in_folder1_$$"
missing_in_folder2_file="/tmp/missing_in_folder2_$$"

# Find missing files
comm -23 <(ls -1 "$folder1" | sort) <(ls -1 "$folder2" | sort) > "$missing_in_folder2_file"
comm -13 <(ls -1 "$folder1" | sort) <(ls -1 "$folder2" | sort) > "$missing_in_folder1_file"

echo "Files missing in $folder1:"
cat "$missing_in_folder1_file"

echo "Files missing in $folder2:"
cat "$missing_in_folder2_file"

# Compare file sizes
for file1 in "$folder1"/*; do
  file2="$folder2/$(basename "$file1")"
  
  if [[ -f "$file1" && -f "$file2" ]]; then
	size1=$(stat -f%z "$file1")
	size2=$(stat -f%z "$file2")

    
    size_color1=$RED
    size_color2=$GREEN

    if [[ "$size1" -gt "$size2" ]]; then
      size_color1=$GREEN
      size_color2=$RED
    elif [[ "$size1" -eq "$size2" ]]; then
      size_color1=$NC
      size_color2=$NC
    fi

    printf "Comparing file sizes: ${size_color1}%s (${size1} bytes)${NC} vs ${size_color2}%s (${size2} bytes)${NC}\n" \
           "$(basename "$file1")" "$(basename "$file2")"
  fi
done

# Cleanup
rm "$missing_in_folder1_file"
rm "$missing_in_folder2_file"

