"""
Finite Dimensional Interstitial Packing (FDIP) Model
Formulated in collaboration with Gemini (Google AI) - Ref. FDIP-D4-TAU

Computes finite-container hypersphere packing efficiency, integer sphere-count
jumps, boundary dead-zone scaling, and multi-generation interstitial void filling
across spatial dimensions d in {2, 3, 4, 8, 24} using tau = 2 * pi.
"""

import math
from dataclasses import dataclass
from typing import Dict, List, Tuple
import numpy as np
import matplotlib.pyplot as plt

TAU = math.tau  # 2 * pi


@dataclass(frozen=True)
class LatticeSpec:
    dimension: int
    name: str
    base_density: float
    hole_radius: float
    holes_per_sphere: int
    boundary_offset: float


LATTICE_SPECS: Dict[int, LatticeSpec] = {
    2: LatticeSpec(
        dimension=2,
        name="Hexagonal (A2)",
        base_density=(TAU / 2.0) / math.sqrt(12.0),
        hole_radius=(2.0 / math.sqrt(3.0)) - 1.0,
        holes_per_sphere=2,
        boundary_offset=0.38,
    ),
    3: LatticeSpec(
        dimension=3,
        name="FCC (A3 / D3)",
        base_density=(TAU / 2.0) / (3.0 * math.sqrt(2.0)),
        hole_radius=math.sqrt(2.0) - 1.0,
        holes_per_sphere=1,
        boundary_offset=0.50,
    ),
    4: LatticeSpec(
        dimension=4,
        name="Checkerboard (D4)",
        base_density=((TAU / 2.0) ** 2) / 16.0,
        hole_radius=math.sqrt(2.0) - 1.0,
        holes_per_sphere=3,
        boundary_offset=0.50,
    ),
    8: LatticeSpec(
        dimension=8,
        name="E8 Lattice",
        base_density=((TAU / 2.0) ** 4) / 384.0,
        hole_radius=math.sqrt(2.0) - 1.0,
        holes_per_sphere=135,
        boundary_offset=0.50,
    ),
    24: LatticeSpec(
        dimension=24,
        name="Leech (Lambda24)",
        base_density=((TAU / 2.0) ** 12) / math.factorial(12),
        hole_radius=math.sqrt(2.0) - 1.0,
        holes_per_sphere=196560,
        boundary_offset=0.50,
    ),
}


class FDIPModel:
    """Finite Dimensional Interstitial Packing (FDIP) analytical model."""

    def __init__(self, dimension: int, custom_c: float = None):
        if dimension not in LATTICE_SPECS:
            raise ValueError(f"Unsupported dimension {dimension}. Choose from {list(LATTICE_SPECS.keys())}.")
        self.spec = LATTICE_SPECS[dimension]
        self.d = self.spec.dimension
        self.c = custom_c if custom_c is not None else self.spec.boundary_offset

    def base_density(self) -> float:
        """Infinite-lattice base packing density eta_0(d)."""
        return self.spec.base_density

    def interstitial_density(self, generations: int = 1) -> float:
        """
        Bulk density after filling interstitial lattice voids up to `generations`.
        Supports Gen 0 (base) and Gen 1 (primary deep holes).
        """
        if generations == 0:
            return self.spec.base_density
        if generations == 1:
            added_ratio = self.spec.holes_per_sphere * (self.spec.hole_radius ** self.d)
            return self.spec.base_density * (1.0 + added_ratio)
        raise ValueError("Analytical deep-hole table supports generations 0 or 1.")

    def gen1_boost(self) -> float:
        """Absolute efficiency gain (eta_1 - eta_0) from Gen 1 interstitial filling."""
        return self.interstitial_density(1) - self.base_density()

    def sphere_count(self, R: float, generations: int = 0) -> int:
        """Predicted integer sphere count n_d(R) inside container radius ratio R."""
        if R <= self.c:
            return 0
        eta_bulk = self.interstitial_density(generations)
        return int(math.floor(eta_bulk * ((R - self.c) ** self.d)))

    def finite_efficiency(self, R: float, generations: int = 0) -> float:
        """Discrete sawtooth efficiency eta_d(R) including integer jumps."""
        if R <= 0:
            return 0.0
        n = self.sphere_count(R, generations=generations)
        return n / (R ** self.d)

    def peak_envelope(self, R: float, generations: int = 0) -> float:
        """Smooth upper-bound efficiency envelope without floor jumps."""
        if R <= self.c:
            return 0.0
        eta_bulk = self.interstitial_density(generations)
        return eta_bulk * ((1.0 - (self.c / R)) ** self.d)

    def min_radius_for_retention(self, alpha: float = 0.90) -> float:
        """Minimum container radius R needed to retain fraction `alpha` of bulk limit."""
        if not (0.0 < alpha < 1.0):
            raise ValueError("alpha must be strictly between 0 and 1.")
        return self.c / (1.0 - (alpha ** (1.0 / self.d)))


