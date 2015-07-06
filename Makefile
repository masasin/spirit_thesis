MASTER = mshtsy_thesis

all:
	make quick

once:
	xelatex $(MASTER)

show:
	evince $(MASTER).pdf

refs:
	make once
	makeglossaries $(MASTER)
	make once

quick:
	make once
	make show

rerun:
	make clean
	make refs

full:
	make rerun
	make show

clean:
	rm -f *.aux *.log *.nav *.out *.snm *.toc *.gz
