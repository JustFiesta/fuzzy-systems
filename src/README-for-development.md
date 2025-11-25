# Development environment

- `>= Python 3.10`

## How to Run project

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

## How to build executable

```shell
cd src/

pyinstaller --onefile --windowed --name "FuzzyCar" --hidden-import=src.core_fuzzy.fuzzy_controller --hidden-import=src.simulation.car_simulation --hidden-import=numpy --hidden-import=pyqtgraph --hidden-import=PyQt5 --hidden-import=PyQt5.QtCore --hidden-import=PyQt5.QtGui --hidden-import=PyQt5.QtWidgets --add-data "core_fuzzy;core_fuzzy" --add-data "simulation;simulation" --add-data "ui;ui" main.py
```
