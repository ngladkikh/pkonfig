ARG VERSION
FROM python:$VERSION-slim

RUN pip install pytest mypy types-PyYAML

COPY . .

# Install package with all extras needed by unit tests across Python versions
RUN pip install .[yaml,toml]

CMD sh -c "python3 -m pytest -q tests/unit 2>&1"
