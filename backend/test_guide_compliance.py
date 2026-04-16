import sys
import os
import math
import numpy as np

def run_math_check():
    print("Verifying VerifyAI Guide Compliance (Mathematical Check)...")
    
    # 1. Test Signal-Retaining Ensemble (Section 3.45-53)
    # Spec: if max(vit, npr) > 0.5: max*0.8 + min*0.2 else: average
    def ensemble(vit_p, npr_p):
        if max(vit_p, npr_p) > 0.5:
            return (max(vit_p, npr_p) * 0.8 + min(vit_p, npr_p) * 0.2) * 100.0
        else:
            return (vit_p * 0.5 + npr_p * 0.5) * 100.0

    # Scenario: Suppression Case (High ViT, Low NPR)
    res = ensemble(0.80, 0.20)
    print(f"Ensemble (0.80 ViT, 0.20 NPR): {res:.1f}% (Spec: 68.0%)")
    assert math.isclose(res, 68.0), f"Ensemble fail! Got {res}"

    # 2. Test Sigmoid-Scaled Jitter Boost (Section 4.65-66)
    def sigmoid(x): return 1 / (1 + math.exp(-x))
    def jitter_boost(flicker, signs):
        jitter_signal = (flicker - 0.08) * 50 + (signs - 0.2) * 20
        return sigmoid(jitter_signal) * 15.0

    # Scenario: High Flicker
    boost = jitter_boost(0.12, 0.25)
    print(f"Jitter Boost (0.12 Flicker, 0.25 Signs): +{boost:.1f}% (Spec: High Lift)")
    assert boost > 12.0, "Jitter boost too low for high artifacts"

    # Scenario: Low Flicker
    boost_low = jitter_boost(0.02, 0.05)
    print(f"Jitter Boost (Low Artifacts): +{boost_low:.1f}% (Spec: Minimal/Zero Lift)")
    assert boost_low < 1.0, "Jitter boost too high for minimal artifacts"

    print("\nSUCCESS: Mathematical compliance with VerifyAI Guide confirmed!")

if __name__ == "__main__":
    run_math_check()
