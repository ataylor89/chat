from pathlib import Path

project_root = Path(__file__).parent.parent.parent
config_path = project_root / 'config' / 'server' / 'settings.ini'
max_connections = 1000
