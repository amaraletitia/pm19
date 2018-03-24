
all:
	@(cd sipgen; $(MAKE))
	@(cd siplib; $(MAKE))

install:
	@(cd sipgen; $(MAKE) install)
	@(cd siplib; $(MAKE) install)
	@test -d $(DESTDIR)/Users/GYUNAM/.pyenv/versions/3.4.5/lib/python3.4/site-packages || mkdir -p $(DESTDIR)/Users/GYUNAM/.pyenv/versions/3.4.5/lib/python3.4/site-packages
	cp -f sipconfig.py $(DESTDIR)/Users/GYUNAM/.pyenv/versions/3.4.5/lib/python3.4/site-packages/sipconfig.py
	cp -f /Users/GYUNAM/Documents/PyProM/library/sip-4.19.8/sip-4.19.8/sipdistutils.py $(DESTDIR)/Users/GYUNAM/.pyenv/versions/3.4.5/lib/python3.4/site-packages/sipdistutils.py

clean:
	@(cd sipgen; $(MAKE) clean)
	@(cd siplib; $(MAKE) clean)
