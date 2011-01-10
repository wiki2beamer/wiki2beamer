.PHONY: test clean

test:	w2b.py
	python w2b_test.py test.txt 

w2b.py: Makefile w2b.g
	yapps2 w2b.g w2b.py

clean:
	rm w2b.py
