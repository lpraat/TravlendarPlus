import os
import sys
sys.path.append(os.path.abspath("src"))  # adds src to PYTHONPATH

from src import setup_logging, create_app

setup_logging()
app = create_app()

if __name__ == '__main__':
    app.run()
