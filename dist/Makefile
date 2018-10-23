.PHONY: debian clean zip man example

VERSIONNR=0.10.0
ZIPSUBDIR=./zip/
VERSIONDIR=wiki2beamer-$(VERSIONNR)

ZIPDISTDIR=$(ZIPSUBDIR)$(VERSIONDIR)

zip:	man example
	mkdir -p $(ZIPDISTDIR)
	mkdir -p $(ZIPDISTDIR)/code
	mkdir -p $(ZIPDISTDIR)/doc/man
	mkdir -p $(ZIPDISTDIR)/doc/example
	cp ../ChangeLog $(ZIPDISTDIR)
	cp ../LICENSE $(ZIPDISTDIR)
	cp ../README $(ZIPDISTDIR)
	cp ../code/wiki2beamer $(ZIPDISTDIR)/code/
	cp ../code/setup.py $(ZIPDISTDIR)/code/
	cp ../doc/fdl.txt $(ZIPDISTDIR)/doc/
	cp ../doc/man/Makefile $(ZIPDISTDIR)/doc/man/
	cp ../doc/man/wiki2beamer.xml $(ZIPDISTDIR)/doc/man/
	cp ../doc/man/wiki2beamer.html $(ZIPDISTDIR)/doc/man/
	cp ../doc/man/wiki2beamer.1 $(ZIPDISTDIR)/doc/man/
	cp ../tests/example/Makefile $(ZIPDISTDIR)/doc/example/
	cp ../tests/example/db-rg1024.png $(ZIPDISTDIR)/doc/example/
	cp ../tests/example/example.txt $(ZIPDISTDIR)/doc/example/
	cp ../tests/example/includefile.txt $(ZIPDISTDIR)/doc/example/
	cp ../tests/example/example.pdf $(ZIPDISTDIR)/doc/example/
	cd $(ZIPSUBDIR) && zip -r $(VERSIONDIR).zip $(VERSIONDIR)/
man:
	$(MAKE) -C ../doc/man/

example:
	$(MAKE) -C ../tests/example/

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
	rm -Rf $(ZIPSUBDIR)

