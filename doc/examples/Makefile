.PRECIOUS: %.tex

WIKIFILES=$(wildcard *.wiki)

all: $(patsubst %.wiki, %.pdf, $(WIKIFILES))


%.tex: %.wiki
	@echo "Translating $<"
	wiki2beamer $< > $@


%.pdf: %.tex
	@echo "Running pdflatex in $<"
	pdflatex $<
	pdflatex $<


%: %.pdf


proper: clean
	$(RM) *.pdf


clean:
	$(RM) *.aux *.log *.nav *.out *.snm *.toc
	$(RM) $(patsubst %.wiki, %.tex, $(WIKIFILES))
