#!/bin/bash

##### COMMANDLINE ARGUMENTS ########

if [[ $# != 6 ]]; then
	echo "num args: $#"
	echo "args: $*"
	echo
	echo "usage: $0 <host> <user> <keychain-pw-key> <kechain> <mount-point> <folders>"
	echo
	echo "folders should be separated by ';'"
	exit 1
fi

SYN_HN="$1"
SYN_USER="$2"
SYN_PW_KEY="$3"
SYN_PW_KEYCHAIN="$4"
SYN_MP="$5"
FOLDERS="$6"

##### SINGLETON ########

LOCKFILE=/tmp/mntsyn.lock
if [ -e ${LOCKFILE} ] && kill -0 `cat ${LOCKFILE}`; then
    echo "already running"
    exit
fi

# make sure the lockfile is removed when we exit and then claim it
trap "rm -f ${LOCKFILE}; exit" INT TERM EXIT
echo $$ > ${LOCKFILE}


##### MAIN ########
echo "starting..."


# security add-generic-password -a USER -p 'PASSWORD' -s SYN_PW_KEY
# for SMB mounts password can also be saved in ~/Library/Preferences/nsmb.conf
# (https://serverfault.com/questions/367950/secure-way-to-mount-a-password-protected-cifs-share-in-mac)
SYN_PW="$(security find-generic-password -s $SYN_PW_KEY -w $SYN_PW_KEYCHAIN)"

for folder in `echo $FOLDERS | tr ';' ' '`; do
    echo -n "working on '$folder': "
    # match on mount point, so shares mounted under any hostname (Sasson, Sasson.local, IP) are detected
    if ! /sbin/mount | grep -qF " on $SYN_MP/$folder ("; then
        mkdir -p "$SYN_MP/$folder"
        #/sbin/mount -t afp -o browse,nosuid,nodev "afp://$SYN_USER:$SYN_PW@$SYN_HN.local/$folder" "$SYN_MP/$folder"
        if /sbin/mount -t smbfs "smb://$SYN_USER:$SYN_PW@$SYN_HN/$folder" "$SYN_MP/$folder"; then
            echo "mounted"
        else
            echo "failed"
        fi
    else
        echo "already mounted"
    fi
done

echo "done"

##### DONE ########


rm -f ${LOCKFILE}

