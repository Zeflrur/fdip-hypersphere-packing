"""
Unit tests for fdip_applications.py (Hierarchical 4D QAM & Bidisperse Container Fill).
Ref. FDIP-D4-TAU
"""

import unittest
from fdip_applications import Hierarchical4DQAM, BidisperseContainerFill


class TestFDIPApplications(unittest.TestCase):
    def test_hierarchical_4d_qam_bit_gain(self):
        """Adding 3 interstitial holes per primary D4 symbol quadruples symbol count (+2.0 bits)."""
        qam = Hierarchical4DQAM(peak_radius_ratio=6.0)
        summary = qam.summary()
        self.assertGreater(summary["primary_symbols"], 0)
        self.assertEqual(summary["total_symbols"], summary["primary_symbols"] * 4)
        self.assertAlmostEqual(summary["extra_bits_per_symbol"], 2.0, places=3)
        self.assertAlmostEqual(summary["relative_volume_gain_pct"], 8.83, places=2)

    def test_hierarchical_4d_qam_invalid_radius(self):
        """Peak radius ratio must exceed 1.0."""
        with self.assertRaises(ValueError):
            Hierarchical4DQAM(peak_radius_ratio=1.0)

    def test_bidisperse_fill_dimensions(self):
        """Verify bidisperse efficiency strictly exceeds single-size efficiency across 2D-4D."""
        for dim in (2, 3, 4):
            fill = BidisperseContainerFill(dimension=dim, container_radius_ratio=20.0).estimate_fill()
            self.assertGreater(fill["secondary_spheres"], 0)
            self.assertGreater(fill["bidisperse_efficiency"], fill["single_size_efficiency"])
            self.assertGreater(fill["efficiency_gain_pct"], 0.0)

    def test_bidisperse_4d_outperforms_2d_and_3d_gain(self):
        """Confirm 4D exhibits the largest finite-container efficiency gain at R=10."""
        gains = {
            dim: BidisperseContainerFill(dimension=dim, container_radius_ratio=10.0).estimate_fill()["efficiency_gain_pct"]
            for dim in (2, 3, 4)
        }
        self.assertGreater(gains[4], gains[3])
        self.assertGreater(gains[4], gains[2])


if __name__ == "__main__":
    unittest.main()
