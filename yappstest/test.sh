#!/bin/bash

rm w2b.py

yapps2 w2b.g w2b.py

python w2b.py document test.txt
