all: man html

man1:
	mkdir man1

man:  wiki2beamer.xml man1
	@docbook2man.pl wiki2beamer.xml
	@bzip2 --keep --stdout wiki2beamer.1 > man1/wiki2beamer.1.bz2
	@man -D -M '.' wiki2beamer

html: wiki2beamer.xml wiki2beamer.1
	man2html wiki2beamer.1 | sed 's/Manpage of wiki2beamer/Manpage of wiki2beamer (man wiki2beamer)/' | sed 's/Content-type: text\/html//' > wiki2beamer.html

clean:
	rm wiki2beamer.1
	rm wiki2beamer.html
	rm man1/wiki2beamer.1.bz2
	rmdir man1/

