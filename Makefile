# (C) 2016 Jean Nassar. Some Rights Reserved
# Except where otherwise noted, this work is licensed under the Creative Commons Attribution-ShareAlike License, version 4
MASTER = mshtsy_thesis
FILES = appendices.tex frontmatter.tex introduction.tex mainmatter.tex 
TEX = xelatex

# target: all - Default target. Run XeLaTeX once, and display PDF.
all: show

# target: help - Display callable targets.
help:
	egrep "^# target:" [Mm]akefile

$(MASTER).pdf: $(MASTER).tex $(FILES)
	$(TEX) $(MASTER)

show:: $(MASTER).pdf
	evince $(MASTER).pdf

refs:: glossary.tex $(MASTER).bib
	makeglossaries $(MASTER)
	biber $(MASTER)
	$(TEX) $(MASTER)
	$(TEX) $(MASTER)

remake:: clean
	make refs

full:: remake
	make show

clean::
	rm -f *.{acn,acr,alg,aux,glg,glo,gls,ist,lof,lot,log,nav,out,snm,toc,gz}
