#!/bin/bash

autopkg repo-list | while read R
do
	echo "$R" | cut -d '(' -f 2| cut -d ')' -f 1
done

exit 0
