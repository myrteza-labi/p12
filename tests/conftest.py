# tests/conftest.py

import os
import sys

# Ajouter la racine du projet au PYTHONPATH
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root not in sys.path:
    sys.path.insert(0, root)
