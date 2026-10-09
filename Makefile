# make site   - render the status site into _site/
# make serve  - render and preview on http://localhost:8000/
.PHONY: site serve clean

site:
	python3 site/build.py

serve: site
	python3 -m http.server -d _site 8000

clean:
	rm -rf _site
