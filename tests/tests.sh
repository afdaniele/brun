#! /bin/bash

./brun --field x:l:1,2,3 -f y:list:0,1 -f z:range:6 -g zip:x,z -- echo {x}, {y}, {z}
