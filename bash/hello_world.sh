#!/bin/bash

owner=jacob

echo "Today is " `date`

echo -e "enter the path to directory"
read the_path

echo -e "your path has the following files and folders: "
ls $the_path

echo "and the owner is $owner"

echo -e "input the text you wanna see"
read -e
echo -e