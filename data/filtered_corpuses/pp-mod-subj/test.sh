#!/bin/bash

array[0]=01234567890abcdefgh
array[1]=blah

# echo ${array[1]}

echo $0
echo $1

echo ${@}

for s in ${@}
do
    echo now at: $s
done
