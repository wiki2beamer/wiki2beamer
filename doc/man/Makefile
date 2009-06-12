build:  wiki2beamer.xml
	@docbook2man.pl wiki2beamer.xml
	@bzip2 --keep --stdout wiki2beamer.1 > man1/wiki2beamer.1.bz2
	@man -D -M '.' wiki2beamer
