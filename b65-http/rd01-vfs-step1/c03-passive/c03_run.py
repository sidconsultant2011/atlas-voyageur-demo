"""SEC01 C03-3 : certificat réciproque depuis écritures VFS en mémoire.
Aucune lecture de journal vivant, aucune panne, aucun buffer brut publié.
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
MAGIC = bytes.fromhex("d9d505f920a163d7")

def be32(blob):
    return int.from_bytes(blob, "big")

def checksum(name):
    # Somme des octets de la référence UTF-8, vérifiée dans le profil testé.
    return sum(name) & 0xffffffff

def _pointer_offsets(j, supername, page_size):
    """Indices des références complètes, validées à partir des octets observés."""
    data, mask = j["data"], j["mask"]
    offsets = []
    for i in range(4, len(data)-len(supername)-16+1):
        if data[i:i+len(supername)] != supername:
            continue
        start, end = i-4, i+len(supername)+16
        if not all(mask[start:end]):
            continue
        if be32(data[start:i]) != 0x40000000 // page_size + 1:
            continue
        if be32(data[i+len(supername):i+len(supername)+4]) != len(supername):
            continue
        if be32(data[i+len(supername)+4:i+len(supername)+8]) != checksum(supername):
            continue
        if data[i+len(supername)+8:end] != MAGIC:
            continue
        offsets.append(start)
    return offsets


def validate_close_evidence(entry):
    """C03-R03: refuse toute fermeture absente, erronée ou indéterminée."""
    if not entry["closed"] or entry["error"]:
        raise AssertionError("C03-R03: fermeture non attestée")
    # Fixtures synthétiques historiques dépourvues de métadonnées C03-R03.
    if any(key in entry for key in ("close_called", "close_known", "close_rc")):
        if (entry.get("close_called") != 1 or entry.get("close_known") != 1
                or entry.get("close_rc") != sqlite3.SQLITE_OK):
            raise AssertionError("C03-R03: résultat xClose non qualifié")


def reciprocal_certificate(entries, main_path, attached_path, page_size):
    """C03-R01: une incarnation prouvée par journal, sans max(generation)."""
    supers = [r for r in entries if r["kind"] == 2]
    if len(supers) != 1:
        raise AssertionError("C03: super-journal absent ou multiple")
    s = supers[0]
    if not s["deleted"]:
        raise AssertionError("C03: suppression S absente")
    for entry in entries:
        validate_close_evidence(entry)
    if not all(s["mask"]) or not s["data"].endswith(b"\x00"):
        raise AssertionError("C03: lacune dans les écritures de S")
    listed = s["data"][:-1].split(b"\x00")
    if len(listed) != 2 or len(set(listed)) != 2:
        raise AssertionError("C03: liste S ambiguë ou incomplète")
    expected = (str(main_path) + "-journal", str(attached_path) + "-journal")
    if set(listed) != {name.encode() for name in expected}:
        raise AssertionError("C03: S ne liste pas exactement les deux journaux")

    witnesses = []
    for role, name in zip(("A", "B"), expected):
        candidates = [r for r in entries if r["kind"] == 1 and r["path"] == name]
        if not candidates:
            raise AssertionError("C03: journal " + role + " absent")
        jname = name.encode()
        soffsets = [i for i in range(len(s["data"])-len(jname))
                    if s["data"][i:i+len(jname)] == jname and
                    s["data"][i+len(jname)] == 0 and all(s["mask"][i:i+len(jname)+1])]
        if len(soffsets) != 1:
            raise AssertionError("C03: S->" + role + " non unique")

        # Une même référence S dans deux incarnations doit être rejetée.
        matches = [(r, _pointer_offsets(r, s["path"].encode(), page_size))
                   for r in candidates]
        if any(len(offsets) > 1 for _, offsets in matches):
            raise AssertionError("C03: " + role + "->S plusieurs pointeurs")
        proved = [(r, offsets[0]) for r, offsets in matches if len(offsets) == 1]
        if len(proved) != 1:
            raise AssertionError("C03: " + role + "->S absent ou plusieurs incarnations compatibles")
        j, pointer = proved[0]
        if not j["deleted"] or not j["closed"] or j["generation"] >= s["generation"]:
            raise AssertionError("C03: cycle de vie de " + role + " non corroboré")
        # Une incarnation plus récente du même chemin peut remplacer le fichier;
        # une référence dans l'ancienne n'atteste pas la continuité du fichier actuel.
        if any(r["generation"] > j["generation"] for r in candidates):
            raise AssertionError("C03: recréation/remplacement de " + role + " sans continuité")
        witnesses.append({"role": role, "journal_generation": j["generation"],
                          "S_list_offset": soffsets[0], "pointer_offset": pointer,
                          "journal_writes": j["writes"], "journal_truncates": j["truncates"]})
    return {"verdict": "RECONSTRUIT_BANC_FICTIF",
            "links": {"S_to_journals": ["A", "B"], "A_to_S": True, "B_to_S": True},
            "super": {"generation": s["generation"], "writes": s["writes"],
                      "opened_as": "SQLITE_OPEN_MASTER_JOURNAL", "deleted": bool(s["deleted"])},
            "provenance": witnesses}

def validate_deletion_attribution(deletion):
    """Refuse toute suppression sans attribution, sans modifier le retour SQLite."""
    if any(deletion[name] > 0 for name in ("ambiguous", "no_match", "native_errors", "not_closed")):
        raise AssertionError("C03-R02: deletion attribution incomplete: " + repr(deletion))

def run():
    with tempfile.TemporaryDirectory(prefix="atlas-c03-passive-") as directory:
        root = Path(directory)
        library_path = root / "libc03.so"
        result = subprocess.run(
            ["cc", "-std=c11", "-shared", "-fPIC", "-o", str(library_path),
             str(HERE / "c03_vfs.c"), "-lsqlite3"], capture_output=True, text=True)
        if result.returncode:
            raise AssertionError("C03 compiler: " + result.stderr)
        lib = ctypes.CDLL(str(library_path))
        lib.c03_register.restype = ctypes.c_int
        lib.c03_count.restype = ctypes.c_int
        lib.c03_overflow.restype = ctypes.c_int
        lib.c03_info.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int] + [
            ctypes.POINTER(ctypes.c_int)] * 7
        lib.c03_info.restype = ctypes.c_int
        lib.c03_copy.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int]
        lib.c03_copy.restype = ctypes.c_int
        lib.c03_close_info.argtypes = [ctypes.c_int] + [ctypes.POINTER(ctypes.c_int)] * 3
        lib.c03_close_info.restype = ctypes.c_int
        lib.c03_sqlite_version.restype = ctypes.c_char_p
        lib.c03_sqlite_symbol.restype = ctypes.c_void_p
        native = ctypes.CDLL(ctypes.util.find_library("sqlite3"))
        native.sqlite3_vfs_find.restype = ctypes.c_void_p
        same = (lib.c03_sqlite_version().decode() == sqlite3.sqlite_version and
                lib.c03_sqlite_symbol() ==
                ctypes.cast(native.sqlite3_vfs_find, ctypes.c_void_p).value)
        if not same:
            raise AssertionError("C03: SQLite Python et VFS différente")
        if lib.c03_register() != sqlite3.SQLITE_OK:
            raise AssertionError("C03: VFS registration failed")
        main, attached = root / "sessions.sqlite", root / "identities.sqlite"
        uri = "file:" + quote(str(main)) + "?mode=rwc&vfs=atlas_c03_passive"
        with sqlite3.connect(uri, uri=True) as db:
            db.execute("PRAGMA main.journal_mode=DELETE")
            db.execute("PRAGMA main.synchronous=FULL")
            db.execute("CREATE TABLE sessions(id TEXT PRIMARY KEY,revoked INTEGER)")
            db.execute("INSERT INTO sessions VALUES('fake',0)")
            db.commit()
            db.execute("ATTACH DATABASE ? AS idb", (str(attached),))
            db.execute("PRAGMA idb.journal_mode=DELETE")
            db.execute("PRAGMA idb.synchronous=FULL")
            db.execute("CREATE TABLE idb.journeys(id TEXT PRIMARY KEY,label TEXT)")
            db.commit()
            db.execute("BEGIN IMMEDIATE")
            db.execute("UPDATE sessions SET revoked=1 WHERE id='fake'")
            db.execute("INSERT INTO idb.journeys VALUES('fake-journey','fake')")
            db.commit()
            state = [db.execute("SELECT revoked FROM sessions").fetchone()[0],
                     db.execute("SELECT label FROM idb.journeys").fetchone()[0]]
            checks = [db.execute("PRAGMA main.integrity_check").fetchone()[0],
                      db.execute("PRAGMA idb.integrity_check").fetchone()[0]]
            modes = [db.execute("PRAGMA main.journal_mode").fetchone()[0],
                     db.execute("PRAGMA idb.journal_mode").fetchone()[0]]
            sync = [db.execute("PRAGMA main.synchronous").fetchone()[0],
                    db.execute("PRAGMA idb.synchronous").fetchone()[0]]
            page_sizes = [db.execute("PRAGMA main.page_size").fetchone()[0],
                          db.execute("PRAGMA idb.page_size").fetchone()[0]]
        if state != [1, "fake"] or checks != ["ok", "ok"] or \
                modes != ["delete", "delete"] or sync != [2, 2] or \
                page_sizes[0] != page_sizes[1]:
            raise AssertionError("C03: SQLite invariants failed")
        if lib.c03_overflow():
            raise AssertionError("C03: unbounded or incomplete journal capture")
        entries = []
        for i in range(lib.c03_count()):
            path = ctypes.create_string_buffer(1024)
            vals = [ctypes.c_int() for _ in range(7)]
            size = lib.c03_info(i, path, 1024, *[ctypes.byref(v) for v in vals])
            if size < 0:
                raise AssertionError("C03: file identity unavailable")
            raw = (ctypes.c_ubyte * size)()
            mask = (ctypes.c_ubyte * size)()
            if lib.c03_copy(i, raw, mask, size) != size:
                raise AssertionError("C03: memory copy incomplete")
            close_fields = [ctypes.c_int() for _ in range(3)]
            if lib.c03_close_info(i, *[ctypes.byref(x) for x in close_fields]) != 0:
                raise AssertionError("C03-R03: état xClose inaccessible")
            entries.append({"close_called": close_fields[0].value,
                            "close_known": close_fields[1].value,
                            "close_rc": close_fields[2].value,
                            "path": path.value.decode(), "kind": vals[0].value,
                            "generation": vals[1].value, "closed": vals[2].value,
                            "deleted": vals[3].value, "error": vals[4].value,
                            "writes": vals[5].value, "truncates": vals[6].value,
                            "data": bytes(raw), "mask": bytes(mask)})
        delete_stats = [ctypes.c_int() for _ in range(6)]
        lib.c03_delete_stats.argtypes = [ctypes.POINTER(ctypes.c_int)] * 6
        lib.c03_delete_stats.restype = ctypes.c_int
        if lib.c03_delete_stats(*[ctypes.byref(x) for x in delete_stats]) != 0:
            raise AssertionError("C03-R02: delete evidence unavailable")
        deletion = dict(zip(("events", "attributed", "ambiguous", "no_match",
                             "native_errors", "not_closed"), (x.value for x in delete_stats)))
        validate_deletion_attribution(deletion)
        certificate = reciprocal_certificate(entries, main, attached, page_sizes[0])
        certificate.update({"deletion_attribution": deletion, "sqlite_version": sqlite3.sqlite_version,
                            "same_sqlite_symbol": same, "page_size": page_sizes[0],
                            "mutations": state, "integrity_check": checks,
                            "journal_mode": modes, "synchronous": sync,
                            "observed_journal_incarnations": len(entries),
                            "raw_buffers_published": False,
                            "crash_recovery_demonstrated": False,
                            "before_delegate_demonstrated": False,
                            "physical_durability_demonstrated": False,
                            "platform": platform.system()})
        return certificate

if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, sort_keys=True, indent=2))
