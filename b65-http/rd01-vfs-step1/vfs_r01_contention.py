"""SEC-01 VFS-R01 — contention N/W sans panne et sans modification du wrapper.

Barrières Python hors SQLite : le premier écrivain conserve BEGIN IMMEDIATE
jusqu'au refus vérifié d'un second écrivain. Puis COMMIT ou ROLLBACK normal.
Chaque scénario dispose de deux bases et deux connexions dédiées.
"""
import ctypes
import ctypes.util
import json
import platform
import sqlite3
import subprocess
import tempfile
import threading
from pathlib import Path
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
SCENARIOS = ("COMMIT", "ROLLBACK")
TIMEOUT = 8


def _uri(path, wrapped):
    value = "file:" + quote(str(path)) + "?mode=rwc"
    if wrapped:
        value += "&vfs=atlas_rd01_observer"
    return value


def _open(folder, wrapped, create=False):
    db = sqlite3.connect(_uri(folder / "sessions.sqlite", wrapped), uri=True,
                         timeout=0, isolation_level=None)
    try:
        db.execute("PRAGMA busy_timeout=0")
        db.execute("ATTACH DATABASE ? AS idb", (str(folder / "identities.sqlite"),))
        if create:
            for alias in ("main", "idb"):
                db.execute("PRAGMA " + alias + ".journal_mode=DELETE")
                db.execute("PRAGMA " + alias + ".synchronous=FULL")
        modes = [db.execute("PRAGMA " + alias + ".journal_mode").fetchone()[0]
                 for alias in ("main", "idb")]
        sync = [db.execute("PRAGMA " + alias + ".synchronous").fetchone()[0]
                for alias in ("main", "idb")]
        if modes != ["delete", "delete"] or sync != [2, 2]:
            raise AssertionError("DELETE/FULL requis : " + str((modes, sync)))
        return db
    except BaseException:
        db.close()
        raise


def _state(folder, wrapped):
    db = _open(folder, wrapped)
    try:
        return {
            "session": db.execute("SELECT id,revoked FROM sessions").fetchall(),
            "journey": db.execute("SELECT id,label FROM idb.journeys").fetchall(),
            "integrity": [db.execute("PRAGMA " + alias + ".integrity_check").fetchone()[0]
                          for alias in ("main", "idb")],
        }
    finally:
        db.close()


def _scenario(folder, wrapped, resolution):
    folder.mkdir(parents=True)
    setup = _open(folder, wrapped, create=True)
    try:
        setup.execute("CREATE TABLE sessions(id TEXT PRIMARY KEY, revoked INTEGER)")
        setup.execute("CREATE TABLE idb.journeys(id TEXT PRIMARY KEY,label TEXT)")
        setup.execute("INSERT INTO sessions VALUES('fictive-session',0)")
        setup.execute("INSERT INTO idb.journeys VALUES('fictive-journey','initial')")
    finally:
        setup.close()

    holder_acquired = threading.Event()
    contender_blocked = threading.Event()
    release_holder = threading.Event()
    holder_finished = threading.Event()
    allow_second = threading.Event()
    errors = []
    observations = {}

    def holder():
        db = None
        try:
            db = _open(folder, wrapped)
            db.execute("BEGIN IMMEDIATE")
            db.execute("UPDATE sessions SET revoked=1 WHERE id='fictive-session'")
            db.execute("UPDATE idb.journeys SET label='holder' WHERE id='fictive-journey'")
            holder_acquired.set()
            if not release_holder.wait(TIMEOUT):
                raise TimeoutError("barrière holder")
            if resolution == "COMMIT":
                db.execute("COMMIT")
            else:
                db.execute("ROLLBACK")
            observations["holder_resolution"] = resolution
        except BaseException as exc:
            errors.append("holder: " + repr(exc))
            if db is not None and db.in_transaction:
                db.rollback()
        finally:
            if db is not None:
                db.close()
            holder_finished.set()

    def contender():
        db = None
        try:
            if not holder_acquired.wait(TIMEOUT):
                raise TimeoutError("premier verrou non établi")
            db = _open(folder, wrapped)
            try:
                db.execute("BEGIN IMMEDIATE")
            except sqlite3.OperationalError as exc:
                observations["busy_code"] = getattr(exc, "sqlite_errorcode", None)
                observations["busy_name"] = getattr(exc, "sqlite_errorname", None)
                observations["busy_message"] = str(exc)
            else:
                db.execute("ROLLBACK")
                raise AssertionError("second écrivain accepté pendant BEGIN IMMEDIATE")
            contender_blocked.set()
            if not allow_second.wait(TIMEOUT):
                raise TimeoutError("barrière second passage")
            db.execute("BEGIN IMMEDIATE")
            db.execute("UPDATE sessions SET revoked=2 WHERE id='fictive-session'")
            db.execute("UPDATE idb.journeys SET label='contender' WHERE id='fictive-journey'")
            db.execute("COMMIT")
            observations["retry"] = "COMMIT"
        except BaseException as exc:
            errors.append("contender: " + repr(exc))
            if db is not None and db.in_transaction:
                db.rollback()
        finally:
            contender_blocked.set()
            if db is not None:
                db.close()

    t1 = threading.Thread(target=holder, name="rd01-holder")
    t2 = threading.Thread(target=contender, name="rd01-contender")
    t1.start(); t2.start()
    try:
        if not holder_acquired.wait(TIMEOUT):
            raise AssertionError("BEGIN IMMEDIATE du holder non confirmé")
        if not contender_blocked.wait(TIMEOUT):
            raise AssertionError("preuve SQLite BUSY absente")
        if observations.get("busy_code") != sqlite3.SQLITE_BUSY:
            raise AssertionError("refus attendu SQLITE_BUSY : " + repr(observations))
        release_holder.set()
        if not holder_finished.wait(TIMEOUT):
            raise AssertionError("résolution normale du holder absente")
        intermediate = _state(folder, wrapped)
        observations["intermediate"] = intermediate
        expected_mid = ([( "fictive-session", 1)], [("fictive-journey", "holder")]) if resolution == "COMMIT" else (
            [("fictive-session", 0)], [("fictive-journey", "initial")])
        if intermediate["session"] != expected_mid[0] or intermediate["journey"] != expected_mid[1]:
            raise AssertionError("état après holder inattendu : " + repr(intermediate))
        allow_second.set()
    finally:
        release_holder.set()
        allow_second.set()
        t1.join(TIMEOUT); t2.join(TIMEOUT)
    if t1.is_alive() or t2.is_alive():
        raise AssertionError("threads non terminés proprement")
    if errors:
        raise AssertionError("erreurs thread : " + "; ".join(errors))
    final = _state(folder, wrapped)
    expected = {"session": [("fictive-session", 2)],
                "journey": [("fictive-journey", "contender")], "integrity": ["ok", "ok"]}
    if final != expected:
        raise AssertionError("invariants finaux : " + repr(final))
    leftover = sorted(p.name for p in folder.iterdir()
                      if p.name.endswith(("-journal", "-wal", "-shm")) or "-mj" in p.name)
    if leftover:
        raise AssertionError("journaux résiduels : " + repr(leftover))
    return {"busy_code": observations["busy_code"],
            "busy_name": observations["busy_name"],
            "holder_resolution": observations["holder_resolution"],
            "retry": observations["retry"],
            "intermediate": observations["intermediate"],
            "final": final,
            "journal_mode": ["delete", "delete"],
            "synchronous": [2, 2],
            "remaining_journals": leftover}


