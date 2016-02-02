# (C) 2016 Jean Nassar. Some Rights Reserved
# Except where otherwise noted, this work is licensed under the Creative Commons Attribution-ShareAlike License, version 4
MASTER = mshtsy_thesis

# target: all - Default target. Run XeLaTeX once, and display PDF.
all: show

# target: help - Display callable targets.
help:
	egrep "^# target:" [Mm]akefile

# target: pdf - Run XeLaTeX once.
pdf:
	xelatex $(MASTER)

# target: show - Show the generated PDF.
show: $(MASTER).pdf
	evince $(MASTER).pdf

# target: refs - Generate the glossaries, bibliography, and indices.
refs: $(MASTER).pdf
	makeglossaries $(MASTER)
	biber $(MASTER)
	make pdf
	make pdf

# target: remake - Remove generated files, then regenerate the references and PDF.
remake: clean
	make refs

# target: full - Remake, then show the PDF.
full: remake
	make show

# target: clean - Remove all generated files except the PDF.
clean:
	rm -f *.{acn,acr,alg,aux,glg,glo,gls,ist,lof,lot,log,nav,out,snm,toc,gz}
