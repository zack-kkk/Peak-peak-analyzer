"""
PXRD Signal Processing & Peak-Matching Engine
---------------------------------------------
Extracts 2-theta peak positions using local maxima detection and compares
experimental diffraction scans against patented reference forms using
binary-search tolerance matching.
"""

import bisect
import io
import numpy as np
from scipy.signal import find_peaks
from typing import List, Dict, Any, Tuple


class PXRDAnalyzer:
    def __init__(self, tolerance: float = 0.1, prominence: float = 5.0):
        self.tolerance = tolerance
        self.prominence = prominence

    def parse_xy_file(self, file_bytes: bytes) -> Tuple[np.ndarray, np.ndarray]:
        """Parses .csv / .xy / .txt files containing 2-theta and Intensity columns."""
        content = file_bytes.decode("utf-8")
        two_theta, intensities = [], []

        for line in content.splitlines():
            line = line.strip()
            # Skip empty lines or header comments
            if not line or line.startswith("#") or line.startswith("//"):
                continue
            
            # Handle comma or space/tab separated values
            parts = line.replace(",", " ").split()
            if len(parts) >= 2:
                try:
                    theta = float(parts[0])
                    intensity = float(parts[1])
                    two_theta.append(theta)
                    intensities.append(intensity)
                except ValueError:
                    continue  # Skip header lines if text conversion fails

        return np.array(two_theta), np.array(intensities)

    def extract_peaks(self, two_theta: np.ndarray, intensities: np.ndarray) -> List[float]:
        """Identifies local maxima 2-theta positions from intensity arrays."""
        if len(intensities) == 0:
            return []

        # Normalize intensities to 0-100 range
        max_val = np.max(intensities)
        norm_intensities = (intensities / max_val * 100.0) if max_val > 0 else intensities

        # Find peak indices using SciPy
        peak_indices, _ = find_peaks(norm_intensities, prominence=self.prominence)
        
        # Round 2-theta positions to 2 decimal places
        extracted_peaks = [round(float(two_theta[i]), 2) for i in peak_indices]
        return sorted(extracted_peaks)

    def match_positions(self, exp_peaks: List[float], ref_peaks: List[float]) -> Dict[str, Any]:
        """
        Performs O(Log N) binary-search matching to classify experimental peaks into:
        1. Matched Peaks (falls within +/- tolerance)
        2. Unique/Novel Peaks (absent in reference patent)
        3. Missing Reference Peaks
        """
        sorted_ref = sorted(ref_peaks)
        matched = []
        unique_new = []
        ref_matched_flags = [False] * len(sorted_ref)

        for exp_p in exp_peaks:
            # Binary search insertion index
            idx = bisect.bisect_left(sorted_ref, exp_p)
            
            # Check candidate neighbors around insertion point
            candidates = []
            if idx > 0:
                candidates.append((abs(exp_p - sorted_ref[idx - 1]), idx - 1))
            if idx < len(sorted_ref):
                candidates.append((abs(exp_p - sorted_ref[idx]), idx))

            if candidates:
                min_dist, best_idx = min(candidates, key=lambda x: x[0])
                if min_dist <= self.tolerance:
                    matched.append({
                        "exp_peak": exp_p,
                        "ref_peak": sorted_ref[best_idx],
                        "delta": round(min_dist, 3)
                    })
                    ref_matched_flags[best_idx] = True
                else:
                    unique_new.append(exp_p)
            else:
                unique_new.append(exp_p)

        missing_ref = [sorted_ref[i] for i, flag in enumerate(ref_matched_flags) if not flag]

        match_score = (len(matched) / len(sorted_ref) * 100.0) if sorted_ref else 0.0

        return {
            "match_score_percentage": round(match_score, 1),
            "matched_peaks": matched,
            "unique_new_peaks": unique_new,
            "missing_ref_peaks": missing_ref,
            "is_potentially_novel": len(unique_new) > 0
        }
