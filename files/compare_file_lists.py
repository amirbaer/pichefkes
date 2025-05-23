#!/usr/bin/env python3

from __future__ import annotations

import random
import os
import sys

from dataclasses import dataclass
from typing import List, Union, Callable


COMP_CONFIG = {
    "replace_fn_func": (lambda fn: fn.replace("_HEVC.MOV", ".MP4")),
    "keys": ("rfilename", "size", "uuid"),
}

SUBFOLDERS = ("live",)

@dataclass
class File:
    filename: str
    parent_folder: str
    full_path: str
    size: int
    uuid: str

    def __post_init__(self):
        self.rfilename = COMP_CONFIG["replace_fn_func"](self.filename)
        bn = os.path.basename
        dn = os.path.dirname
        if self.parent_folder in SUBFOLDERS:
            self.parent_folder = os.path.join(bn(dn(dn(self.full_path))), bn(dn(self.full_path)))

    def __eq__(self, other) -> bool:
        return self.__key() == other.__key()

    def __key(self):
        keys = COMP_CONFIG["keys"]
        return (
                "filename" in keys and self.filename,
                "rfilename" in keys and self.rfilename,
                "size" in keys and self.size,
                "uuid" in keys and self.uuid
            )

    def __hash__(self):
        return hash(self.__key())

@dataclass
class FileSet:
    files: List[File]

    def __len__(self):
        return len(self.files)

    def append(self, file: File):
        self.files.append(file)

    def diff_by(self, dest: FileSet, name=False, rname=False, size=False, uuid=False) -> FileSet:
        COMP_CONFIG["keys"] = {
            name and "filename",
            rname and "rfilename",
            size and "size",
            uuid and "uuid",
        }
        source_set = set(self.files)
        dest_set = set(dest.files)

        source_but_not_dest = FileSet(source_set - dest_set)
        dest_but_not_source = FileSet(dest_set - source_set)
        intersection = FileSet(source_set.intersection(dest_set))

        return (source_but_not_dest, intersection, dest_but_not_source)
        

class FileIndex:
    def __init__(self, list_fn: str, sep="|"):
        self.list_fn = list_fn
        self.sep = sep

        self._index(self._parse_file_list(list_fn, sep))

    def _parse_file_list(self, list_fn, sep="|"):
        file_list = []
        for line in open(list_fn).readlines():
            parent_folder, filename, size, uuid, full_path = line.split(sep)
            file_list.append(File(filename, parent_folder, full_path.strip(), int(size), uuid))
        return file_list

    def _index(self, file_list: List[File]):
        self.file_list = file_list

        self.path_to_files = {}
        self.name_to_paths = {}
        self.rname_to_paths = {}
        self.pfolder_to_paths = {}

        # Create various indexes
        for file in self.file_list:

            # By path [assuming unique]
            self.path_to_files[file.full_path] = file

            # By name
            self.name_to_paths.setdefault(file.filename, [])
            self.name_to_paths[file.filename].append(file.full_path)

            # By replaced name
            self.rname_to_paths.setdefault(file.rfilename, [])
            self.rname_to_paths[file.rfilename].append(file.full_path)

            # By parent folder
            self.pfolder_to_paths.setdefault(file.parent_folder, [])
            self.pfolder_to_paths[file.parent_folder].append(file.full_path)

    def _file_or_attr(self, file_or_attr, attr_name):
        attr = file_or_attr
        if isinstance(file_or_attr, File):
            attr = getattr(file_or_attr, attr_name)
        return attr
    
    def _fileset_by_key(self, index, key) -> FileSet:
        paths = index[key]
        return FileSet(list(filter(None, [self.path_to_files.get(path) for path in paths])))

    def by_path(self, file_or_path: Union[File, str]) -> File:
        path = self._file_or_attr(file_or_path, "full_path")
        return self.path_to_files.get(path)

    def by_name(self, file_or_name: Union[File, str]) -> FileSet:
        name = self._file_or_attr(file_or_name, "filename")
        return self._fileset_by_key(self.name_to_paths, name)

    def by_rname(self, file_or_rname: Union[File, str]) -> FileSet:
        rname = self._file_or_attr(file_or_rname, "rfilename")
        return self._fileset_by_key(self.rname_to_paths, rname)

    def by_parent_folder(self, file_or_pfolder: Union[File, str]) -> FileSet:
        pfolder = self._file_or_attr(file_or_pfolder, "parent_folder")
        return self._fileset_by_key(self.pfolder_to_paths, pfolder)

    def get_parent_folders(self):
        return set(self.pfolder_to_paths.keys())


