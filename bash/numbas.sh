#!/bin/bash

echo "Please enter a number: "
read num

# if > 0
if [ $num -gt 0 ]; then
  echo "$num is positive"

# if < 0
elif [ $num -lt 0 ]; then
  echo "$num is negative"
else
  echo "$num is zero"
fi