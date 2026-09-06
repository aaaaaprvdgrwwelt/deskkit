import sqlite3

from deskkit.backup import backup_database


def test_backup_database_copies_data(tmp_path):
    source = sqlite3.connect(str(tmp_path / "source.sqlite"))
    source.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, title TEXT)")
    source.execute("INSERT INTO items (title) VALUES ('Hello')")
    source.commit()

    destination = tmp_path / "backup" / "copy.sqlite"
    backup_database(source, destination)

    assert destination.exists()
    check = sqlite3.connect(str(destination))
    rows = check.execute("SELECT title FROM items").fetchall()
    assert rows == [("Hello",)]
    check.close()


def test_backup_database_creates_missing_parent_dirs(tmp_path):
    source = sqlite3.connect(str(tmp_path / "source.sqlite"))
    source.execute("CREATE TABLE t (x INTEGER)")
    source.commit()

    destination = tmp_path / "a" / "b" / "c" / "backup.sqlite"
    backup_database(source, destination)
    assert destination.exists()


def test_backup_database_source_remains_usable_after_backup(tmp_path):
    # Die Verbindung der laufenden App darf durch das Backup nicht
    # beeintraechtigt werden - die App soll normal weiterlaufen.
    source = sqlite3.connect(str(tmp_path / "source.sqlite"))
    source.execute("CREATE TABLE items (id INTEGER PRIMARY KEY)")
    source.commit()

    backup_database(source, tmp_path / "backup.sqlite")

    source.execute("INSERT INTO items DEFAULT VALUES")
    source.commit()
    assert source.execute("SELECT COUNT(*) FROM items").fetchone()[0] == 1
