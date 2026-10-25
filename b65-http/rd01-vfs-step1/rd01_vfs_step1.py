"""SEC01 RD01 step1: isolated G01/G02/G05 prequalification; NO SIGKILL."""
import ctypes
import ctypes.util
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from urllib.parse import quote

HERE=Path(__file__).resolve().parent

def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def capture(folder,raw,copy):
    """OS-level file copy; caller ensures all SQLite connections are CLOSED."""
    raw.mkdir(); copy.mkdir()
    manifest=[]
    for f in sorted(folder.iterdir()):
        if not f.is_file(): continue
        shutil.copyfile(f,raw/f.name)
        item={"name":f.name,"size":(raw/f.name).stat().st_size,"sha256":sha(raw/f.name)}
        manifest.append(item)
        shutil.copyfile(raw/f.name,copy/f.name)
        assert sha(copy/f.name)==item["sha256"]
    return manifest

def run():
    with tempfile.TemporaryDirectory(prefix="atlas-rd01-vfs-step1-") as d:
        root=Path(d); fixture=root/"fixture";fixture.mkdir()
        so=root/"observer.so"
        compile_result=subprocess.run(["cc","-std=c11","-shared","-fPIC","-Wall","-Wextra",
                        "-o",str(so),str(HERE/"atlas_rd01_vfs.c"),"-lsqlite3"],
                       check=False,capture_output=True,text=True)
        if compile_result.returncode:
            raise RuntimeError("VFS compiler failure: "+compile_result.stderr)
        obs=ctypes.CDLL(str(so))
        obs.atlas_rd01_register.argtypes=[ctypes.c_char_p]
        obs.atlas_rd01_register.restype=ctypes.c_int
        obs.atlas_rd01_sqlite_version.restype=ctypes.c_char_p
        obs.atlas_rd01_sqlite_symbol.restype=ctypes.c_void_p
        lib=ctypes.CDLL(ctypes.util.find_library("sqlite3"))
        lib.sqlite3_vfs_find.argtypes=[ctypes.c_char_p]
        lib.sqlite3_vfs_find.restype=ctypes.c_void_p
        address=ctypes.cast(lib.sqlite3_vfs_find,ctypes.c_void_p).value
        version=obs.atlas_rd01_sqlite_version().decode()
        same=(address==obs.atlas_rd01_sqlite_symbol() and version==sqlite3.sqlite_version)
        if not same: raise AssertionError("G01: SQLite runtime mismatch")
        trace=fixture/"vfs.tsv"
        assert obs.atlas_rd01_register(str(trace).encode())==0
        assert lib.sqlite3_vfs_find(b"atlas_rd01_observer")
        a=fixture/"sessions.sqlite";b=fixture/"identities.sqlite"
        uri="file:"+quote(str(a))+"?mode=rwc&vfs=atlas_rd01_observer"
        with sqlite3.connect(uri,uri=True) as db:
            db.execute("PRAGMA main.journal_mode=DELETE")
            db.execute("PRAGMA main.synchronous=FULL")
            db.execute("CREATE TABLE sessions (id TEXT PRIMARY KEY, revoked INTEGER)")
            db.execute("INSERT INTO sessions VALUES ('fixture-session',0)")
            db.commit()
            db.execute("ATTACH DATABASE ? AS idb",(str(b),))
            db.execute("PRAGMA idb.journal_mode=DELETE")
            db.execute("PRAGMA idb.synchronous=FULL")
            db.execute("CREATE TABLE idb.journeys (id TEXT PRIMARY KEY,label TEXT)")
            db.commit()
            db.execute("BEGIN IMMEDIATE")
            db.execute("UPDATE sessions SET revoked=1 WHERE id='fixture-session'")
            db.execute("INSERT INTO idb.journeys VALUES ('fixture-journey','fake')")
            db.commit()
            environment={
                "os":platform.platform(),"python":sys.version.split()[0],
                "sqlite3_python":sqlite3.sqlite_version,"sqlite3_vfs_link":version,
                "same_sqlite_symbol_address":same,
                "sqlite_library":ctypes.util.find_library("sqlite3"),
                "compiler":"cc (system, local build only)",
                "compile_options":[x[0] for x in db.execute("PRAGMA compile_options")],
                "database_list":[Path(row[2]).name for row in db.execute("PRAGMA database_list") if row[1]!="temp"],
                "journal_mode":[db.execute("PRAGMA main.journal_mode").fetchone()[0],db.execute("PRAGMA idb.journal_mode").fetchone()[0]],
                "synchronous":[db.execute("PRAGMA main.synchronous").fetchone()[0],db.execute("PRAGMA idb.synchronous").fetchone()[0]],
                "same_device":a.stat().st_dev==b.stat().st_dev}
        # No writer/connection exists after with. No crash injected.
        events=[]
        for line in trace.read_text().splitlines():
            parts=line.split("\t")
            if len(parts)!=7: raise AssertionError("Malformed VFS trace")
            events.append({"seq":int(parts[0]),"pid":int(parts[1]),"event":parts[2],
                           "role":parts[3],"rc":int(parts[4]),"flags":int(parts[5]),"file":parts[6]})
        dbs={e["file"] for e in events if e["event"]=="xOpen" and e["role"]=="main-db"}
        journals={e["file"] for e in events if e["event"]=="xOpen" and "journal" in e["role"]}
        if not {"sessions.sqlite","identities.sqlite"}.issubset(dbs):
            raise AssertionError("G02: main/attached DB not observed")
        if not journals: raise AssertionError("G02: rollback journal not observed")
        manifest=capture(fixture,root/"capture_brute",root/"recuperation_travail")
        # Work-copy ONLY is opened for verification. Original raw data untouched.
        work=root/"recuperation_travail"
        with sqlite3.connect(work/"sessions.sqlite") as db:
            db.execute("ATTACH DATABASE ? AS idb",(str(work/"identities.sqlite"),))
            invariant=[db.execute("SELECT revoked FROM sessions").fetchone()[0],
                       db.execute("SELECT label FROM idb.journeys").fetchone()[0]]
            integrity=[db.execute("PRAGMA main.integrity_check").fetchone()[0],
                       db.execute("PRAGMA idb.integrity_check").fetchone()[0]]
        if invariant!=[1,"fake"] or integrity!=["ok","ok"]: raise AssertionError("G05: invalid work-copy")
        if any(sha(root/"capture_brute"/e["name"])!=e["sha256"] for e in manifest):
            raise AssertionError("G05: raw archive changed")
        proof={"environment":environment,
                "G01":{"status":"demontre_dans_cet_environnement","same_engine":same},
                "G02":{"status":"demontre_pour_ouvertures_observees","databases":sorted(dbs),
                       "journal_files":sorted(journals),
                       "event_counts":{ev:sum(e["event"]==ev for e in events) for ev in
                                       ("xOpen","xWrite","xSync","xDelete","xFileControl")},
                       "super_journal_candidates":[e["file"] for e in events
                           if e["role"]=="super-journal-candidate" and e["event"]=="xOpen"]},
                "G05":{"status":"partiel_sans_journal_chaud","manifest_raw":manifest,
                       "integrity":integrity,"invariant":invariant,"raw_unchanged":True,
                       "recovery_after_crash":"NON_TESTEE"},
                "limits":["Aucune panne ni SIGKILL","Moteur Python du banc uniquement",
                          "Pas de preuve d'adoption VFS par _persistent_journey()",
                          "Aucun journal chaud après panne conservé",
                          "Pas de durabilité physique démontrée"]}
        # G05: publish exactly the existing clean fixture archive, with a manifest.
        # Do not open either original SQLite file before copying.\n        destination=os.environ.get("ATLAS_RD01_G05_OUTPUT")\n        if destination:
            out=Path(destination).resolve()
            if out.exists():
                raise RuntimeError("G05 destination must not exist: "+str(out))
            if out == root or root in out.parents:
                raise RuntimeError("G05 destination must be outside temporary workspace")
            out.mkdir(parents=True)
            shutil.copytree(root/"capture_brute",out/"capture_brute")
            shutil.copytree(root/"recuperation_travail",out/"recuperation_travail")
            snapshot={"schema":"atlas-rd01-g05-v1","nature":"bases fictives propres, sans panne",
                      "source_commit":os.environ.get("GITHUB_SHA","local-non-versionne"),
                      "source_run":os.environ.get("GITHUB_RUN_ID","local"),
                      "files":manifest,"environment":environment,
                      "database_state":invariant,"integrity_check":integrity,
                      "no_hot_journals":True,"no_crash_recovery":True}
            (out/"manifest.json").write_text(json.dumps(snapshot,indent=2,sort_keys=True)+"\\n",encoding="utf-8")
            (out/"proof.json").write_text(json.dumps(proof,indent=2,sort_keys=True)+"\\n",encoding="utf-8")
            for item in manifest:
                for directory in ("capture_brute","recuperation_travail"):
                    saved=out/directory/item["name"]
                    if saved.stat().st_size!=item["size"] or sha(saved)!=item["sha256"]:
                        raise AssertionError("G05 archived bytes differ: "+str(saved))
            proof["G05"]["persistent_output"]=str(out)
            proof["G05"]["persisted_files_verified"]=2*len(manifest)
        return proof

if __name__=="__main__":
    r=run()
    print(json.dumps(r,indent=2,ensure_ascii=False))
