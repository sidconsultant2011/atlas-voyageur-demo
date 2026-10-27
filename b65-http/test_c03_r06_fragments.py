"""C03-R06 lot 2 — tests synthétiques de structure des fragments."""
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "rd01-vfs-step1" / "c03-passive"))
from c03_run import reciprocal_certificate, _pointer_offsets, validate_fragment_structure
from test_c03_passive import fictional_entries, MAIN, ATTACHED

class C03R06FragmentStructure(unittest.TestCase):
    def assert_rejected(self, entries, diagnostic):
        with self.assertRaisesRegex(AssertionError, diagnostic):
            reciprocal_certificate(entries, MAIN, ATTACHED, 4096)

    def test_valid_S_A_B_control(self):
        result = reciprocal_certificate(fictional_entries(), MAIN, ATTACHED, 4096)
        self.assertEqual(result["verdict"], "RECONSTRUIT_BANC_FICTIF")
        self.assertEqual(result["links"]["A_to_S"], True)
        self.assertEqual(result["links"]["B_to_S"], True)

    def test_truncated_S_mask_even_all_remaining_one(self):
        entries = fictional_entries()
        entries[0]["mask"] = entries[0]["mask"][:-1]
        self.assertTrue(all(entries[0]["mask"]))
        self.assert_rejected(entries, "length mismatch")

    def test_truncated_A_mask_in_pointer_region(self):
        entries = fictional_entries()
        entries[1]["mask"] = entries[1]["mask"][:-5]
        self.assert_rejected(entries, "length mismatch")

    def test_oversized_B_mask(self):
        entries = fictional_entries()
        entries[2]["mask"] += b"\x01"
        self.assert_rejected(entries, "length mismatch")

    def test_nonbinary_0x02_marker(self):
        for index in range(3):
            with self.subTest(file=index):
                entries = fictional_entries()
                mask = bytearray(entries[index]["mask"])
                mask[-1] = 2
                entries[index]["mask"] = bytes(mask)
                self.assert_rejected(entries, "nonbinary")

    def test_incompatible_data_and_mask_types(self):
        for field, invalid in (("data", "text"), ("mask", "text"),
                               ("data", [1, 2]), ("mask", bytearray(b"\x01")),
                               ("data", None), ("mask", None)):
            with self.subTest(field=field, invalid_type=type(invalid).__name__):
                entries = fictional_entries()
                entries[1][field] = invalid
                self.assert_rejected(entries, "must be bytes")

    def test_direct_pointer_decoder_rejects_invalid_pair(self):
        entries = fictional_entries()
        entries[1]["mask"] += b"\x01"
        with self.assertRaisesRegex(AssertionError, "length mismatch"):
            _pointer_offsets(entries[1], entries[0]["path"].encode(), 4096)

    def test_empty_or_out_of_bounds_slice_never_qualifies(self):
        from c03_run import _observed_slice
        self.assertFalse(_observed_slice(b"abc", b"\x01\x01\x01", 0, 4))
        self.assertFalse(_observed_slice(b"abc", b"\x01\x01\x01", 2, 2))
        self.assertFalse(_observed_slice(b"abc", b"\x01\x01\x01", -1, 2))
        self.assertFalse(_observed_slice(b"abc", b"\x01\x00\x01", 0, 3))

if __name__ == "__main__":
    unittest.main()
