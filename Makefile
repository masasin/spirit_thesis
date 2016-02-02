# (C) 2016 Jean Nassar. Some Rights Reserved
# Except where otherwise noted, this work is licensed under the Creative Commons Attribution-ShareAlike License, version 4
MASTER = mshtsy_thesis
COMPILER = xelatex

ifneq (COMPILER, "pdflatex")
TEX = latexmk -pdf -e "$$pdflatex=q/$(COMPILER) %O %S/"
else
TEX = latexmk
endif

# target: all - Default target. Run XeLaTeX once, and display PDF.
all:: show

# target: help - Display callable targets.
help::
	egrep "^# target:" [Mm]akefile

# target: pdf - Make the PDF.
pdf::
	$(TEX) $(MASTER)

# target: show - Show the final PDF.
show:: pdf
	evince $(MASTER).pdf

# target: remake - Clean, then remake PDF. Use when there is an error in the .aux file.
remake:: clean
	make pdf

# target: full - Remake pdf and show.
full:: remake
	make show

# target: clean - Remove generated files.
clean::
	rm -f *.{acn,acr,alg,aux,glg,glo,gls,ist,lof,lot,log,nav,out,snm,toc,gz}
