"""G01/G02/G05 VFS step1 prequalification, no fault injection."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "rd01-vfs-step1"))
from rd01_vfs_step1 import run


class RD01VFSStage1(unittest.TestCase):
    def test_g01_g02_g05_prequalification(self):
        proof=run()
        self.assertTrue(proof["G01"]["same_engine"])
        self.assertEqual(proof["G02"]["databases"],["identities.sqlite","sessions.sqlite"])
        self.assertTrue(proof["G02"]["journal_files"])
        self.assertEqual(proof["G05"]["integrity"],["ok","ok"])
        self.assertEqual(proof["G05"]["invariant"],[1,"fake"])
        self.assertTrue(proof["G05"]["raw_unchanged"])
        self.assertTrue(proof["G03"]["observations"]["two_databases"])
        self.assertFalse(proof["G03"]["observations"]["commit_internal_phase_proven"])
        self.assertFalse(proof["G03"]["observations"]["durability_proven"])
        print("RD01 G03 NORMAL COMMIT TRACE "+json.dumps(proof["G03"],sort_keys=True,ensure_ascii=False),flush=True)
        compact={k:proof[k] for k in ("G01","G02")}
        compact["G05"]={k:v for k,v in proof["G05"].items() if k!="manifest_raw"}
        compact["manifest_raw"]=proof["G05"]["manifest_raw"]
        compact["environment"]={k:v for k,v in proof["environment"].items() if k!="compile_options"}
        compact["compile_options_sha256_note"]="See full script; options omitted from CI log"
        print("RD01 VFS STEP1 PROOF "+json.dumps(compact,sort_keys=True,ensure_ascii=False),flush=True)


if __name__=="__main__":
    unittest.main()
