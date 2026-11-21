import unittest
import math
from fdip_model import FDIPModel

TAU = 2 * math.pi


class TestFDIPModel(unittest.TestCase):
    def setUp(self):
        self.model = FDIPModel()

    def test_base_lattice_densities(self):
        expected = {
            2: (TAU / 2) / math.sqrt(12),
            3: (TAU / 2) / (3 * math.sqrt(2)),
            4: ((TAU / 2) ** 2) / 16,
            8: ((TAU / 2) ** 4) / 384,
            24: ((TAU / 2) ** 12) / math.factorial(12),
        }
        for dim, val in expected.items():
            self.assertAlmostEqual(self.model.base_density(dim), val, places=6)

    def test_4d_peak_single_generation_boost(self):
        boosts = {
            dim: self.model.gen1_density(dim) - self.model.base_density(dim)
            for dim in [2, 3, 4, 8, 24]
        }
        peak_dim = max(boosts, key=boosts.get)
        self.assertEqual(peak_dim, 4)
        self.assertAlmostEqual(boosts[4], 0.054454, places=4)

    def test_discrete_bounded_by_envelope(self):
        for dim in [2, 3, 4, 8]:
            for r in [2.5, 5.0, 10.0, 25.0]:
                discrete = self.model.discrete_efficiency(dim, r)
                envelope = self.model.peak_envelope(dim, r)
                self.assertLessEqual(discrete, envelope + 1e-12)
                self.assertGreaterEqual(discrete, 0.0)

    def test_minimum_retention_radius(self):
        r_2d = self.model.min_radius_for_retention(dim=2, alpha=0.90)
        r_24d = self.model.min_radius_for_retention(dim=24, alpha=0.90)
        self.assertAlmostEqual(r_2d, 7.405, places=2)
        self.assertGreater(r_24d, 110.0)


if __name__ == "__main__":
    unittest.main()
