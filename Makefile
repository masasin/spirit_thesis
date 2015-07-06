# (C) 2016 Jean Nassar. Some Rights Reserved
# Except where otherwise noted, this work is licensed under the Creative Commons Attribution-ShareAlike License, version 4
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
	rm -f {src/,}*.{aux,log,nav,out,snm,toc,gz}
	#rm -f *.aux *.log *.nav *.out *.snm *.toc *.gz
