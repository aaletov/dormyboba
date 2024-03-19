# dormyboba
Dormitory registration and mailing system

## Installation

Multidict requires gcc-11 to compile. Use `MULTIDICT_NO_EXTENSIONS` to use raw python version.

```
export MULTIDICT_NO_EXTENSIONS=1
poetry install
```

## Local Development

Необходимо указать переменную среды `CONFIG_DIR`, соответствующий директории, в которой
лежат конфиги

```bash
CONFIG_DIR=./config poetry run python3 -m dormyboba
```

### Coverage:

```bash
poetry run pytest --cov=dormyboba --cov-report term-missing
```
cool
