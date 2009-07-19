.PHONY: debian debianclean

debian:
	mkdir -p ./debian/usr/bin
	mkdir -p ./debian/usr/share/man/man1
	mkdir -p ./debian/usr/share/doc/wiki2beamer/
	cp -p ../code/wiki2beamer ./debian/usr/bin/
	cp -p ../doc/man/wiki2beamer.1 ./debian/usr/share/man/man1/
	gzip ./debian/usr/share/man/man1/wiki2beamer.1
	cp -Rp ../doc/examples ./debian/usr/share/doc/wiki2beamer/
	fakeroot dpkg-deb --build ./debian/ wiki2beamer_x.x-x_all.deb

clean:	
	rm -Rf ./debian/usr

