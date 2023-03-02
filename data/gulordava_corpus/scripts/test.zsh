#!/bin/zsh

echo $(dirname $0)
echo $(realpath $(dirname $0))
echo $(realpath $(dirname $0))/../
echo $(realpath $(realpath $(dirname $0))/../)
ls $(realpath $(dirname $0))/../
ls $(realpath $(realpath $(dirname $0))/../)
#MY_PATH=`pwd`/../
#MY_PATH=`dirname $0`/../
#MY_PATH=$(realpath $(dirname $0))
##MY_PATH_ONEUP=$(realpath $MY_PATH/../)
#MY_PATH_ONEUP=$(realpath $(dirname $0))../
#echo "\$0 is $0"
#echo "Path of $0 is $MY_PATH"
#echo "Path one up is $MY_PATH_ONEUP"
#ls $MY_PATH
