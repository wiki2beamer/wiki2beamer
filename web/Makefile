.PHONY: publish example man

USER=cleeus
PROJECT=wiki2beamer
DSTPATH=/home/groups/w/wi/wiki2beamer/htdocs/
EXAMPLEDIR=../tests/example/
MANDIR=../doc/man/

COMMANDS =put index.html $(DSTPATH) \n
COMMANDS+=put $(EXAMPLEDIR)/example.pdf $(DSTPATH)/wiki2beamer-example.pdf \n
COMMANDS+=put $(MANDIR)/wiki2beamer.html $(DSTPATH)/wiki2beamer.html \n
COMMANDS+=bye

publish: example man
	echo -e "$(COMMANDS)" | sftp -b - $(USER),$(PROJECT)@web.sourceforge.net

example:
	$(MAKE) -C $(EXAMPLEDIR)

man:
	$(MAKE) -C $(MANDIR)
