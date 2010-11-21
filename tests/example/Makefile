.PHONY : all clean tex pdf view

all: tex pdf

tex: example.tex

pdf: example.pdf

view: example.pdf
	evince example.pdf

example.tex: example.txt Makefile
	../../code/wiki2beamer example.txt > example.tex
	
example.pdf: example.tex Makefile
	pdflatex example.tex

clean:
	rm example.aux example.log example.nav example.out example.pdf example.snm example.tex example.toc example.vrb
