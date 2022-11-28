#!/usr/local/bin/python3

import random
import subprocess
import os
import shutil
import sys

import PIL.Image

def add_date_to_filename(phile, dest_folder):
    if "IMG_" in phile or "DSC" in phile:
        img = PIL.Image.open(phile)
        if img and img._getexif():
            img_date = img._getexif().get(36867, "unknown").replace(':','-').replace(' ','_')
            return os.path.join(dest_folder, "%s_%s" % (img_date, os.path.basename(phile)))

    return dest_folder

def main(src_folder, dest_folder, index_file, num_files_to_copy, bl_exts, prob_del):
    if not os.path.exists(src_folder):
        print("Source folder ('%s') not found" % src_folder)
        sys.exit(1)

    if not os.path.exists(dest_folder):
        print("Destination folder ('%s') not found" % dest_folder)
        sys.exit(1)

    # Get list of files from index or by running `find`
    files = []
    if os.path.exists(index_file):
        print('found index file: %s' % index_file)
        for path in open(index_file, 'r').readlines():
            if "." in os.path.basename(path):
                item = os.path.join(src_folder, path).strip()
                files.append(item)
        print('%s files found' % len(files))
    else:
        print("running 'find'...")
        files = subprocess.getoutput("find %s -iname '*.jpg' -or -iname '*.jpeg'" % src_folder).split('\n')

    # Pick new files
    print("choosing %d new files" % num_files_to_copy, end="", sep="")
    chosen = set()
    for i in range(num_files_to_copy):
        sys.stdout.write(".")
        sys.stdout.flush()

        files = [f for f in files if os.path.basename(f).lower().split(".")[-1] not in bl_exts]

        phile = None
        tries = 0
        while not phile and tries < 100:
            candidate = files[random.randrange(0, len(files))]
            if os.path.isfile(candidate):
                phile = candidate
                chosen.add(phile)
            else:
                tries += 1

        if tries == 100:
            print("error finding photos, is the diskstation connected?")
            sys.exit(1)


    # CAREFULL!!!
    print("\ndeleting old files", end="", sep="")
    num_undeleted = 0
    for the_file in os.listdir(dest_folder):
        file_path = os.path.join(dest_folder, the_file)
        try:
            if os.path.isfile(file_path):
                if random.random() < prob_del:
                    os.unlink(file_path)
                    sys.stdout.write(".")
                else:
                    num_undeleted += 1
                    sys.stdout.write(":")
        except Exception as e:
            print(e)

        sys.stdout.flush()

    num_to_copy = num_files_to_copy - num_undeleted
    print("\ncopying %d new files" % num_to_copy, end="", sep="")
    chosen_list = list(chosen)
    random.shuffle(chosen_list)
    for i in range(num_to_copy):
        phile = chosen_list[i]
        dest = add_date_to_filename(phile, dest_folder)
        shutil.copy2(phile, dest)

        sys.stdout.write(".")
        sys.stdout.flush()

    print("\ndone")

if __name__ == "__main__":
    if len(sys.argv) != 7:
        print("usage: %s <src folder> <dest folder> <index file> <num_files_to_copy> <bl_exts> <probability_del>" % sys.argv[0])
        sys.exit(1)

    src = sys.argv[1]
    dest = sys.argv[2]
    index = sys.argv[3]
    count = int(sys.argv[4])
    bl_exts = sys.argv[5].split(";")
    prob_del = float(sys.argv[6])

    main(src, dest, index, count, bl_exts, prob_del)
