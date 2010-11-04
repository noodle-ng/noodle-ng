#!/bin/bash
#
# this script starts the crawler and takes care, that not multiple instances are spawned at once
#
crawler="newhcrawler.py"
LCK_FILE="/tmp/noodle_crawler.lck"

cwd=`pwd`
python=`which python`
noodlepath=`dirname $0`

# the lock file routine is provided by Jonathan Franzone 
# (http://www.franzone.com/2007/09/23/how-can-i-tell-if-my-bash-script-is-already-running/)
if [ -f "${LCK_FILE}" ]; then

  # The file exists so read the PID
  # to see if it is still running
  MYPID=`head -n 1 "${LCK_FILE}"`

  TEST_RUNNING=`ps -p ${MYPID} | grep ${MYPID}`

  if [ -z "${TEST_RUNNING}" ]; then
    echo $$ > "${LCK_FILE}"
  else
    echo "`basename $0` is already running [${MYPID}]"
    exit 0
  fi

else
  echo "Not running"
  echo $$ > "${LCK_FILE}"
fi



cd $noodlepath
$python ./$crawler
cd $cwd

rm -f "${LCK_FILE}"
exit 0