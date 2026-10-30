import sys
from pathlib import Path

# Garante resolução do backend, frontend e app em qualquer ambiente de execução de testes
repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))
