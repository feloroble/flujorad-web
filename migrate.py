import os
from playhouse.migrate import MySQLMigrator, migrate
from importlib import import_module
from database import db
import sys

# Obtener la ruta absoluta de la carpeta de modelos
model_dir = os.path.abspath("models")

# Agregar la ruta de la carpeta de modelos al sys.path
sys.path.insert(0, model_dir)

# Realizar las importaciones de los modelos
new_models = []
print("Cargando modelos desde:", model_dir)


for file in os.listdir(model_dir):
    if file.endswith(".py") and file != "base.py":
        module_name = os.path.splitext(file)[0]
        module = import_module(f"models.{module_name}")
        for attribute_name in dir(module):
            attribute = getattr(module, attribute_name)
            # Verificar si es una subclase de BaseModel
            if hasattr(attribute, "_meta") and hasattr(attribute._meta, 'database') and attribute._meta.database == db:
                new_models.append(attribute)

print("Los modelos son:", new_models)
# Realizar migraciones
with db:
    migrator = MySQLMigrator(db)
    for model in new_models:
        migrator.add_model(model)

    migrate(*migrator._operations)
