# VerifyAI Forensic Model Implementation Guide (v3.0.1)

This guide provides the exact implementation logic for the **VerifyAI** forensic pipeline (comprised of `Cross-Efficient ViT` and `NPR ResNet50`) for use in similar deepfake detection projects.

## 1. System Architecture
The system uses a **Dual-Ensemble Approach** that combines structural facial landmarks with high-frequency noise analysis.

### Required Dependencies
```bash
pip install torch torchvision facenet-pytorch einops opencv-python pillow PyYAML yt-dlp
```

---

## 2. Model: NPR Detector (Image & Texture Forensics)
**Base**: ResNet50 (num_classes=1).
**Key Improvement**: **11-View Test Time Augmentation (TTA)**.

### Implementation Logic:
When scoring an image, derive 11 views to detect artifacts at multiple scales:
1.  **Original** (1x)
2.  **Horizontal Flip** (1x)
3.  **Center Crops** @ 90% & 80% (2x)
4.  **Flipped Crops** @ 90% & 80% (2x)
5.  **JPEG Re-compression** @ Quality 85 (1x)
6.  **Brightness/Contrast Boost** @ 1.1x (2x)
7.  **Sharpen/Blur Filters** (2x)

> [!IMPORTANT]
> Use **Weighted Mean Pooling** for TTA results.
> `weights = results + 0.1` (this biases the result toward detecting manipulations rather than missing them).

---

## 3. Model: Video Forensic Detector (Video & Face Forensics)
**Base**: Cross-Efficient Vision Transformer (ViT).
**Pre-processing**: MTCNN for face detection (Margin: 60%, Threshold: 0.70).

### Implementation Logic:
1.  **Temporal Sampling**: Extract 128 frames (maximum coverage).
2.  **Face-Aware ViT TTA**: Score every detected face along with its **Horizontal Flip**.
3.  **Dual Forward Pass**: For every face crop, run *both* the ViT transformation and the NPR texture analysis.

### Signal-Retaining Ensemble (Critical)
To prevent "Signal Suppression" (where a real-looking background hides a fake face), use **Confidence-Weighted Max Pooling**:

```python
# Weighted Max - preserving high-confidence flags
if max(vit_score, npr_score) > 0.5:
    combined_prob = max(vit_score, npr_score) * 0.8 + min(vit_score, npr_score) * 0.2
else:
    combined_prob = vit_score * 0.5 + npr_score * 0.5
```

---

## 4. Advanced Temporal Aggregation
The final video score is **not** a simple average. Follow these steps:

1.  **3-Frame Rolling Average**: Smooth out per-frame scores to eliminate single-frame glitches.
2.  **Attention Cluster**: Aggregate only the **Top 30% of highest signals**. This captures short deepfake segments.
3.  **Flicker Index Logic**:
    -   Calculate `std(diff(probabilities))`.
    -   Calculate `sign_changes` (slope flipping count).
4.  **Jitter-Triggered Boost**:
    If `flicker_index > 0.08` or `sign_changes > 0.2`, apply a sigmoid-scaled probability lift to ensure frame-level generation artifacts trigger a detection even if single-frame textures are "clean."

---

## 5. Summary Response Metadata
To maintain forensic integrity, the response object must contain:
- `probability`: Final aggregated and boosted score (0.0 to 1.0).
- `flicker_index`: Temporal variance measure.
- `discrepancy_score`: Face-vs-Background texture mismatch.
- `faces_detected`: Count of faces scanned.
- `tta_coverage`: Number of augmented views analyzed.

---

> [!TIP]
> **Why this works**: By combining a **Structural-Aware Transformer** (ViT) with a **Texture-Aware CNN** (NPR), you create a system that catches both high-level face swaps and low-level generative noise.