class FileIndexComparator:
    def __init__(self, source_fn, dest_fn):
        self.source = FileIndex(source_fn)
        self.dest = FileIndex(dest_fn)

    def compare_indexes(self):
        source_pfs = self.source.get_parent_folders()
        dest_pfs = self.dest.get_parent_folders()

        print(f"source parent folders: {len(source_pfs)}")
        print(f"dest parent folders: {len(dest_pfs)}")

        missing_pfs_dest = source_pfs - dest_pfs
        missing_pfs_source = dest_pfs - source_pfs
        if missing_pfs_dest:
            print(f"missing in dest: {', '.join(sorted(missing_pfs_dest))}")
        if missing_pfs_source:
            print(f"missing in source: {', '.join(sorted(missing_pfs_source))}")
        
        print("------------------------------")

        shared_pfs = source_pfs.intersection(dest_pfs)

        action_commands = []
        print(f"analyzing {len(shared_pfs)} shared folders...")
        for pf in sorted(shared_pfs):
            action_commands += self.compare_by_parent_folder(pf)

        return action_commands

    def compare_by_parent_folder(self, pf):
        source_fs = self.source.by_parent_folder(pf)
        dest_fs = self.dest.by_parent_folder(pf)

        #self.compare_file_sets_by_name(source_fs, dest_fs)
        action_commands, log = self.compare_file_sets_by_size_and_uuid(source_fs, dest_fs)

        if action_commands or log:
            print(f"\n-- [ {pf} | source: {len(source_fs)} files | dest: {len(dest_fs)}) files ] --")
            print(log)

        return action_commands

    def compare_file_sets_by_name(self, source: FileSet, dest: FileSet):
        COMP_CONFIG["keys"] = ("rfilename",)
        source_only, both, dest_only = source.diff_by(dest, rname=True)

        if source_only or dest_only:
            print(f"comparison by name | source only: {len(source_only)} | shared: {len(both)} | dest only: {len(dest_only)}")
            print(" -> source only:\n%s" % '\n'.join(sorted(map(lambda f: f.filename, source_only.files))))
            print(" -> dest only:\n%s" % '\n'.join(sorted(map(lambda f: f.filename, dest_only.files))))

    def compare_file_sets_by_size_and_uuid(self, source: FileSet, dest: FileSet):
        COMP_CONFIG["keys"] = ("size", "uuid")
        source_only, both, dest_only = source.diff_by(dest, rname=True)

        log = ""
        action_commands = []


        # missing in each side
        if source_only or dest_only:
            log += f"comparison by size & UUID | source only: {len(source_only)} | shared: {len(both)} | dest only: {len(dest_only)}\n"
            if source_only:
                log += " -> source only:\n%s\n" % '\n'.join(sorted(map(lambda f: f.filename, source_only.files)))
            if dest_only:
                log += " -> dest only:\n%s\n" % '\n'.join(sorted(map(lambda f: f.filename, dest_only.files)))

            # action items for source-only files
            dest_pf = os.path.dirname(dest.files[0].full_path)
            for sf in sorted(source_only.files, key=lambda f: f.full_path):

                # XXX: rfilename or filename
                dest_path = os.path.join(dest_pf, sf.rfilename)
                df = self.dest.by_path(dest_path)
                if df and sf.size < df.size:
                    action_commands.append(f'echo source file smaller than dest file # cp -v "{sf.full_path}" "{dest_path}"')
                else:
                    cmd = f'cp -v "{sf.full_path}" "{dest_path}"'
                    cmd = f'read -p "{sf.full_path}: are you sure? " -n 1 -r; echo; if [[ $REPLY =~ ^[Yy]$ ]]; then {cmd}; fi' # confirm
                    action_commands.append(cmd)

                """
                print(f"source // name: {sf.filename} | rname: {sf.rfilename} | size: {sf.size} | UUID: {sf.uuid}", end="")
                if df:
                    print(f" || dest // name: {df.filename} | rname: {df.rfilename} | size: {df.size} | UUID: {df.uuid}")
                else:
                    print()
                """

        return action_commands, log

#------------

def main(source_fn, dest_fn):
    comparator = FileIndexComparator(source_fn, dest_fn)
    action_commands = comparator.compare_indexes()

    if action_commands:
        output_fn = f"/tmp/action-commands-{random.randrange(10000)}.sh"
        open(output_fn, 'w').write("\n".join(action_commands))
        print("\naction commands:", output_fn)

#------------

if __name__ == "__main__":

    if len(sys.argv) != 3:
        print(f"usage: {sys.argv[0]} <source file list> <dest file list>")
        print()
        print("the script uses two file lists generated by 'compare_folders.sh' to figure out which files are different or missing")
        sys.exit(1)

    source_file_list = sys.argv[1]
    dest_file_list = sys.argv[2]

    main(source_file_list, dest_file_list)


