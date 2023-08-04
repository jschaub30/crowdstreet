.PHONY: test

help :
	@echo "-------------------------------------------------------"
	@echo "Look in README.md for general information              "
	@echo "-------------------------------------------------------"
	@echo "test            ... run unit tests                     "
	@echo "                    (run after git commit and push)    "
	@echo "clean           ... cleanup python cache files         "
	@echo
	@echo "help	           ... print this message                 "
	@echo "-------------------------------------------------------"

test:
	-coverage run -m pytest test/ | tee coverage.log
	coverage report -m | tee -a coverage.log

docs:
	pydoc crowdstreet.Portfolio > doc/Portfolio.txt
	pydoc crowdstreet.Transaction > doc/Transaction.txt

clean:
	rm -rf `find . -name .cache`
	rm -rf `find . -name .pytest_cache`
	rm -rf `find . -name __pycache__`
