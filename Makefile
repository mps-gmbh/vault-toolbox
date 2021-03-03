env-test: test-requirements.txt
	virtualenv env-test --python=$(which python3)
	env-test/bin/pip install -r test-requirements.txt  
	touch env-test

clean:
	rm -rf env-build/
	rm -rf env-test/

install:
	pip install --editable .

test-requirements: test-requirements.txt
test-requirements.txt: test-requirements.in
	pip-compile test-requirements.in
