ENV_DIR := venv

setup: virtualenv

tests: virtualenv
	( . ${ENV_DIR}/bin/activate && cd tests && pytest )

format: virtualenv
	( . ${ENV_DIR}/bin/activate && \
		yapf --style='{based_on_style: google, column_limit: 120}' -ir apms )

lint: virtualenv
	( . ${ENV_DIR}/bin/activate && pylint --rcfile=.pylintrc apms )

virtualenv: ${ENV_DIR}

${ENV_DIR}:
	( virtualenv -p python3 ${ENV_DIR} && . ${ENV_DIR}/bin/activate && pip install -U -r requirements.txt )

clean:
	find . -depth \( -type f -name "*.pyc" -o -type d -name "__pycache__" -o -type d -name ${ENV_DIR} \) -exec rm -rf {} \;

.PHONY: setup tests virtualenv format clean
