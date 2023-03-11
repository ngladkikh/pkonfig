.PHONY fmt:
fmt:
	black . && \
	isort .

.PHONY unit:
unit:
	pytest tests


.PHONY lint:
lint:
	mypy pkonfig && pylint pkonfig

.PHONY check:
check: fmt unit lint