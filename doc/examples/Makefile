build: beamer advanced graphics version0_4 version0_7

beamer:
	@python ../../code/wiki2beamer wiki2beamer.txt > wiki2beamer.tex && \
	echo "Running pdflatex" && \
	pdflatex beamer.tex && \
	pdflatex beamer.tex && \
	echo "Now, take a look at beamer.pdf"

advanced:
	@python ../../code/wiki2beamer wiki_advanced.txt > wiki_advanced.tex && \
	echo "Running pdflatex" && \
	pdflatex advanced.tex && \
	pdflatex advanced.tex && \
	echo "Now, take a look at advanced.pdf"

graphics:
	@python ../../code/wiki2beamer wiki_graphics.txt > wiki_graphics.tex && \
	echo "Running pdflatex" && \
	pdflatex graphics.tex && \
	pdflatex graphics.tex && \
	echo "Now, take a look at graphics.pdf"

version0_4:
	@python ../../code/wiki2beamer wiki_version0_4.txt > wiki_version0_4.tex && \
	echo "Running pdflatex" && \
	pdflatex version0_4.tex && \
	pdflatex version0_4.tex && \
	echo "Now, take a look at version0_4.pdf"

version0_7:
	@python ../../code/wiki2beamer wiki_version0_7.txt > wiki_version0_7.tex && \
	echo "Running pdflatex" && \
	pdflatex wiki_version0_7.tex && \
	pdflatex wiki_version0_7.tex && \
	echo "Now, take a look at wiki_version0_7.pdf"



clean:
	rm -f beamer.aux beamer.log beamer.snm beamer.toc beamer.out beamer.nav beamer.pdf wiki2beamer.tex beamer.vrb && \
	rm -f graphics.aux graphics.log graphics.snm graphics.toc graphics.out graphics.nav graphics.pdf graphics.vrb wiki_graphics.tex && \
	rm -f advanced.aux advanced.log advanced.snm advanced.toc advanced.out advanced.nav advanced.pdf wiki_advanced.tex && \
	rm -f version0_4.aux version0_4.log version0_4.snm version0_4.toc version0_4.out version0_4.nav version0_4.pdf version0_4.vrb wiki_version0_4.tex && \
	rm -f wiki_version0_7.aux wiki_version0_7.log wiki_version0_7.snm wiki_version0_7.toc wiki_version0_7.out wiki_version0_7.nav wiki_version0_7.pdf wiki_version0_7.vrb wiki_version0_7.tex