def compare_contention():
    with tempfile.TemporaryDirectory(prefix="atlas-vfs-r01-locks-") as tmp:
        root = Path(tmp)
        compiled = root / "observer.so"
        compile_result = subprocess.run(
            ["cc", "-std=c11", "-shared", "-fPIC", "-Wall", "-Wextra",
             "-o", str(compiled), str(HERE / "atlas_rd01_vfs.c"), "-lsqlite3"],
            capture_output=True, text=True)
        if compile_result.returncode:
            raise RuntimeError("compilation : " + compile_result.stderr)
        obs = ctypes.CDLL(str(compiled))
        obs.atlas_rd01_register.argtypes = [ctypes.c_char_p]
        obs.atlas_rd01_register.restype = ctypes.c_int
        obs.atlas_rd01_sqlite_version.restype = ctypes.c_char_p
        obs.atlas_rd01_sqlite_symbol.restype = ctypes.c_void_p
        lib = ctypes.CDLL(ctypes.util.find_library("sqlite3"))
        lib.sqlite3_vfs_find.argtypes = [ctypes.c_char_p]
        lib.sqlite3_vfs_find.restype = ctypes.c_void_p
        same = (obs.atlas_rd01_sqlite_version().decode() == sqlite3.sqlite_version and
                obs.atlas_rd01_sqlite_symbol() ==
                ctypes.cast(lib.sqlite3_vfs_find, ctypes.c_void_p).value)
        if not same:
            raise AssertionError("moteur SQLite ou symbole divergent")
        if obs.atlas_rd01_register(str(root / "events.tsv").encode()) != 0:
            raise AssertionError("enregistrement VFS")
        cases = {}
        for resolution in SCENARIOS:
            n = _scenario(root / ("N-" + resolution), False, resolution)
            w = _scenario(root / ("W-" + resolution), True, resolution)
            if n != w:
                raise AssertionError("N/W non comparables pour " + resolution + ": " +
                                     json.dumps({"N": n, "W": w}))
            cases[resolution] = {"N": n, "W": w, "functional_parity": True}
        raw = (root / "events.tsv").read_text(encoding="utf-8")
        events = [line.split("\t") for line in raw.splitlines()]
        count_sync = sum(len(e) == 7 and e[2] == "xSync" and e[4] == "0" for e in events)
        if count_sync <= 0:
            raise AssertionError("aucun retour xSync réussi enregistré par W")
        return {
            "environment": {"python_sqlite": sqlite3.sqlite_version,
                            "system": platform.platform(), "same_library_symbol": same},
            "cases": cases, "W_successful_xSync_logged": count_sync,
            "not_measured": ["séquence d'I/O native N", "durabilité physique",
                             "neutralité temporelle", "chemin _persistent_journey",
                             "équivalence générale VFS V2/V3"],
            "scope": "deux connexions, barrières Python, COMMIT/ROLLBACK normaux, aucune panne"
        }


if __name__ == "__main__":
    print(json.dumps(compare_contention(), indent=2, ensure_ascii=False))
