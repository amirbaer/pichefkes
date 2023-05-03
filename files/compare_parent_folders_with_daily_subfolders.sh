#!/bin/bash

usage() {
  echo "Usage: $0 <parent_folder1> <parent_folder2>"
  exit 1
}

if [ "$#" -ne 2 ]; then
  usage
fi

parent_folder1="$1"
parent_folder2="$2"

if [[ ! -d "$parent_folder1" || ! -d "$parent_folder2" ]]; then
  echo "Error: Both arguments must be valid directories."
  usage
fi

index1=1
index2=2

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
NC='\033[0m' # No Color

echo "Comparing folders in $parent_folder1 (Index $index1) and $parent_folder2 (Index $index2)"

for folder1 in "$parent_folder1"/*; do
  if [[ -d "$folder1" && "$(basename "$folder1")" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2} ]]; then
    folder2="$parent_folder2/$(basename "$folder1")"

	bf1="$(basename "$folder1")"
	pf2="$(basename "$parent_folder2")"
    
    if [[ -d "$folder2" ]]; then
      num_files1=$(find "$folder1" -type f | wc -l)
      num_files2=$(find "$folder2" -type f | wc -l)
      
      size1=$(du -s "$folder1" | awk '{print $1}')
      size2=$(du -s "$folder2" | awk '{print $1}')

      if [[ "$num_files1" -ge "$num_files2" && "$size1" -gt "$size2" ]]; then
        index1_color=$GREEN
        index2_color=$RED
      elif [[ "$num_files1" -le "$num_files2" && "$size1" -lt "$size2" ]]; then
        index1_color=$RED
        index2_color=$GREEN
      else
        index1_color=$YELLOW
        index2_color=$YELLOW
      fi

      # Color code file parameters
      num_files_color1=$RED
      num_files_color2=$GREEN
      size_color1=$RED
      size_color2=$GREEN

      if [[ "$num_files1" -gt "$num_files2" ]]; then
        num_files_color1=$GREEN
        num_files_color2=$RED
      elif [[ "$num_files1" -eq "$num_files2" ]]; then
        num_files_color1=$YELLOW
        num_files_color2=$YELLOW
      fi

      if [[ "$size1" -gt "$size2" ]]; then
        size_color1=$GREEN
        size_color2=$RED
      elif [[ "$size1" -eq "$size2" ]]; then
        size_color1=$NC
        size_color2=$NC
      fi

	  printf "Comparing folders [$BLUE%s$NC]: ${index1_color}%d${NC} | ${index2_color}%d${NC} | Number of files: ${num_files_color1}%d${NC} vs ${num_files_color2}%d${NC} | Size: ${size_color1}%d${NC} vs ${size_color2}%d${NC}\n" \
			 "$bf1" "$index1" "$index2" "$num_files1" "$num_files2" "$size1" "$size2"

    else
      printf "No match for ${BLUE}%s${NC} in ${BLUE}%s${NC}\n" \
      	"${bf1%% *}" "${pf2}"
    fi
  fi
done

