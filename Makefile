ENV_DIR := venv

setup: virtualenv

tests: virtualenv
	( . ${ENV_DIR}/bin/activate && cd tests && pytest )

format: virtualenv
	( . ${ENV_DIR}/bin/activate && \
		find . -name ${ENV_DIR} -a -type d -prune -o -name '*.py' -print -exec yapf --style='{based_on_style: google, column_limit: 120}' -i {} \; )

lint: virtualenv
	( . ${ENV_DIR}/bin/activate && pylint --rcfile=.pylintrc ptao_service )

virtualenv: ${ENV_DIR}

${ENV_DIR}:
	( virtualenv -p python3 ${ENV_DIR} && . ${ENV_DIR}/bin/activate && pip install -U -r requirements.txt )

clean:
	find . -depth \( -type f -name "*.pyc" -o -type d -name "__pycache__" -o -type d -name ${ENV_DIR} \) -exec rm -rf {} \;

.PHONY: setup tests virtualenv format clean
