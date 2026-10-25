"""SEC01 C03-R06 lot 1 — comptabilité stricte xDelete, données synthétiques."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent/"rd01-vfs-step1"/"c03-passive"))
from c03_run import validate_deletion_attribution

GOOD={"events":6,"attributed":6,"ambiguous":0,"no_match":0,
      "native_errors":0,"not_closed":0}

class C03R06Accounting(unittest.TestCase):
    def test_balanced_positive_certificate(self):
        validate_deletion_attribution(dict(GOOD))

    def test_unattributed_event_with_zero_anomalies_rejected(self):
        with self.assertRaisesRegex(AssertionError,"inconsistent xDelete accounting"):
            validate_deletion_attribution(dict(GOOD,attributed=5))

    def test_overcount_rejected(self):
        with self.assertRaisesRegex(AssertionError,"inconsistent xDelete accounting"):
            validate_deletion_attribution(dict(GOOD,attributed=7))

    def test_negative_counter_rejected(self):
        for key in GOOD:
            with self.subTest(key=key):
                with self.assertRaisesRegex(AssertionError,"invalid xDelete counters"):
                    validate_deletion_attribution(dict(GOOD,**{key:-1}))

    def test_missing_required_field_rejected_without_keyerror(self):
        for key in GOOD:
            with self.subTest(key=key):
                candidate=dict(GOOD)
                del candidate[key]
                with self.assertRaisesRegex(AssertionError,"invalid xDelete counters"):
                    validate_deletion_attribution(candidate)

    def test_invalid_type_rejected_without_typeerror(self):
        for value in ("6",6.0,None,True,False,[],{}):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(AssertionError,"invalid xDelete counters"):
                    validate_deletion_attribution(dict(GOOD,events=value))
        with self.assertRaisesRegex(AssertionError,"invalid xDelete counters"):
            validate_deletion_attribution(None)

    def test_accounted_positive_anomaly_still_blocks_certificate(self):
        for kind in ("ambiguous","no_match","native_errors","not_closed"):
            with self.subTest(kind=kind):
                candidate=dict(GOOD,attributed=5,**{kind:1})
                with self.assertRaisesRegex(AssertionError,"deletion attribution incomplete"):
                    validate_deletion_attribution(candidate)

    def test_balanced_zero_event_empty_record(self):
        # Le lot porte sur la cohérence comptable, pas sur une obligation de >0.
        validate_deletion_attribution({key:0 for key in GOOD})

if __name__=="__main__":
    unittest.main()
