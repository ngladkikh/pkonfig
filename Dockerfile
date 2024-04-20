ARG VERSION
FROM python:$VERSION-slim

RUN pip install pytest

COPY . .

RUN pip install .[yaml]

CMD python3 -m pytest -q tests
