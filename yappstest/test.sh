#!/bin/bash

rm w2b.py w2b.pyc

yapps2 w2b.g w2b.py

python w2b_test.py document test_complex.txt
