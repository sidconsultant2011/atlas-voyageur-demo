"""AC-08 : préconditions SQLite pour fixtures locales fictives uniquement."""
import sqlite3
from pathlib import Path
from urllib.parse import quote


class SQLitePreconditionError(RuntimeError):
    """Connexion non admissible ; ne révèle ni chemin ni identifiant."""


def _disk_path(path):
    if not isinstance(path, (str, Path)) or str(path) == ":memory:" or str(path).startswith("file:"):
        raise SQLitePreconditionError("AC08_INVALID_DISK_PATH")
    target = Path(path).expanduser().resolve(strict=False)
    if target.is_symlink() or (target.exists() and not target.is_file()):
        raise SQLitePreconditionError("AC08_INVALID_DISK_PATH")
    return target


def _mode(connection, schema):
    return str(connection.execute("PRAGMA " + schema + ".journal_mode").fetchone()[0]).lower()


def _full(connection, schema):
    connection.execute("PRAGMA " + schema + ".synchronous=FULL")
    if connection.execute("PRAGMA " + schema + ".synchronous").fetchone() != (2,):
        raise SQLitePreconditionError("AC08_SYNCHRONOUS_NOT_FULL")


def open_qa_database(path, *, initialize=False, foreign_keys=False):
    """Nouvelle fixture: configuration hors transaction; existante: lecture sans conversion.

    Une base disparue après initialisation est refusée et jamais recréée.
    """
    target = _disk_path(path)
    existed = target.is_file()
    if not existed and not initialize:
        raise SQLitePreconditionError("AC08_DATABASE_MISSING")
    if not target.parent.is_dir():
        raise SQLitePreconditionError("AC08_PARENT_MISSING")
    # mode=rw garantit qu'aucune base existante manquante ne sera recréée.
    uri = "file:" + quote(str(target), safe="/") + "?mode=" + ("rw" if existed else "rwc")
    connection = sqlite3.connect(uri, uri=True, timeout=10)
    try:
        mode = _mode(connection, "main")
        if existed:
            if mode != "delete":
                raise SQLitePreconditionError("AC08_JOURNAL_INCOMPATIBLE")
        else:
            result = connection.execute("PRAGMA main.journal_mode=DELETE").fetchone()
            if not result or str(result[0]).lower() != "delete":
                raise SQLitePreconditionError("AC08_JOURNAL_INCOMPATIBLE")
        if _mode(connection, "main") != "delete":
            raise SQLitePreconditionError("AC08_JOURNAL_INCOMPATIBLE")
        _full(connection, "main")
        if foreign_keys:
            connection.execute("PRAGMA foreign_keys=ON")
            if connection.execute("PRAGMA foreign_keys").fetchone() != (1,):
                raise SQLitePreconditionError("AC08_FOREIGN_KEYS_OFF")
        return connection
    except BaseException:
        connection.close()
        raise


def verify_attached(connection, main_path, identity_path):
    """Appeler immédiatement après ATTACH, impérativement avant BEGIN IMMEDIATE."""
    main, attached = _disk_path(main_path), _disk_path(identity_path)
    if not main.is_file() or not attached.is_file() or main == attached:
        raise SQLitePreconditionError("AC08_ATTACHMENT_MISSING")
    names = {name: Path(file).resolve(strict=False)
             for _, name, file in connection.execute("PRAGMA database_list").fetchall()
             if name in ("main", "identity_db")}
    if names != {"main": main, "identity_db": attached}:
        raise SQLitePreconditionError("AC08_ATTACHMENT_MISMATCH")
    if main.stat().st_dev != attached.stat().st_dev:
        raise SQLitePreconditionError("AC08_STORAGE_MISMATCH")
    for schema in ("main", "identity_db"):
        if _mode(connection, schema) != "delete":
            raise SQLitePreconditionError("AC08_JOURNAL_INCOMPATIBLE")
        _full(connection, schema)
