"""SEC-01 RD01. Banc isole : SIGKILL sur processus enfant uniquement.
Ne simule ni coupure secteur, ni crash OS, ni sous-etape interne COMMIT.
"""
import json
import os
import platform
import signal
import sqlite3
import subprocess
import sys
import tempfile
import time
from pathlib import Path

PHASES = ("before_begin", "after_begin", "after_first_update",
          "after_second_update", "after_commit")
REPEATS = 3


def connection(path):
    return sqlite3.connect(str(path), timeout=8, isolation_level=None)


def initialize(folder):
    a, b = folder / "session_fixture.sqlite", folder / "journey_fixture.sqlite"
    with connection(a) as db:
        db.execute("PRAGMA journal_mode=DELETE")
        db.execute("PRAGMA synchronous=FULL")
        db.execute("CREATE TABLE sessions (id TEXT PRIMARY KEY, revoked INTEGER NOT NULL)")
        db.execute("INSERT INTO sessions VALUES ('fictive-session',0)")
    with connection(b) as db:
        db.execute("PRAGMA journal_mode=DELETE")
        db.execute("PRAGMA synchronous=FULL")
        db.execute("CREATE TABLE journeys (id TEXT PRIMARY KEY, transaction_id TEXT NOT NULL)")
    return a, b


def signal_phase(proof, phase):
    # Evidence outside SQLite; fsync alters scheduling. Not an internal COMMIT hook.
    with open(proof, "w", encoding="utf-8") as stream:
        json.dump({"phase": phase, "pid": os.getpid()}, stream)
        stream.flush()
        os.fsync(stream.fileno())
    while True:
        time.sleep(1)


def child(folder, phase, proof):
    a, b = folder / "session_fixture.sqlite", folder / "journey_fixture.sqlite"
    with connection(a) as db:
        db.execute("ATTACH DATABASE ? AS aux", (str(b),))
        if phase == "before_begin":
            signal_phase(proof, phase)
        db.execute("BEGIN IMMEDIATE")
        if phase == "after_begin":
            signal_phase(proof, phase)
        db.execute("UPDATE sessions SET revoked=1 WHERE id='fictive-session'")
        if phase == "after_first_update":
            signal_phase(proof, phase)
        db.execute("INSERT INTO aux.journeys VALUES ('fictive-journey','fictive-transaction')")
        if phase == "after_second_update":
            signal_phase(proof, phase)
        db.execute("COMMIT")
        if phase == "after_commit":
            signal_phase(proof, phase)
    raise AssertionError("Phase unreachable")


def inspect(folder):
    a, b = folder / "session_fixture.sqlite", folder / "journey_fixture.sqlite"
    with connection(a) as db:
        mode_a = db.execute("PRAGMA journal_mode").fetchone()[0]
        sync_a = db.execute("PRAGMA synchronous").fetchone()[0]
        integrity_a = db.execute("PRAGMA integrity_check").fetchone()[0]
        sessions = db.execute("SELECT id,revoked FROM sessions ORDER BY id").fetchall()
    with connection(b) as db:
        mode_b = db.execute("PRAGMA journal_mode").fetchone()[0]
        sync_b = db.execute("PRAGMA synchronous").fetchone()[0]
        integrity_b = db.execute("PRAGMA integrity_check").fetchone()[0]
        journeys = db.execute("SELECT id,transaction_id FROM journeys ORDER BY id").fetchall()
    before = sessions == [("fictive-session", 0)] and not journeys
    after = sessions == [("fictive-session", 1)] and journeys == [("fictive-journey", "fictive-transaction")]
    return {"journal_mode": [mode_a, mode_b], "synchronous": [sync_a, sync_b],
            "integrity_check": [integrity_a, integrity_b],
            "sessions": sessions, "journeys": journeys,
            "etat": "AVANT" if before else "APRES" if after else "PARTIEL_OU_INATTENDU"}


def experiment(repeats=REPEATS):
    if os.name != "posix" or not hasattr(signal, "SIGKILL"):
        raise RuntimeError("Only POSIX process isolation supported")
    environment = {
        "os": platform.platform(), "python": sys.version.split()[0],
        "sqlite": sqlite3.sqlite_version, "points_instrumentes": list(PHASES),
        "repetitions_par_point": repeats,
        "fenetres_non_qualifiees": ["entree_interne_COMMIT", "journalisation_interne",
                                   "synchronisation_interne", "finalisation_interne_COMMIT"]}
    cases = []
    for phase in PHASES:
        for iteration in range(1, repeats + 1):
            with tempfile.TemporaryDirectory(prefix="atlas-rd01-") as directory:
                folder = Path(directory)
                a, b = initialize(folder)
                if a.stat().st_dev != b.stat().st_dev:
                    raise RuntimeError("Databases are not on the same filesystem")
                proof = folder / "phase-marker.json"
                proc = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--child",
                                         str(folder), phase, str(proof)],
                                        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
                try:
                    deadline = time.monotonic() + 12
                    while not proof.is_file():
                        if proc.poll() is not None:
                            raise RuntimeError("Child exit before marker: " + proc.stderr.read())
                        if time.monotonic() >= deadline:
                            raise TimeoutError("Marker missing at " + phase)
                        time.sleep(.01)
                    reached = json.loads(proof.read_text())
                    if reached != {"phase": phase, "pid": proc.pid}:
                        raise AssertionError("Invalid phase marker")
                    proc.kill()
                    code = proc.wait(timeout=8)
                    if code != -signal.SIGKILL:
                        raise AssertionError("Unexpected child exit " + str(code))
                    state = inspect(folder)
                    expected = "APRES" if phase == "after_commit" else "AVANT"
                    compliant = (state["etat"] == expected and
                                 state["integrity_check"] == ["ok", "ok"] and
                                 state["journal_mode"] == ["delete", "delete"] and
                                 state["synchronous"] == [2, 2])
                    record = {"phase": phase, "repetition": iteration,
                              "phase_prouvee": reached["phase"],
                              "signal": "SIGKILL", "exit_code": code,
                              "expected": expected, "compliant": compliant, **state}
                    cases.append(record)
                    if not compliant:
                        raise AssertionError(json.dumps(record))
                finally:
                    if proc.poll() is None:
                        proc.kill()
                        proc.wait(timeout=8)
    return {"environment": environment, "cases": cases, "total": len(cases),
            "passed": sum(x["compliant"] for x in cases),
            "limits": "Child SIGKILL at external checkpoints only. No internal COMMIT crash injection."}


if __name__ == "__main__":
    if len(sys.argv) == 5 and sys.argv[1] == "--child":
        child(Path(sys.argv[2]), sys.argv[3], Path(sys.argv[4]))
    elif len(sys.argv) == 1:
        print(json.dumps(experiment(), ensure_ascii=False, indent=2))
    else:
        raise SystemExit("Usage: python3 rd01_crash_bench.py")
