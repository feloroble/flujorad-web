import os
import importlib
from pathlib import Path

def register_models():
    """
    Importa todos los archivos .py en la carpeta models excepto __init__.py.
    Esto registra automáticamente todos los modelos con SQLAlchemy.
    """
    models_path = Path(__file__).parent
    for file in models_path.glob("*.py"):
        if file.name != "__init__.py":
            module_name = f"app.models.{file.stem}"
            importlib.import_module(module_name)
