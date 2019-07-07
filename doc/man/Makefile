.PHONY: all
all: man html

man1:
	mkdir man1

wiki2beamer.1: wiki2beamer.adoc
	asciidoctor -b manpage -d manpage wiki2beamer.adoc

man1/wiki2beamer.1.bz2: wiki2beamer.1 | man1
	bzip2 --keep --stdout wiki2beamer.1 > man1/wiki2beamer.1.bz2

wiki2beamer.html: wiki2beamer.adoc
	asciidoctor -b html5 -d manpage wiki2beamer.adoc

.PHONY: man
man: man1/wiki2beamer.1.bz2

.PHONY: html
html: wiki2beamer.html

.PHONY: clean
clean:
	rm -f wiki2beamer.1
	rm -f wiki2beamer.html
	rm -f man1/wiki2beamer.1.bz2
	[ ! -d man1 ] || rmdir man1
