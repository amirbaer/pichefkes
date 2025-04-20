#!/bin/bash

# Create 'all' directory if it doesn't exist
mkdir -p all

# First, move all top-level files to all/uncategorized
for file in *; do
    # Check if it's a regular file (not a directory)
    if [ -f "$file" ]; then
        # Move and rename the file
        mv "$file" "all/uncategorized--${file}"
    fi
done

# Then handle files in subdirectories
for folder in */; do
    # Remove trailing slash
    folder=${folder%/}
    
    # Skip the 'all' directory
    if [ "$folder" != "all" ]; then
        # Loop through each file in the folder
        for file in "$folder"/*; do
            # Check if it's a file (not another directory)
            if [ -f "$file" ]; then
                # Get just the filename without path
                filename=$(basename "$file")
                
                # Move and rename the file
                mv "$file" "all/${folder}--${filename}"
            fi
        done
    fi
done
