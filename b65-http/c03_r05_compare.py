"""C03-R05: N/W/C03 bounded parity and descriptive duration measurements.

Protocol frozen at b65-http/SEC01-RD01-C03-R05-PROTOCOLE-20261025.md.
No crash, no causal callback, no modifications of C wrappers.
"""
import argparse
import ctypes
import ctypes.util
import json
from pathlib import Path
import platform
import sqlite3
import statistics
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE / "rd01-vfs-step1"
MODES = ("N", "W", "C03")
RESOLUTIONS = ("COMMIT", "ROLLBACK")
ORDERS = (("N", "W", "C03"), ("W", "C03", "N"), ("C03", "N", "W"))


def _configure(mode, directory):
    sys.path.insert(0, str(ROOT))
    import vfs_r01_contention as old
    if mode == "N":
        return old, None
    if mode == "W":
        source = ROOT / "atlas_rd01_vfs.c"
        name, register = "atlas_rd01_observer", "atlas_rd01_register"
        symbol, version = "atlas_rd01_sqlite_symbol", "atlas_rd01_sqlite_version"
    else:
        source = ROOT / "c03-passive" / "c03_vfs.c"
        name, register = "atlas_c03_passive", "c03_register"
        symbol, version = "c03_sqlite_symbol", "c03_sqlite_version"
    so = directory / "observer.so"
    proc = subprocess.run(["cc", "-std=c11", "-shared", "-fPIC", "-o",
                           str(so), str(source), "-lsqlite3"],
                          capture_output=True, text=True, timeout=15)
    if proc.returncode:
        raise AssertionError("compiler failed: " + proc.stderr)
    lib = ctypes.CDLL(str(so))
    getattr(lib, version).restype = ctypes.c_char_p
    getattr(lib, symbol).restype = ctypes.c_void_p
    sqlite = ctypes.CDLL(ctypes.util.find_library("sqlite3"))
    sqlite.sqlite3_vfs_find.restype = ctypes.c_void_p
    if (getattr(lib, version)().decode() != sqlite3.sqlite_version or
        getattr(lib, symbol)() != ctypes.cast(sqlite.sqlite3_vfs_find, ctypes.c_void_p).value):
        raise AssertionError("SQLite engine or symbol mismatch")
    method = getattr(lib, register)
    method.restype = ctypes.c_int
    if mode == "W":
        method.argtypes = [ctypes.c_char_p]
        status = method(str(directory / "W-events.tsv").encode())
    else:
        status = method()
    if status != sqlite3.SQLITE_OK:
        raise AssertionError("VFS register failed")
    def _uri(path, wrapped=False):
        from urllib.parse import quote
        return "file:" + quote(str(path)) + "?mode=rwc&vfs=" + name
    old._uri = _uri
    return old, lib


def child(mode, resolution):
    with tempfile.TemporaryDirectory(prefix="atlas-c03-r05-") as tmp:
        directory = Path(tmp)
        old, lib = _configure(mode, directory)
        case = directory / "case"
        before = time.perf_counter_ns()
        result = old._scenario(case, mode != "N", resolution)
        duration_ns = time.perf_counter_ns() - before
        if mode == "C03" and lib.c03_overflow() != 0:
            raise AssertionError("C03 observer quota exceeded")
        # Exclude any environmental paths from the comparison.
        return {"configuration": mode, "resolution": resolution,
                "duration_ns": duration_ns, "result": result,
                "sqlite": sqlite3.sqlite_version, "python": platform.python_version(),
                "platform": platform.platform()}


def _invoke(mode, resolution):
    proc = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--child",
                           mode, resolution], text=True, capture_output=True, timeout=30)
    if proc.returncode:
        raise AssertionError(mode + "/" + resolution + " child failed: " +
                             proc.stderr[-4000:])
    try:
        return json.loads(proc.stdout)
    except ValueError as exc:
        raise AssertionError("unparseable result " + proc.stdout[-1000:]) from exc


def campaign():
    raw = []
    # Warmups: strictly separate from measured data.
    for resolution in RESOLUTIONS:
        for mode in MODES:
            _invoke(mode, resolution)
    for modes in ORDERS:
        for resolution in RESOLUTIONS:
            for mode in modes:
                raw.append(_invoke(mode, resolution))
    summaries = {}
    for resolution in RESOLUTIONS:
        refs = [r for r in raw if r["resolution"] == resolution]
        native = next(r["result"] for r in refs if r["configuration"] == "N")
        for r in refs:
            if r["result"] != native:
                raise AssertionError("N/W/C03 functional divergence: " +
                                     repr({"mode": r["configuration"],
                                           "resolution": resolution, "data": r["result"]}))
            if r["result"]["busy_code"] != sqlite3.SQLITE_BUSY:
                raise AssertionError("SQLITE_BUSY not preserved")
        summaries[resolution] = {}
        for mode in MODES:
            ms = [r["duration_ns"] / 1e6 for r in refs if r["configuration"] == mode]
            if len(ms) != 3:
                raise AssertionError("repetition count invalid")
            summaries[resolution][mode] = {
                "samples_ms": [round(x, 6) for x in ms],
                "median_ms": round(statistics.median(ms), 6),
                "min_ms": round(min(ms), 6), "max_ms": round(max(ms), 6),
                "range_ms": round(max(ms) - min(ms), 6)}
    return {"protocol": "SEC01-RD01-C03-R05-PROTOCOLE-20261025.md",
            "scenario": "existing vfs_r01_contention._scenario",
            "sqlite": sqlite3.sqlite_version,
            "platform": platform.platform(), "python": platform.python_version(),
            "warmups": 6, "measured_samples": len(raw),
            "order": [list(x) for x in ORDERS], "functional_parity": True,
            "summary": summaries, "not_demonstrated": [
                "absolute temporal neutrality", "physical durability",
                "same native IO-call sequences", "crash recovery", "G04"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--child", nargs=2, metavar=("MODE", "RESOLUTION"))
    args = parser.parse_args()
    if args.child:
        mode, resolution = args.child
        if mode not in MODES or resolution not in RESOLUTIONS:
            parser.error("invalid case")
        print(json.dumps(child(mode, resolution), ensure_ascii=False))
    else:
        print(json.dumps(campaign(), ensure_ascii=False, sort_keys=True))
