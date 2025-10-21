# Development environment

* >= Python 3.10

## How to create development venv

```shell
cd fuzzy-systems/

python3 -m venv .venv

.venv/Scripts/Activate.ps1 # Windows
.venv/bin/activate         # Linux

pip install -r requirements.txt
```

## Adding new dependencies

In Activated development Environment run:

```shell
pip install <package-name>

pip freeze > requirements.txt

# push new dependencies to repo with git
```

## How to run development env

```shell
python -m src.ui.ui_app
```
