.PHONY: debian debianclean

debian:
	cp ../code/wiki2beamer ./debian/usr/bin/
	cp ../doc/man/wiki2beamer.1 ./debian/usr/share/man/man1/
	gzip ./debian/usr/share/man/man1/wiki2beamer.1
	cp -R ../doc/examples ./debian/usr/share/doc/wiki2beamer/
	fakeroot dpkg-deb --build ./debian/ wiki2beamer_x.x-x_all.deb

clean:	
	rm ./debian/usr/bin/wiki2beamer
	rm ./debian/usr/share/man/man1/wiki2beamer.1.gz
	rm -Rf ./debian/usr/share/doc/wiki2beamer/examples