def print_dimensional_summary() -> None:
    """Print comparison table across all supported dimensions."""
    header = f"{'Dim':<5} | {'Lattice':<18} | {'Base eta0':<10} | {'Gen1 eta1':<10} | {'Boost':<9} | {'R_min (90%)':<11}"
    print(header)
    print("-" * len(header))
    for d in [2, 3, 4, 8, 24]:
        m = FDIPModel(d)
        eta0 = m.base_density() * 100
        eta1 = m.interstitial_density(1) * 100
        boost = m.gen1_boost() * 100
        r_min = m.min_radius_for_retention(0.90)
        print(f"{d:<5} | {m.spec.name:<18} | {eta0:>8.4f}% | {eta1:>8.4f}% | +{boost:>6.4f}% | {r_min:>10.2f}")


def plot_fdip_analysis(save_path: str = "fdip_analysis.png") -> None:
    """Generate two-panel visualization of 2D sawtooth jumps and dimensional boundary retention."""
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2))

    # Panel 1: 2D Unified Sawtooth Efficiency vs. Smooth Envelope
    m2 = FDIPModel(2)
    r_vals = np.linspace(2.0, 11.0, 1200)
    sawtooth = [m2.finite_efficiency(r, generations=0) * 100 for r in r_vals]
    envelope = [m2.peak_envelope(r, generations=0) * 100 for r in r_vals]

    axes[0].plot(r_vals, sawtooth, label="Unified Floor Model (With Jumps)", color="#2563eb", linewidth=1.4)
    axes[0].plot(r_vals, envelope, "--", label="Smooth Peak Envelope", color="#f97316", linewidth=2.0)
    axes[0].axhline(m2.base_density() * 100, color="#16a34a", linestyle=":", label="Hexagonal Limit (90.69%)")
    axes[0].set_title("2D Unified Efficiency & Sawtooth Jumps")
    axes[0].set_xlabel("Container Radius Ratio (R)")
    axes[0].set_ylabel("Packing Efficiency (%)")
    axes[0].set_ylim(45, 95)
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(loc="lower right", fontsize=8.5)

    # Panel 2: Boundary Volume Retention Across Dimensions
    r_dim = np.linspace(2.0, 50.0, 500)
    colors = {2: "#2563eb", 3: "#0891b2", 4: "#7c3aed", 8: "#ea580c", 24: "#dc2626"}
    for d in [2, 3, 4, 8, 24]:
        md = FDIPModel(d)
        retention = [((1.0 - md.c / r) ** d) * 100 for r in r_dim]
        axes[1].plot(r_dim, retention, label=f"{d}D ({md.spec.name})", color=colors[d], linewidth=2.0)

    axes[1].axhline(90.0, color="#374151", linestyle="--", linewidth=1.2, label="90% Bulk Retention")
    axes[1].set_title("Boundary Volume Retention (1 - c/R)^d Across Dimensions")
    axes[1].set_xlabel("Container Radius Ratio (R)")
    axes[1].set_ylabel("Fraction of Bulk Limit Retained (%)")
    axes[1].set_ylim(0, 102)
    axes[1].grid(True, alpha=0.3)
    axes[1].legend(loc="lower right", fontsize=8.5)

    plt.tight_layout()
    plt.savefig(save_path, dpi=200)
    print(f"Saved plot to {save_path}")


if __name__ == "__main__":
    print_dimensional_summary()
    plot_fdip_analysis()
