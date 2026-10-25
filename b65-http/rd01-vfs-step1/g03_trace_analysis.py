"""SEC-01 RD01 G03 : analyse hors ligne de traces VFS, sans injection ni arrêt."""
from collections import Counter
from pathlib import Path


def analyze_trace(path):
    events = []
    for index, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        fields = line.split("\t")
        if len(fields) != 7:
            raise ValueError(f"Trace VFS mal formée, ligne {index}")
        seq, pid, event, role, rc, flags, filename = fields
        record = dict(seq=int(seq), pid=int(pid), event=event, role=role,
                      rc=int(rc), flags=int(flags), filename=filename)
        events.append(record)
    if not events:
        raise ValueError("Trace VFS vide")
    sequences = [e["seq"] for e in events]
    if sequences != sorted(set(sequences)):
        raise ValueError("Séquence non strictement croissante ou doublon")
    candidate_opens = [e for e in events if e["event"] == "xOpen" and
                       e["role"] == "super-journal-candidate" and e["rc"] == 0]
    candidates = []
    for opening in candidate_opens:
        later = [e for e in events if e["seq"] > opening["seq"]
                 and e["filename"] == opening["filename"] and e["event"] == "xDelete"]
        candidates.append({
            "filename": opening["filename"], "open_seq": opening["seq"],
            "delete_seq": later[0]["seq"] if later else None,
            "delete_rc": later[0]["rc"] if later else None,
            "matched_successful_delete": bool(later and later[0]["rc"] == 0),
            "matching_basis": "basename et ordre dans la même trace, pas une identité de handle"
        })
    statuses = {
        "two_databases": {"sessions.sqlite", "identities.sqlite"}.issubset({
            e["filename"] for e in events if e["event"] == "xOpen" and
            e["role"] == "main-db" and e["rc"] == 0}),
        "candidate_open_observed": bool(candidate_opens),
        "candidate_delete_observed": any(c["matched_successful_delete"] for c in candidates),
        "commit_internal_phase_proven": False,
        "before_after_delegate_proven": False,
        "transaction_id_proven": False,
        "durability_proven": False
    }
    return {
        "scope": "COMMIT normal du banc fictif ; émission VFS post-délégation",
        "event_count": len(events), "event_types": dict(Counter(e["event"] for e in events)),
        "pid_count": len(set(e["pid"] for e in events)),
        "sequence_min": sequences[0], "sequence_max": sequences[-1],
        "candidates": candidates, "observations": statuses,
        "limits": [
            "xDelete est loggé après retour de la VFS mère",
            "le rôle xDelete du super-journal est rapproché par nom de fichier",
            "aucun identifiant explicite de transaction, aucune phase COMMIT instrumentée",
            "sérialisation globale non protégée pour plusieurs threads",
            "trace non fsync après chaque événement et basename sans chemin canonique",
            "pas de suspension, SIGKILL, panne ou mesure de durabilité"]
    }
