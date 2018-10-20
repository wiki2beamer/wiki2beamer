all: man html

man1:
	mkdir man1

man:  wiki2beamer.xml man1
	@asciidoctor -b manpage wiki2beamer.adoc
	@bzip2 --keep --stdout wiki2beamer.1 > man1/wiki2beamer.1.bz2
	@man -D -M '.' wiki2beamer

html: wiki2beamer.xml wiki2beamer.1
	asciidoctor -b html5 wiki2beamer.adoc

clean:
	rm wiki2beamer.1
	rm wiki2beamer.html
	rm man1/wiki2beamer.1.bz2
	rmdir man1/

