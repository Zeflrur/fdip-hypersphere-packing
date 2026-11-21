"""
Practical Engineering Applications of the Finite Dimensional Interstitial Packing (FDIP) Model.
Ref. FDIP-D4-TAU

Demonstrates two applied use cases:
1. Hierarchical 4D QAM Signal Constellation Packing (Optical & Wireless Communications)
2. Finite-Container Bidisperse Particle & Bundle Fill Estimation (Materials & Conduit Engineering)
"""

import math
from typing import Dict

TAU = 2.0 * math.pi


class Hierarchical4DQAM:
    """
    Models a two-tier 4D signal constellation built on the D4 checkerboard lattice
    plus its 3 deep interstitial holes (r1 = sqrt(2) - 1) per primary lattice point.

    Physical context:
        Dual-polarization optical fiber or MIMO wireless links transmit 4 real
        dimensions per symbol interval (I_H, Q_H, I_V, Q_V). Bounding peak symbol
        energy corresponds to bounding points inside a 4D hypersphere of radius R.
    """

    def __init__(self, peak_radius_ratio: float = 6.0, boundary_loss: float = 0.5):
        if peak_radius_ratio <= 1.0:
            raise ValueError("peak_radius_ratio (R) must be greater than 1.0")
        self.R = peak_radius_ratio
        self.c = boundary_loss
        self.eta_d4 = ((TAU / 2.0) ** 2) / 16.0  # ~0.616850
        self.r_hole = math.sqrt(2.0) - 1.0        # ~0.414214
        self.holes_per_cell = 3

    def primary_symbol_count(self) -> int:
        """Number of high-reliability primary D4 symbols within peak power radius R."""
        usable_r = max(0.0, self.R - self.c)
        return int(math.floor(self.eta_d4 * (usable_r ** 4)))

    def interstitial_symbol_count(self) -> int:
        """Number of secondary lower-power symbols placed inside D4 deep holes."""
        return self.primary_symbol_count() * self.holes_per_cell

    def summary(self) -> Dict[str, float]:
        """Compute capacity, spectral efficiency gain, and packing density metrics."""
        n_base = self.primary_symbol_count()
        n_hole = self.interstitial_symbol_count()
        n_total = n_base + n_hole

        bits_base = math.log2(n_base) if n_base > 0 else 0.0
        bits_total = math.log2(n_total) if n_total > 0 else 0.0

        vol_base = n_base / (self.R ** 4)
        vol_total = (n_base + n_hole * (self.r_hole ** 4)) / (self.R ** 4)

        return {
            "R": self.R,
            "primary_symbols": n_base,
            "interstitial_symbols": n_hole,
            "total_symbols": n_total,
            "bits_per_4d_symbol_base": round(bits_base, 3),
            "bits_per_4d_symbol_hierarchical": round(bits_total, 3),
            "extra_bits_per_symbol": round(bits_total - bits_base, 3),
            "base_packing_efficiency": round(vol_base, 5),
            "hierarchical_packing_efficiency": round(vol_total, 5),
            "relative_volume_gain_pct": round(((vol_total / vol_base) - 1.0) * 100.0, 2)
            if vol_base > 0
            else 0.0,
        }


class BidisperseContainerFill:
    """
    Estimates primary and interstitial particle counts inside a bounded d-dimensional
    container (e.g., 2D cable conduits, 3D packed-bed reactors or battery electrodes).
    """

    BASE_LIMITS = {
        2: (TAU / 2.0) / math.sqrt(12.0),
        3: (TAU / 2.0) / (3.0 * math.sqrt(2.0)),
        4: ((TAU / 2.0) ** 2) / 16.0,
    }

    HOLE_SPECS = {
        2: (2.0 / math.sqrt(3.0) - 1.0, 2),
        3: (math.sqrt(2.0) - 1.0, 1),  # Octahedral voids in FCC
        4: (math.sqrt(2.0) - 1.0, 3),  # Deep holes in D4
    }

    def __init__(self, dimension: int, container_radius_ratio: float):
        if dimension not in self.BASE_LIMITS:
            raise ValueError("Supported dimensions for bidisperse fill: 2, 3, 4")
        self.d = dimension
        self.R = container_radius_ratio
        self.c = 0.38 if dimension == 2 else 0.50

    def estimate_fill(self) -> Dict[str, float]:
        """Return primary count, interstitial count, and finite container efficiencies."""
        eta_0 = self.BASE_LIMITS[self.d]
        r_1, n_holes = self.HOLE_SPECS[self.d]

        usable_r = max(0.0, self.R - self.c)
        n_primary = int(math.floor(eta_0 * (usable_r ** self.d)))
        n_secondary = n_primary * n_holes

        eff_single = n_primary / (self.R ** self.d)
        eff_bidisperse = (n_primary + n_secondary * (r_1 ** self.d)) / (self.R ** self.d)

        return {
            "dimension": self.d,
            "R": self.R,
            "primary_spheres": n_primary,
            "secondary_spheres": n_secondary,
            "secondary_radius_ratio": round(r_1, 5),
            "single_size_efficiency": round(eff_single, 5),
            "bidisperse_efficiency": round(eff_bidisperse, 5),
            "efficiency_gain_pct": round((eff_bidisperse - eff_single) * 100.0, 2),
        }


if __name__ == "__main__":
    print("=== 1. Hierarchical 4D QAM Signal Constellation (D4 + Deep Holes) ===")
    for r_val in [4.0, 6.0, 8.0, 10.0]:
        qam = Hierarchical4DQAM(peak_radius_ratio=r_val).summary()
        print(
            f"R={qam['R']:4.1f} | Base: {qam['primary_symbols']:4d} syms ({qam['bits_per_4d_symbol_base']:5.2f} bits) "
            f"-> Hierarchical: {qam['total_symbols']:5d} syms ({qam['bits_per_4d_symbol_hierarchical']:5.2f} bits, "
            f"+{qam['extra_bits_per_symbol']:.2f} bits/sym, +{qam['relative_volume_gain_pct']:.2f}% vol)"
        )

    print("\n=== 2. Finite-Container Bidisperse Fill Across 2D, 3D, and 4D ===")
    for dim in [2, 3, 4]:
        fill = BidisperseContainerFill(dimension=dim, container_radius_ratio=10.0).estimate_fill()
        print(
            f"{dim}D (R=10) | Primary: {fill['primary_spheres']:4d} | Secondary (r={fill['secondary_radius_ratio']:.3f}): "
            f"{fill['secondary_spheres']:5d} | Eff: {fill['single_size_efficiency']:.2%} -> "
            f"{fill['bidisperse_efficiency']:.2%} (+{fill['efficiency_gain_pct']:.2f}%)"
        )
