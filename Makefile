# (C) 2016 Jean Nassar. Some Rights Reserved
# Except where otherwise noted, this work is licensed under the Creative Commons Attribution-ShareAlike License, version 4
MASTER = mshtsy_thesis
SOURCES = $(MASTER).tex $(wildcard *.tex *.sty *.py) Makefile
FIGURES = $(shell find img/* -type f)

VIEWER = evince

LATEX = xelatex
LATEXOPT = --shell-escape
NONSTOP = --interaction=nonstopmode

LATEXMK = latexmk
LATEXMKOPT = -pdf
CONTINUOUS = -pvc

TEX = $(LATEXMK) $(LATEXMKOPT) -pdflatex="$(LATEX) $(LATEXOPT) $(NONSTOP) %O %S"

# target: all - Default target. Compile, and display PDF.
all:: $(MASTER).pdf
	make show

# target: help - Display callable targets.
help::
	egrep "^# target:" [Mm]akefile

# target: show - Display PDF.
show:: $(MASTER).pdf
	$(VIEWER) $(MASTER).pdf

.refresh:
	touch .refresh

$(MASTER).pdf: $(MASTER).tex .refresh $(SOURCES) $(FIGURES)
	make once

# target: once - Run through compilation once.
once::
	$(TEX) $(MASTER)

# target: force - Force recompilation.
force::
	touch .refresh
	rm $(MASTER).pdf
	make once

# target: remake - Clean, then remake PDF. Use when there is an error in the .aux file.
remake:: cleanall
	make refs

# target: full - Remake pdf and show.
full:: remake
	make show

# target: clean - Remove generated files.
clean::
	# Regular generated files.
	rm -f *.aux *.lof *.lot *.out *.toc *.log *.gz
	# Bibliography
	rm -f $(MASTER)-blx.bib *.bbl *.xdy *.bcf *.blg
	# Glossary
	rm -f *.acn *.acr *.alg # Acronyms
	rm -f *.glg *.glo *.gls # Glossaries
	rm -f *.nlg *.not *.ntn # Notation
	rm -f *.sbl *.slg *.sym # Symbols
	# Other
	rm -f *.ist *.nav *.xml $(MASTER).fdb_latexmk *.fls

# target: cleanall - Remove generated and output files.
cleanall:: clean
	$(LATEXMK) -C $(MASTER)
	rm -f $(MASTER).pdfsync 

# target: refs - Generate the glossaries.
refs:: debug
	makeglossaries $(MASTER)
	biber $(MASTER)
	make debug
	make debug

# target: debug - Run the latex engine once.
debug::
	$(LATEX) $(LATEXOPT) $(MASTER)
