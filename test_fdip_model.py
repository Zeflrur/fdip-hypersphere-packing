import unittest
import math
from fdip_model import FDIPModel

TAU = 2 * math.pi


class TestFDIPModel(unittest.TestCase):
    def test_base_lattice_densities(self):
        expected = {
            2: (TAU / 2) / math.sqrt(12),
            3: (TAU / 2) / (3 * math.sqrt(2)),
            4: ((TAU / 2) ** 2) / 16,
            8: ((TAU / 2) ** 4) / 384,
            24: ((TAU / 2) ** 12) / math.factorial(12),
        }
        for dim, val in expected.items():
            model = FDIPModel(dimension=dim)
            self.assertAlmostEqual(model.base_density(), val, places=6)

    def test_4d_peak_single_generation_boost(self):
        boosts = {}
        for dim in [2, 3, 4, 8, 24]:
            model = FDIPModel(dimension=dim)
            boosts[dim] = model.interstitial_density(generations=1) - model.base_density()
        peak_dim = max(boosts, key=boosts.get)
        self.assertEqual(peak_dim, 4)
        self.assertAlmostEqual(boosts[4], 0.054454, places=4)

    def test_finite_efficiency_and_sphere_count_consistency(self):
        for dim in [2, 3, 4, 8]:
            model = FDIPModel(dimension=dim)
            for r in [3.0, 5.0, 10.0, 20.0]:
                eff = model.finite_efficiency(R=r, generations=0)
                count = model.sphere_count(R=r, generations=0)
                self.assertAlmostEqual(eff, count / (r ** dim), places=8)
                self.assertLessEqual(eff, model.base_density())
                self.assertGreaterEqual(eff, 0.0)

    def test_interstitial_density_monotonicity(self):
        model_4d = FDIPModel(dimension=4)
        base = model_4d.base_density()
        gen1 = model_4d.interstitial_density(generations=1)
        self.assertGreater(gen1, base)
        self.assertLess(gen1, 1.0)


if __name__ == "__main__":
    unittest.main()
