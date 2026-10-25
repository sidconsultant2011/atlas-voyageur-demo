"""C03-3: contrôle réel en COMMIT normal et rejets synthétiques hors SQLite."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent / "rd01-vfs-step1" / "c03-passive"))
from c03_run import run, reciprocal_certificate, validate_deletion_attribution, MAGIC, checksum

MAIN = Path("/fictional/c03/sessions.sqlite")
ATTACHED = Path("/fictional/c03/identities.sqlite")
S = "/fictional/c03/sessions.sqlite-mjABC123"

def fictional_entries():
    names = (str(MAIN) + "-journal", str(ATTACHED) + "-journal")
    super_bytes = (names[0] + "\0" + names[1] + "\0").encode()
    entries = [{"path": S, "kind": 2, "generation": 3, "closed": 1, "deleted": 1,
                "error": 0, "writes": 2, "truncates": 0,
                "data": super_bytes, "mask": b"\x01" * len(super_bytes)}]
    for gen, name in enumerate(names, 1):
        bs = S.encode()
        ptr = ((0x40000000 // 4096 + 1).to_bytes(4, "big") + bs +
               len(bs).to_bytes(4, "big") + checksum(bs).to_bytes(4, "big") + MAGIC)
        data = b"\0" * 512 + ptr
        entries.append({"path": name, "kind": 1, "generation": gen,
                        "closed": 1, "deleted": 1, "error": 0,
                        "writes": 2, "truncates": 0, "data": data,
                        "mask": b"\0" * 512 + b"\x01" * len(ptr)})
    return entries

class C03Passive(unittest.TestCase):
    def test_certificate_rejects_no_match_one_and_many(self):
        baseline = {"events": 1, "attributed": 0, "ambiguous": 0, "no_match": 0, "native_errors": 0, "not_closed": 0}
        for count in (1, 2):
            with self.subTest(no_match=count):
                values = dict(baseline, events=count, no_match=count)
                with self.assertRaisesRegex(AssertionError, "deletion attribution incomplete"):
                    validate_deletion_attribution(values)

    def test_certificate_all_zero_is_accepted(self):
        validate_deletion_attribution({
            "events": 1, "attributed": 1,
            "ambiguous": 0, "no_match": 0, "native_errors": 0, "not_closed": 0
        })

    def test_certificate_keeps_other_rejections(self):
        baseline = {"events": 1, "attributed": 0, "ambiguous": 0, "no_match": 0, "native_errors": 0, "not_closed": 0}
        for field in ("ambiguous", "native_errors", "not_closed"):
            with self.subTest(field=field):
                values = dict(baseline, **{field: 1})
                with self.assertRaises(AssertionError):
                    validate_deletion_attribution(values)

    def test_r01_one_compatible_incarnation(self):
        proof = reciprocal_certificate(fictional_entries(), MAIN, ATTACHED, 4096)
        self.assertEqual([w["journal_generation"] for w in proof["provenance"]], [1, 2])

    def test_r01_historical_incarnation_discriminated_by_references(self):
        e = fictional_entries()
        old = dict(e[1], generation=0, data=b"\x00" * 512,
                   mask=b"\x00" * 512, deleted=1, closed=1)
        e.append(old)
        proof = reciprocal_certificate(e, MAIN, ATTACHED, 4096)
        self.assertEqual(proof["provenance"][0]["journal_generation"], 1)

    def test_r01_indistinguishable_compatible_incarnations_rejected(self):
        e = fictional_entries()
        e.append(dict(e[1], generation=0))
        with self.assertRaisesRegex(AssertionError, "plusieurs incarnations"):
            reciprocal_certificate(e, MAIN, ATTACHED, 4096)

    def test_r01_missing_participant_rejected(self):
        e = fictional_entries()
        e.pop(2)
        with self.assertRaises(AssertionError):
            reciprocal_certificate(e, MAIN, ATTACHED, 4096)

    def test_r01_incompatible_reciprocal_reference_rejected(self):
        e = fictional_entries()
        e[1]["data"] = e[1]["data"].replace(S.encode(), b"X" * len(S))
        with self.assertRaises(AssertionError):
            reciprocal_certificate(e, MAIN, ATTACHED, 4096)
        e = fictional_entries()
        e[0]["data"] = e[0]["data"].replace((str(MAIN)+"-journal").encode(),
                                             b"X" * len(str(MAIN)+"-journal"))
        with self.assertRaises(AssertionError):
            reciprocal_certificate(e, MAIN, ATTACHED, 4096)

    def test_r01_recreated_or_replaced_without_continuity_rejected(self):
        e = fictional_entries()
        newer = dict(e[1], generation=4, data=b"", mask=b"",
                     deleted=0, closed=1)
        e.append(newer)
        with self.assertRaisesRegex(AssertionError, "recréation/remplacement"):
            reciprocal_certificate(e, MAIN, ATTACHED, 4096)

    def test_r01_incomplete_incarnation_rejected(self):
        e = fictional_entries()
        e[1]["mask"] = e[1]["mask"][:-12] + b"\x00" * 12
        with self.assertRaises(AssertionError):
            reciprocal_certificate(e, MAIN, ATTACHED, 4096)

    def test_normal_commit_real_sqlite(self):
        proof = run()
        self.assertEqual(proof["verdict"], "RECONSTRUIT_BANC_FICTIF")
        self.assertEqual(proof["links"], {"S_to_journals": ["A", "B"],
                                          "A_to_S": True, "B_to_S": True})
        self.assertEqual(proof["integrity_check"], ["ok", "ok"])
        self.assertTrue(proof["same_sqlite_symbol"])
        self.assertFalse(proof["physical_durability_demonstrated"])
        print("RD01 C03-3 PASSIVE CERTIFICATE " +
              json.dumps(proof, ensure_ascii=False, sort_keys=True), flush=True)

    def test_reject_missing_reference(self):
        e = fictional_entries()
        e[2]["data"] = e[2]["data"].replace(S.encode(), b"X" * len(S))
        with self.assertRaises(AssertionError):
            reciprocal_certificate(e, MAIN, ATTACHED, 4096)

    def test_reject_incomplete_fragment(self):
        e = fictional_entries()
        e[1]["mask"] = e[1]["mask"][:-10] + b"\0" * 10
        with self.assertRaises(AssertionError):
            reciprocal_certificate(e, MAIN, ATTACHED, 4096)

    def test_reject_ambiguous_super(self):
        e = fictional_entries()
        e.append(dict(e[0], generation=4))
        with self.assertRaises(AssertionError):
            reciprocal_certificate(e, MAIN, ATTACHED, 4096)

    def test_accept_complete_synthetic_fragments(self):
        e = fictional_entries()
        p = reciprocal_certificate(e, MAIN, ATTACHED, 4096)
        self.assertEqual(p["verdict"], "RECONSTRUIT_BANC_FICTIF")

if __name__ == "__main__":
    unittest.main()
