# Versight AI - Deepfake Detection System Installation Guide (v3.1.0)

This document provides absolute technical clarity for installing, configuring, and maintaining the **Versight AI** forensic platform. 

## 🏗 System Overview
Versight AI is a dual-layered forensic system combining high-level Visual Context (Gemini 2.0) with low-level Signal Analysis (PyTorch). It is designed to detect manipulated media where high-level semantic logic may be perfect but low-level sensor physics are broken.

---

## 🛠 Prerequisites & Environment

### 🐍 Python Environment (Backend)
- **Version**: **Python 3.11.9** (Exact match recommended).
- **Architecture**: 64-bit.
- **Key Dependencies**:
  - `torch 2.11.0` + `torchvision 0.26.0` (Core ML)
  - `transformers 5.5.4` (HuggingFace Integration)
  - `facenet-pytorch 2.6.0` (MTCNN Face Detection)
  - `fastapi 0.135.3` (API Layer)
  - `opencv-python 4.11.0.86` (Frame processing)

### ⚛️ Node.js Environment (Frontend)
- **Version**: **Node.js 18.x** or **20.x**.
- **Package Manager**: `npm`.
- **Key Dependencies**:
  - `react 19.x`
  - `vite 8.x`
  - `framer-motion 12.x` (UI Animations)
  - `tailwindcss 4.x`

### 💻 Hardware Requirements
| Resource | Minimum | Recommended | 
| :--- | :--- | :--- |
| **System RAM** | 16 GB | 32 GB |
| **GPU** | CPU Only (Functional) | NVIDIA GPU (8GB+ VRAM) | 
| **Disk Space** | 5 GB | 10 GB (for model caching) |
| **Connectivity** | 10 Mbps | 100 Mbps (for initial model pull) |

---

## 🚀 Installation & Setup

### 1. Repository Initializations
```bash
git clone <repository-url>
cd versight
```

### 2. Forensic Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate # Unix

# Install foundational ML stack
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Integrated Frontend Setup
```bash
cd ../frontend
npm install
```

### 4. Configuration (`.env`)
Create `backend/.env` with the following:
```env
GEMINI_API_KEY=AIza... (Your Google AI Studio Key)
# HF_TOKEN=(Optional) For faster/authenticated HuggingFace model pulls
```

---

## 🔦 Forensic Layers Breakdown
Versight utilizes a 9-layer forensic audit. Understanding these is key to interpreting results:

1.  **Neural Artifacts (ViT)**: Uses an 11-view TTA ensemble to detect generative noise in facial regions.
2.  **Frequency Domain (DCT)**: Detects abnormal energy ratios in high-frequency spectrums (typical of GANs).
3.  **Temporal Consistency**: Analyzes frame-to-frame variance (Flicker Index) and sign changes in probability.
4.  **Physiological Pulse (rPPG)**: Extracts blood volume pulses from skin regions using the CHROM method.
5.  **Ocular Symmetry**: Analyzes physics consistency of eye reflections using Gini coefficients.
6.  **Compression Artifacts**: Detects double-quantization patterns common in deepfake re-renders.
7.  **Optical Flow**: Uses Farneback motion tracking to find discontinuities at face boundaries.
8.  **Noise Residual (PRNU)**: Analyzes the absence of natural sensor-specific noise patterns.
9.  **Spectral Decay**: Checks if the image follows the natural 1/f power law for light distribution.

---

## 🏃 Running the Platform

### Unified Startup (Recommended)
This uses our built-in Node orchestrator to launch both services, handle logging, and clear ports:
```bash
node start
```

### Developer Mode (Manual)
**Backend:**
```bash
cd backend && venv\Scripts\activate
uvicorn main:app --reload --port 8010
```
**Frontend:**
```bash
cd frontend
npm run dev
```

---

## 🛠 Maintenance & Troubleshooting

### Deep Cleanup Utility
If you encounter port conflicts or ghost processes holding GPU memory, run:
- **Windows**: `cleanup.bat`
- **Unix**: `kill -9 $(lsof -t -i:8010 -i:5173)`

### First-Run Model Downloads
On the first analysis, Versight will download:
- `prithivMLmods/Deep-Fake-Detector-v2-Model` (~1.2GB)
- `umm-maybe/AI-image-detector` (~400MB)
- `facenet-pytorch/MTCNN` weights

### Developer Verification
To verify the forensic layers independently, run:
```bash
python backend/test_new_metrics.py
```

---

## 🔒 Security Best Practices
- **API Safety**: Never commit your `.env` file. It is already added to `.gitignore`.
- **Upload Storage**: Temporary video files are stored in `temp_uploads/` and are automatically deleted after analysis. If the server crashes, run `cleanup.bat` to clear the cache.
