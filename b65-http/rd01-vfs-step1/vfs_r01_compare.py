"""VFS-R01 : comparaison N/W non destructive, même moteur, SQL et PRAGMA.
Le témoin natif ne possède pas de trace VFS comparable : marquer non mesuré.
"""
import ctypes
import ctypes.util
import json
from pathlib import Path
import platform
import sqlite3
import subprocess
import tempfile
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
SQL = (
    "CREATE TABLE sessions (id TEXT PRIMARY KEY, revoked INTEGER)",
    "INSERT INTO sessions VALUES ('fixture-session',0)",
    "CREATE TABLE idb.journeys (id TEXT PRIMARY KEY,label TEXT)",
    "UPDATE sessions SET revoked=1 WHERE id='fixture-session'",
    "INSERT INTO idb.journeys VALUES ('fixture-journey','fake')",
)


def specimen(folder, wrapped):
    a, b = folder / "sessions.sqlite", folder / "identities.sqlite"
    uri = "file:" + quote(str(a)) + "?mode=rwc"
    if wrapped:
        uri += "&vfs=atlas_rd01_observer"
    conn = sqlite3.connect(uri, uri=True, timeout=5)
    phases = []
    try:
        for statement in (
            "PRAGMA main.journal_mode=DELETE",
            "PRAGMA main.synchronous=FULL",
        ):
            conn.execute(statement)
        conn.execute(SQL[0]); conn.execute(SQL[1]); conn.commit()
        conn.execute("ATTACH DATABASE ? AS idb", (str(b),))
        conn.execute("PRAGMA idb.journal_mode=DELETE")
        conn.execute("PRAGMA idb.synchronous=FULL")
        conn.execute(SQL[2]); conn.commit()
        config = {
            "sqlite": sqlite3.sqlite_version,
            "database_list": sorted((name, Path(path).name) for _, name, path
                                    in conn.execute("PRAGMA database_list") if name != "temp"),
            "journal_mode": [conn.execute("PRAGMA main.journal_mode").fetchone()[0],
                             conn.execute("PRAGMA idb.journal_mode").fetchone()[0]],
            "synchronous": [conn.execute("PRAGMA main.synchronous").fetchone()[0],
                            conn.execute("PRAGMA idb.synchronous").fetchone()[0]],
            "same_device": a.stat().st_dev == b.stat().st_dev
        }
        conn.execute("BEGIN IMMEDIATE"); phases.append("BEGIN IMMEDIATE")
        conn.execute(SQL[3]); conn.execute(SQL[4])
        conn.commit(); phases.append("COMMIT")
        result = [conn.execute("SELECT id,revoked FROM sessions").fetchall(),
                  conn.execute("SELECT id,label FROM idb.journeys").fetchall()]
        integrity = [conn.execute("PRAGMA main.integrity_check").fetchone()[0],
                     conn.execute("PRAGMA idb.integrity_check").fetchone()[0]]
    finally:
        conn.close()
    residual = sorted(p.name for p in folder.iterdir()
                      if p.name.endswith(("-journal", "-wal", "-shm")) or "-mj" in p.name)
    return {"config": config, "phases": phases, "result": result,
            "integrity": integrity, "remaining_journals": residual}


def compare():
    with tempfile.TemporaryDirectory(prefix="atlas-vfs-r01-") as directory:
        root = Path(directory)
        native, wrapped = root / "N", root / "W"
        native.mkdir(); wrapped.mkdir()
        compiled = root / "observer.so"
        build = subprocess.run(["cc", "-std=c11", "-shared", "-fPIC", "-Wall",
                                "-Wextra", "-o", str(compiled),
                                str(HERE / "atlas_rd01_vfs.c"), "-lsqlite3"],
                               text=True, capture_output=True)
        if build.returncode:
            raise RuntimeError("Compilation du banc impossible : " + build.stderr)
        observer = ctypes.CDLL(str(compiled))
        observer.atlas_rd01_register.argtypes = [ctypes.c_char_p]
        observer.atlas_rd01_register.restype = ctypes.c_int
        observer.atlas_rd01_sqlite_version.restype = ctypes.c_char_p
        observer.atlas_rd01_sqlite_symbol.restype = ctypes.c_void_p
        library = ctypes.CDLL(ctypes.util.find_library("sqlite3"))
        library.sqlite3_vfs_find.argtypes = [ctypes.c_char_p]
        library.sqlite3_vfs_find.restype = ctypes.c_void_p
        same = (observer.atlas_rd01_sqlite_version().decode() == sqlite3.sqlite_version
                and observer.atlas_rd01_sqlite_symbol() ==
                ctypes.cast(library.sqlite3_vfs_find, ctypes.c_void_p).value)
        if not same:
            raise AssertionError("Même bibliothèque SQLite non démontrée")
        if observer.atlas_rd01_register(str(root / "wrapper-events.tsv").encode()) != 0:
            raise AssertionError("Enregistrement VFS impossible")
        n = specimen(native, False)
        w = specimen(wrapped, True)
        differences = [key for key in ("config", "phases", "result", "integrity",
                                      "remaining_journals") if n[key] != w[key]]
        if differences:
            raise AssertionError("Divergence N/W : " + json.dumps(differences))
        if n["config"]["journal_mode"] != ["delete", "delete"] or n["config"]["synchronous"] != [2, 2]:
            raise AssertionError("Paramètres de journalisation non conformes")
        if n["integrity"] != ["ok", "ok"]:
            raise AssertionError("Intégrité SQLite non conforme")
        if n["result"] != [[("fixture-session", 1)], [("fixture-journey", "fake")]]:
            raise AssertionError("Invariants métier non conformes")
        log = (root / "wrapper-events.tsv").read_text(encoding="utf-8")
        events = [line.split("\t")[2] for line in log.splitlines() if len(line.split("\t")) == 7]
        return {
            "environment": {"python_sqlite": sqlite3.sqlite_version, "system": platform.platform(),
                            "same_library_symbol": same},
            "N": n, "W": w, "differences": differences,
            "W_observations": {name: events.count(name)
                               for name in ("xOpen", "xWrite", "xSync", "xDelete", "xFileControl")},
            "non_mesures": ["Parité des appels xSync et xLock événement par événement",
                            "Latence et ordre exacts côté VFS native",
                            "Atomicité après panne et persistance physique",
                            "Equivalence générale V2/V3 et WAL",
                            "Chemin applicatif _persistent_journey()"],
            "scope": "Même transaction fictive, COMMIT normal, aucune panne"
        }


if __name__ == "__main__":
    print(json.dumps(compare(), ensure_ascii=False, indent=2))
