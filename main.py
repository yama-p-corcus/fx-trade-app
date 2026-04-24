from pathlib import Path
import sys

from PyQt6.QtWidgets import QApplication

from src.database.connection import initialize_database
from src.ui.main_window import MainWindow


def main() -> int:
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "data"
    images_dir = data_dir / "images"
    data_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)

    db_path = data_dir / "trades.db"
    initialize_database(db_path)

    app = QApplication(sys.argv)
    window = MainWindow(db_path=db_path, images_dir=images_dir)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
