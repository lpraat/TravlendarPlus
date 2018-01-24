import os
import sys

sys.path.append(os.path.abspath("src"))

from src import create_app, setup_logging


setup_logging()
app = create_app()


if __name__ == '__main__':
    app.run()
