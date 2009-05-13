build: beamer advanced graphics version0_4

beamer:
	@python ../wiki2beamer.py wiki2beamer.txt > wiki2beamer.tex && \
	echo "Running pdflatex" && \
	pdflatex beamer.tex && \
	pdflatex beamer.tex && \
	echo "Now, take a look at beamer.pdf"

advanced:
	@python ../wiki2beamer.py wiki_advanced.txt > wiki_advanced.tex && \
	echo "Running pdflatex" && \
	pdflatex advanced.tex && \
	pdflatex advanced.tex && \
	echo "Now, take a look at advanced.pdf"

graphics:
	@python ../wiki2beamer.py wiki_graphics.txt > wiki_graphics.tex && \
	echo "Running pdflatex" && \
	pdflatex graphics.tex && \
	pdflatex graphics.tex && \
	echo "Now, take a look at graphics.pdf"

version0_4:
	@python ../wiki2beamer.py wiki_version0_4.txt > wiki_version0_4.tex && \
	echo "Running pdflatex" && \
	pdflatex version0_4.tex && \
	pdflatex version0_4.tex && \
	echo "Now, take a look at version0_4.pdf"




clean:
	rm -f beamer.aux beamer.log beamer.snm beamer.toc beamer.out beamer.nav beamer.pdf wiki2beamer.tex beamer.vrb && \
	rm -f graphics.aux graphics.log graphics.snm graphics.toc graphics.out graphics.nav graphics.pdf graphics.vrb wiki_graphics.tex && \
	rm -f advanced.aux advanced.log advanced.snm advanced.toc advanced.out advanced.nav advanced.pdf wiki_advanced.tex && \
	rm -f version0_4.aux version0_4.log version0_4.snm version0_4.toc version0_4.out version0_4.nav version0_4.pdf version0_4.vrb wiki_version0_4.tex
