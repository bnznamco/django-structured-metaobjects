clean:
	@find . -name "*.pyc" | xargs rm -rf
	@find . -name "*.pyo" | xargs rm -rf
	@find . -name "__pycache__" -type d | xargs rm -rf

test: clean
	@flake8 structured_metaobjects
	@pytest --cov=structured_metaobjects -s -vv --cov-report=xml --cov-report=term-missing
