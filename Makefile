# (C) 2016 Jean Nassar. Some Rights Reserved
# Except where otherwise noted, this work is licensed under the Creative Commons Attribution-ShareAlike License, version 4
MASTER = mshtsy_thesis

# target: all - Default target. Run XeLaTeX once, and display PDF.
all:
	make quick

# target: help - Display callable targets.
help:
	egrep "^# target:" [Mm]akefile

# target: once - Run XeLaTeX once.
once:
	xelatex $(MASTER)

# target: show - Show the generated PDF.
show:
	evince $(MASTER).pdf

# target: refs - Generate the glossaries, bibliography, and indices.
refs:
	make once
	makeglossaries $(MASTER)
	biber $(MASTER)
	make once
	make once

# target: quick - Run XeLaTeX once, and display PDF.
quick:
	make once
	make show

# target: rerun - Remove generated files, then regenerate the references and PDF.
rerun:
	make clean
	make refs

# target: full - Rerun, then show the PDF.
full:
	make rerun
	make show

# target: clean - Remove all generated files except the PDF.
clean:
	rm -f *.{acn,acr,alg,aux,glg,glo,gls,ist,lof,lot,log,nav,out,snm,toc,gz}
