import torch
import json
import torch.nn as nn
import torchvision.models as models
import torch.nn.functional as F_torch
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.cm as cm
import torchvision.transforms as transforms
from transformers import AutoModelForImageClassification, AutoImageProcessor
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
import os
import math
import base64
import io
import time
from google import genai
import concurrent.futures
from facenet_pytorch import MTCNN
from dotenv import load_dotenv
from scipy import stats as sp_stats

load_dotenv()

# Client will be initialized in __init__ using environment variables
pass

class DeepfakeDetector:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"[VERSIGHT] Using device: {self.device}")

        # ── Pretrained Deepfake Detection Model (HuggingFace) ──
        hf_model_name = "prithivMLmods/Deep-Fake-Detector-v2-Model"
        print(f"[VERSIGHT] Loading pretrained deepfake detector: {hf_model_name}")
        self.detector_model = AutoModelForImageClassification.from_pretrained(hf_model_name, attn_implementation='eager')
        self.detector_processor = AutoImageProcessor.from_pretrained(hf_model_name)
        self.detector_model.to(self.device).eval()
        
        # Get label mapping from the model config
        self.label_map = self.detector_model.config.id2label
        # Find which label index corresponds to "Fake"/"Deepfake"
        self.fake_idx = None
        for idx, label in self.label_map.items():
            if 'fake' in label.lower() or 'deepfake' in label.lower() or 'synthetic' in label.lower():
                self.fake_idx = int(idx)
                break
        if self.fake_idx is None:
            # Default to index 1 if we can't find it
            self.fake_idx = 1
        print(f"[VERSIGHT] Label map: {self.label_map}, Fake index: {self.fake_idx}")

        # Ensure compatibility with Guide: NPR ResNet50 (texture) + ViT (Structural)
        # We are using Deep-Fake-Detector-v2 (ViT) and AI-image-detector (NPR-like texture)

        # ── Fast MTCNN Face Detector ──
        self.mtcnn = MTCNN(keep_all=True, device=self.device, thresholds=[0.7, 0.8, 0.8])

        # ── LLM Logical Forensics (Unified SDK) ──
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.gemini_model_name = "gemini-2.0-flash"

        # ── General AI Image Detector (works on ALL content, not just faces) ──
        gen_model_name = "umm-maybe/AI-image-detector"
        print(f"[VERSIGHT] Loading general AI image detector: {gen_model_name}")
        self.gen_detector = AutoModelForImageClassification.from_pretrained(gen_model_name)
        self.gen_processor = AutoImageProcessor.from_pretrained(gen_model_name)
        self.gen_detector.to(self.device).eval()
        self.gen_label_map = self.gen_detector.config.id2label
        # Find the "artificial" index
        self.gen_fake_idx = 0  # Default
        for idx, label in self.gen_label_map.items():
            if 'artificial' in label.lower() or 'ai' in label.lower() or 'fake' in label.lower():
                self.gen_fake_idx = int(idx)
                break
        print(f"[VERSIGHT] General AI detector labels: {self.gen_label_map}, Artificial index: {self.gen_fake_idx}")
        
        print("[VERSIGHT] Advanced Forensics Engine Loaded (Pretrained + General AI + DCT + PRNU + Spectral + Compression + OpticalFlow).")

    # ── TTA Views ──
    def get_tta_views(self, face_pil):
        import torchvision.transforms.functional as F
        w, h = face_pil.size
        # Protect against tiny crops breaking center_crop
        w_90, h_90 = max(1, int(w * 0.9)), max(1, int(h * 0.9))
        w_80, h_80 = max(1, int(w * 0.8)), max(1, int(h * 0.8))
        
        views = [face_pil]
        views.append(F.hflip(face_pil))
        views.append(F.center_crop(face_pil, (h_90, w_90)))
        views.append(F.center_crop(face_pil, (h_80, w_80)))
        views.append(F.hflip(F.center_crop(face_pil, (h_90, w_90))))
        views.append(F.hflip(F.center_crop(face_pil, (h_80, w_80))))
        
        buf = io.BytesIO()
        face_pil.save(buf, format="JPEG", quality=85)
        views.append(Image.open(buf).copy())
        
        views.append(ImageEnhance.Brightness(face_pil).enhance(1.1))
        views.append(ImageEnhance.Contrast(face_pil).enhance(1.1))
        
        views.append(face_pil.filter(ImageFilter.SHARPEN))
        views.append(face_pil.filter(ImageFilter.GaussianBlur(1.0)))
        
        return views

    # ── Pretrained Model Evaluation with TTA ──
    def evaluate_face(self, face_pil):
        """Evaluate a face crop using the pretrained HuggingFace deepfake detector with TTA.
        Returns (score, heatmap_base64)."""
        tta_views = self.get_tta_views(face_pil)
        
        fake_probs = []
        for view in tta_views:
            inputs = self.detector_processor(images=view, return_tensors="pt").to(self.device)
            with torch.no_grad():
                outputs = self.detector_model(**inputs)
                probs = torch.softmax(outputs.logits, dim=-1).cpu().numpy().flatten()
                fake_prob = float(probs[self.fake_idx])
                fake_probs.append(fake_prob)
        
        fake_probs = np.array(fake_probs)
        # Weighted mean pooling — reduced bias for robustness (results + 0.05)
        # unless detecting high variance (potential manipulation)
        bias = 0.1 if np.max(fake_probs) > 0.7 else 0.05
        weighted_score = float(np.average(fake_probs, weights=fake_probs + bias))
        
        # Generate attention heatmap from the original (un-augmented) view
        heatmap_b64 = self.generate_heatmap(face_pil)
        
        return weighted_score, heatmap_b64

    # ── Attention Heatmap Generation ──
    def generate_heatmap(self, face_pil):
        """Extract ViT attention maps and overlay as a heatmap on the face crop."""
        try:
            inputs = self.detector_processor(images=face_pil, return_tensors="pt").to(self.device)
            with torch.no_grad():
                outputs = self.detector_model(**inputs, output_attentions=True)
            
            # outputs.attentions is a tuple of (num_layers,) tensors
            # Each tensor shape: (batch, num_heads, seq_len, seq_len)
            # seq_len = num_patches + 1 (CLS token)
            # We use the last layer's attention from the CLS token to all patches
            last_attn = outputs.attentions[-1]  # (1, 12, 197, 197) for ViT-B/16
            
            # Average across all attention heads
            attn_heads_avg = last_attn.mean(dim=1)  # (1, 197, 197)
            
            # CLS token attention to all patch tokens (skip CLS-to-CLS at index 0)
            cls_attn = attn_heads_avg[0, 0, 1:]  # (196,) = 14x14 patches
            
            # Reshape to 14x14 spatial grid
            grid_size = int(cls_attn.shape[0] ** 0.5)  # 14
            attn_map = cls_attn.reshape(grid_size, grid_size).cpu().numpy()
            
            # Normalize to 0-1
            attn_map = (attn_map - attn_map.min()) / (attn_map.max() - attn_map.min() + 1e-8)
            
            # Upscale to original face crop size (preserve aspect ratio)
            orig_w, orig_h = face_pil.size
            face_np = np.array(face_pil)
            attn_upscaled = cv2.resize(attn_map, (orig_w, orig_h), interpolation=cv2.INTER_CUBIC)
            
            # Apply colormap (red = high attention = suspected fake region)
            colormap = cm.get_cmap('jet')
            heatmap_rgba = colormap(attn_upscaled)  # (224, 224, 4) float 0-1
            heatmap_rgb = (heatmap_rgba[:, :, :3] * 255).astype(np.uint8)
            
            # Overlay heatmap on face at 40% opacity
            overlay = cv2.addWeighted(face_np, 0.6, heatmap_rgb, 0.4, 0)
            
            # Encode as base64
            overlay_pil = Image.fromarray(overlay)
            buf = io.BytesIO()
            overlay_pil.save(buf, format="JPEG", quality=80)
            return base64.b64encode(buf.getvalue()).decode("utf-8")
        except Exception as e:
            print(f"[VERSIGHT] Heatmap generation error: {e}")
            return None

    # ── DCT Frequency Domain Analysis (Priority 2) ──
    def frequency_analysis(self, face_pil):
        """Detect GAN fingerprints via DCT high-frequency energy ratio."""
        face_np = np.array(face_pil)
        gray = cv2.cvtColor(face_np, cv2.COLOR_RGB2GRAY).astype(np.float32)
        
        # Resize to power-of-2 for clean DCT
        gray = cv2.resize(gray, (256, 256))
        dct = cv2.dct(gray)
        
        h, w = dct.shape
        # GAN-generated faces have abnormal high-frequency energy patterns
        high_freq_region = dct[h // 2:, w // 2:]
        total_energy = np.sum(np.abs(dct)) + 1e-8
        high_freq_energy = np.sum(np.abs(high_freq_region))
        energy_ratio = high_freq_energy / total_energy
        
        # Scale to 0-100 range — higher = more likely manipulated
        # Real faces typically have energy_ratio around 0.05-0.15
        # GAN faces often show 0.02-0.06 (suspiciously low) or >0.20 (artifact noise)
        # Deviation from natural range indicates manipulation
        natural_center = 0.10
        deviation = abs(energy_ratio - natural_center)
        score = min(100.0, deviation * 500.0)  # Scale deviation to 0-100
        
        return float(score)

    # ── Compression Artifact Detection (Priority 3) ──
    def compression_analysis(self, face_pil):
        """Detect double-JPEG compression artifacts indicating manipulation."""
        buf_high = io.BytesIO()
        buf_low = io.BytesIO()
        face_pil.save(buf_high, format="JPEG", quality=95)
        face_pil.save(buf_low, format="JPEG", quality=50)
        
        img_high = np.array(Image.open(buf_high)).astype(float)
        img_low = np.array(Image.open(buf_low)).astype(float)
        original = np.array(face_pil).astype(float)
        
        # Double-compressed images show characteristic degradation patterns
        diff_high = np.mean(np.abs(original - img_high))
        diff_low = np.mean(np.abs(original - img_low))
        
        # Ratio of high-quality vs low-quality degradation
        # Manipulated images often show unusual compression behavior
        ratio = diff_high / (diff_low + 1e-8)
        
        # Scale to 0-100 — higher = more suspicious compression behavior
        score = min(100.0, ratio * 100.0)
        return float(score)

    # ── Optical Flow Temporal Analysis (Priority 4) ──
    def optical_flow_consistency(self, prev_gray, curr_gray):
        """Detect unnatural motion patterns between consecutive frames."""
        # Resize for consistent analysis
        prev_resized = cv2.resize(prev_gray, (320, 240))
        curr_resized = cv2.resize(curr_gray, (320, 240))
        
        flow = cv2.calcOpticalFlowFarneback(
            prev_resized, curr_resized, None,
            pyr_scale=0.5, levels=3, winsize=15,
            iterations=3, poly_n=5, poly_sigma=1.2, flags=0
        )
        
        magnitude = np.sqrt(flow[..., 0] ** 2 + flow[..., 1] ** 2)
        
        # Deepfakes often have unnaturally uniform flow in face regions
        # or sudden discontinuities at face boundaries
        flow_std = float(np.std(magnitude))
        flow_mean = float(np.mean(magnitude))
        
        # Coefficient of variation — low CoV = suspiciously uniform motion
        cov = flow_std / (flow_mean + 1e-8)
        
        return flow_std, cov

    # ── General AI Image Classifier (Priority 5 — whole frame) ──
    def evaluate_frame_general(self, frame_pil):
        """Classify an entire frame as human/natural vs AI-generated.
        Works on any content — landscapes, objects, planes, etc."""
        try:
            inputs = self.gen_processor(images=frame_pil, return_tensors="pt").to(self.device)
            with torch.no_grad():
                outputs = self.gen_detector(**inputs)
            probs = F_torch.softmax(outputs.logits, dim=-1)
            artificial_prob = float(probs[0, self.gen_fake_idx].item())
            return artificial_prob * 100.0  # 0-100 scale
        except Exception as e:
            err_msg = f"General AI detection error: {e}"
            print(f"[VERSIGHT] {err_msg}")
            with open("error_debug.txt", "a") as f: f.write(err_msg + "\n")
            return 0.0

    # ── Noise Residual Analysis / PRNU (Priority 6) ──
    def noise_residual_analysis(self, frame_np):
        """Detect absence of camera sensor noise (PRNU).
        Real camera images have structured, sensor-specific noise patterns.
        AI-generated images have flat/synthetic/uniform noise."""
        try:
            # Convert to grayscale float
            if len(frame_np.shape) == 3:
                gray = cv2.cvtColor(frame_np, cv2.COLOR_RGB2GRAY).astype(np.float64)
            else:
                gray = frame_np.astype(np.float64)
            
            # Resize for consistent analysis
            gray = cv2.resize(gray, (512, 512))
            
            # Extract noise residual: original - denoised
            denoised = cv2.GaussianBlur(gray, (5, 5), 1.5)
            residual = gray - denoised
            
            # Metric 1: Kurtosis of noise distribution
            # Real sensor noise has specific kurtosis; AI noise is more Gaussian (kurtosis ~0)
            noise_kurtosis = float(sp_stats.kurtosis(residual.flatten()))
            
            # Metric 2: Spatial variance of local noise power
            # Real cameras: noise varies with brightness (Poisson-like), creating spatial structure
            # AI: noise is uniform across the image
            local_var = cv2.blur(residual**2, (16, 16)) - cv2.blur(residual, (16, 16))**2
            var_of_var = float(np.std(local_var))
            
            # Metric 3: Noise magnitude
            noise_std = float(np.std(residual))
            
            # Combine: low kurtosis + low var_of_var + low noise = likely AI
            # Real cameras: var_of_var ~2-5, kurtosis ~3-10, noise_std ~3-8
            # AI images: var_of_var ~0.1-0.8, kurtosis ~0-2, noise_std ~0.5-2
            
            vov_score = max(0, min(100, (1.0 - min(var_of_var, 3.0) / 3.0) * 60))
            kurt_score = max(0, min(100, (1.0 - min(abs(noise_kurtosis), 8.0) / 8.0) * 40))
            
            # If noise is extremely low, the image is likely rendered/AI
            if noise_std < 1.0:
                vov_score = max(vov_score, 70)
            
            return float(vov_score + kurt_score)
        except Exception as e:
            err_msg = f"Noise residual error: {e}"
            print(f"[VERSIGHT] {err_msg}")
            with open("error_debug.txt", "a") as f: f.write(err_msg + "\n")
            return 0.0

    # ── Spectral Decay Analysis (Priority 7 — 1/f power law) ──
    def spectral_decay_analysis(self, frame_np):
        """Check if image follows the natural 1/f spectral decay law.
        Real photographs have a power spectrum that falls off as 1/f.
        AI-generated images often have flatter or steeper spectral slopes."""
        try:
            if len(frame_np.shape) == 3:
                gray = cv2.cvtColor(frame_np, cv2.COLOR_RGB2GRAY)
            else:
                gray = frame_np
            
            # Resize for consistent/fast FFT
            gray = cv2.resize(gray, (256, 256)).astype(np.float64)
            
            # 2D FFT
            f_transform = np.fft.fft2(gray)
            f_shift = np.fft.fftshift(f_transform)
            magnitude = np.abs(f_shift)
            
            # Radial average of power spectrum
            h, w = magnitude.shape
            cy, cx = h // 2, w // 2
            max_r = min(cy, cx)
            
            radial_profile = []
            for r in range(1, max_r):
                # Create circular mask at radius r
                y, x = np.ogrid[-cy:h-cy, -cx:w-cx]
                mask = (x**2 + y**2 >= (r-1)**2) & (x**2 + y**2 < r**2)
                radial_profile.append(np.mean(magnitude[mask]))
            
            radial_profile = np.array(radial_profile)
            
            # Fit log-log slope (natural images have slope ~ -1.0)
            freqs = np.arange(1, len(radial_profile) + 1).astype(np.float64)
            log_freqs = np.log(freqs)
            log_power = np.log(radial_profile + 1e-10)
            
            # Linear regression on log-log plot
            slope, _, _, _, _ = sp_stats.linregress(log_freqs, log_power)
            
            # Natural images: slope ~ -1.0 to -1.5
            # AI images: slope often ~ -0.5 to -0.8 (flatter) or > -2.0 (steeper)
            # Score: deviation from natural slope (-1.0)
            deviation = abs(slope - (-1.0))
            score = min(100.0, deviation * 80.0)  # Scale deviation to 0-100
            
            return float(score)
        except Exception as e:
            err_msg = f"Spectral decay error: {e}"
            print(f"[VERSIGHT] {err_msg}")
            with open("error_debug.txt", "a") as f: f.write(err_msg + "\n")
            return 0.0

    def calculate_gini(self, data):
        """Calculates Gini coefficient for light distribution (Physics Forensic)"""
        if len(data) == 0: return 0.0
        x = np.sort(data.flatten().astype(np.float64))
        n = len(x)
        if np.sum(x) == 0: return 0.0
        index = np.arange(1, n + 1)
        return (np.sum((2 * index - n - 1) * x)) / (n * np.sum(x))

    def extract_rppg_bvp(self, rgb_seq, fps):
        """Extracts Blood Volume Pulse using CHROM method (Physiological Forensic)"""
        if len(rgb_seq) < 10: return np.array([0.0])
        rgb_mean = np.mean(rgb_seq, axis=0)
        rgb_norm = rgb_seq / (rgb_mean + 1e-6)
        xs = 3 * rgb_norm[:, 0] - 2 * rgb_norm[:, 1]
        ys = 1.5 * rgb_norm[:, 0] + rgb_norm[:, 1] - 1.5 * rgb_norm[:, 2]
        
        # Bandpass filter for physiological range (0.7-3.0 Hz / 42-180 BPM)
        from scipy import signal
        nyq = 0.5 * fps
        b, a = signal.butter(3, [max(0.01, 0.7/nyq), min(0.99, 3.0/nyq)], btype='bandpass')
        xs_f = signal.filtfilt(b, a, xs)
        ys_f = signal.filtfilt(b, a, ys)
        
        alpha = np.std(xs_f) / (np.std(ys_f) + 1e-6)
        return xs_f - alpha * ys_f

    def ocular_symmetry_analysis(self, face_pil):
        """Analyzes eye reflection (catchlight) consistency via Gini coefficient"""
        w, h = face_pil.size
        # Estimate eye locations (top-ish left and right)
        left_eye_roi = face_pil.crop((int(w*0.2), int(h*0.2), int(w*0.45), int(h*0.45)))
        right_eye_roi = face_pil.crop((int(w*0.55), int(h*0.2), int(w*0.8), int(h*0.45)))
        
        l_arr = np.array(left_eye_roi.convert('L'))
        r_arr = np.array(right_eye_roi.convert('L'))
        
        gini_l = self.calculate_gini(l_arr)
        gini_r = self.calculate_gini(r_arr)
        
        symmetry_diff = abs(gini_l - gini_r)
        
        # Anomaly if reflections are wildly asymmetric or perfectly identical (suspicious tiling)
        if symmetry_diff > 0.15: return 85.0 # Mismatched physics
        if symmetry_diff < 0.001: return 60.0 # Suspiciously mirrored/tiled
        return max(0.0, min(100.0, symmetry_diff * 400)) # Scaled score

    def physiological_pulse_analysis(self, rgb_sequence, fps):
        """Analyzes heart rate stability across video segments"""
        if len(rgb_sequence) < 30: return 20.0 # Not enough data = moderate suspicion
        
        try:
            bvp = self.extract_rppg_bvp(rgb_sequence, fps)
            
            # Compute Signal-to-Noise Ratio (SNR) of the heart rate peak
            from scipy import signal
            freqs, psd = signal.welch(bvp, fs=fps, nperseg=len(bvp))
            
            # Find peak in human HR range
            mask = (freqs >= 0.7) & (freqs <= 3.0)
            if not np.any(mask): return 90.0
            
            target_psd = psd[mask]
            peak_idx = np.argmax(target_psd)
            peak_energy = target_psd[peak_idx]
            total_energy = np.sum(target_psd)
            
            snr = peak_energy / (total_energy - peak_energy + 1e-6)
            
            # Humans have stable peaks (SNR > 0.1 depending on quality). AI is chaotic noise.
            if snr < 0.06: return 95.0 # Confident pulse absence / Synthetic
            if snr < 0.15: return 75.0 # Suspiciously weak/noisy signal
            
            # Map high SNR (real pulse) to low score (0-30), Low SNR to high score
            score = max(0.0, min(100.0, 40.0 - (snr * 100))) 
            return float(score)
        except:
            return 30.0 # Error fallback

    @staticmethod
    def img_to_base64(pil_img, max_size=160):
        pil_img.thumbnail((max_size, max_size), Image.LANCZOS)
        buf = io.BytesIO()
        pil_img.save(buf, format="JPEG", quality=70)
        return base64.b64encode(buf.getvalue()).decode("utf-8")

    def logical_forensics_video(self, video_path):
        prompt = """
You are an elite visual forensics AI. I am providing you with a full video recording.
Your job is to act as a deepfake visual fact-checker. You must heavily scrutinize the CONTEXT, PHYSICS, and UNCANNY VISUALS of the scene.
Are the facial features too perfect, shiny, or unnaturally smoothed? Do the eyes/teeth look synthetic? Does the lighting on the subject truly match the background? Are the facial expressions slightly robotic, "uncanny", or AI-generated? Pay special attention to temporal consistency and physics across the whole video.

Respond STRICTLY with a JSON object containing exactly two keys:
1. "logical_reasoning": A 2-3 sentence paragraph explaining your visual analysis and why it looks natural or synthetic.
2. "anomaly_score": An integer from 0 to 100, where 100 heavily implies the face/context is AI-generated, synthetic, or manipulated, and 0 implies it is a 100% natural, unaltered physical camera recording.

Do not use markdown formatting like ```json. Output raw JSON ONLY.
"""
        try:
            print(f"[VERSIGHT] Uploading full video to Gemini File API (Unified SDK)...")
            video_file = self.client.files.upload(file=video_path)
            
            # Wait for processing
            while video_file.state == 'PROCESSING':
                time.sleep(2)
                video_file = self.client.files.get(name=video_file.name)
                
            if video_file.state == 'FAILED':
                raise Exception("Gemini failed to process the video.")
                
            response = self.client.models.generate_content(
                model=self.gemini_model_name,
                contents=[video_file, prompt]
            )
            
            # Cleanup
            self.client.files.delete(name=video_file.name)
            
            text = response.text.strip()
            if text.startswith("```json"): text = text[7:-3].strip()
            elif text.startswith("```"): text = text[3:-3].strip()
            data = json.loads(text)
            return float(data.get("anomaly_score", 50)), data.get("logical_reasoning", "Analysis unavailable.")
        except Exception as e:
            print(f"[VERSIGHT] Gemini Unified SDK Video Error: {e}")
            return 50.0, "Logical forensics unavailable due to an API error."

    def analyze_video(self, video_path: str):
        final_result = None
        for update in self.analyze_video_stream(video_path):
            if update.get("status") == "complete":
                final_result = update.get("result")
        return final_result

    def analyze_video_stream(self, video_path: str):
        if not os.path.exists(video_path):
            raise Exception("Video file not found")

        t_start = time.time()
        log_steps = []
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception("Could not open video file")

        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = total_frames / fps if fps > 0 else 0
        codec = "h264"
        
        yield {"status": "processing", "step": "Video loaded", "progress": 10, "details": f"{width}x{height} @ {fps:.1f}fps"}
        
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        gemini_future = executor.submit(self.logical_forensics_video, video_path)

        # Frame sampling
        num_sample = min(128, max(30, total_frames // max(1, int(fps))))
        indices = np.linspace(0, max(0, total_frames - 1), num_sample, dtype=int)
        
        yield {"status": "processing", "step": "Running Pretrained Forensic Analysis", "progress": 25, "details": f"Analyzing {num_sample} distributed frames with HuggingFace detector"}
        
        all_face_scores = []
        all_freq_scores = []
        all_comp_scores = []
        all_flow_stds = []
        all_flow_covs = []
        
        # New General Metrics 
        all_gen_scores = []
        all_noise_scores = []
        all_spec_scores = []
        face_crop_data = []  # Collect top face crops with heatmaps
        all_skin_rgbs = [] # For rPPG analysis
        all_eye_scores = []
        total_faces_scanned = 0
        prev_gray = None
        
        for p_idx, idx in enumerate(indices):
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
            ok, frame = cap.read()
            if not ok: break
            
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            curr_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            pil_frame = Image.fromarray(rgb)
            
            # ── Optical Flow (between consecutive sampled frames) ──
            if prev_gray is not None:
                try:
                    flow_std, flow_cov = self.optical_flow_consistency(prev_gray, curr_gray)
                    all_flow_stds.append(flow_std)
                    all_flow_covs.append(flow_cov)
                except Exception:
                    pass
            prev_gray = curr_gray
            # ── General Content Analysis (Every 3rd frame to save CPU) ──
            if p_idx % 3 == 0:
                gen_score = self.evaluate_frame_general(pil_frame)
                noise_score = self.noise_residual_analysis(rgb)
                spec_score = self.spectral_decay_analysis(rgb)
                all_gen_scores.append(gen_score)
                all_noise_scores.append(noise_score)
                all_spec_scores.append(spec_score)
                
                # Also collect frequency for whole frame if no faces are ever detected
                all_freq_scores.append(self.frequency_analysis(pil_frame))

            # ── Face Detection & Analysis ──
            boxes, _ = self.mtcnn.detect(pil_frame)
            
            frame_score = None
            if boxes is not None:
                total_faces_scanned += len(boxes)
                best_face_score = 0
                for box in boxes:
                    x1, y1, x2, y2 = [int(v) for v in box]
                    x1, y1 = max(0, x1), max(0, y1)
                    x2, y2 = min(width, x2), min(height, y2)
                    
                    if (x2 - x1) > 20 and (y2 - y1) > 20: 
                        face_crop = pil_frame.crop((x1, y1, x2, y2))
                        
                        # Pretrained deepfake detection with TTA + heatmap
                        prob, heatmap_b64 = self.evaluate_face(face_crop)
                        
                        # DCT frequency analysis
                        freq_score = self.frequency_analysis(face_crop)
                        all_freq_scores.append(freq_score)
                        
                        # Compression artifact analysis
                        comp_score = self.compression_analysis(face_crop)
                        all_comp_scores.append(comp_score)
                        
                        # Pupil Symmetry Forensic (Ocular)
                        eye_score = self.ocular_symmetry_analysis(face_crop)
                        all_eye_scores.append(eye_score)

                        # Extract skin RGB for rPPG
                        cw, ch = face_crop.size
                        # Multi-region skin ROI (cheeks + forehead)
                        fh = face_crop.crop((int(cw*0.3), int(ch*0.1), int(cw*0.7), int(ch*0.3))) # Forehead
                        ck = face_crop.crop((int(cw*0.2), int(ch*0.4), int(cw*0.8), int(ch*0.6))) # Cheeks
                        skin_data = np.concatenate([np.array(fh).reshape(-1, 3), np.array(ck).reshape(-1, 3)], axis=0)
                        all_skin_rgbs.append(np.mean(skin_data, axis=0))
                        
                        # Collect face crop data for top detections
                        if len(face_crop_data) < 8:  # Keep top 8 face crops
                            # Encode original at same size as heatmap (native dimensions)
                            buf_orig = io.BytesIO()
                            face_crop.save(buf_orig, format="JPEG", quality=80)
                            original_b64 = base64.b64encode(buf_orig.getvalue()).decode("utf-8")
                            
                            face_crop_data.append({
                                "frame_index": int(idx),
                                "score": round(prob * 100, 1),
                                "original": original_b64,
                                "heatmap": heatmap_b64,
                                "freq_score": round(float(freq_score), 1),
                                "comp_score": round(float(comp_score), 1),
                                "face_width": int(x2 - x1),
                                "face_height": int(y2 - y1),
                            })
                        
                        if prob > best_face_score:
                            best_face_score = prob
                        
                frame_score = best_face_score
            
            if frame_score is not None:
                all_face_scores.append(frame_score * 100.0)  # Scale to 0-100
            else:
                all_face_scores.append(25.0)  # Background fallback

            if p_idx % 15 == 0:
                yield {"status": "processing", "step": "11-View TTA Evaluation", "progress": min(95, 25 + int((p_idx/len(indices))*70)), "details": f"Analyzing frame {p_idx}/{len(indices)} with pretrained detector + DCT + compression"}
                
        cap.release()

        # ══════════════════════════════════════════
        # Aggregation Logic
        # ══════════════════════════════════════════
        scores_array = np.array(all_face_scores)
        if len(scores_array) == 0:
            scores_array = np.array([30.0])

        def rolling_avg(a, n=3):
            if len(a) < n: return a
            ret = np.cumsum(a, dtype=float)
            ret[n:] = ret[n:] - ret[:-n]
            return ret[n - 1:] / n

        smoothed = rolling_avg(scores_array, 3)
        top_k = max(1, int(len(smoothed) * 0.3))
        attention_cluster = np.sort(smoothed)[-top_k:]
        neural_score = float(np.mean(attention_cluster))
        
        # ── Temporal Flicker Analysis ──
        if len(scores_array) > 1:
            diffs = np.diff(scores_array)
            flicker_index = float(np.std(diffs))
            signs = np.sign(diffs)
            sign_changes = float(np.sum(signs[:-1] != signs[1:]) / len(diffs))
        else:
            flicker_index = sign_changes = 0.0
            
        # ── Temporal Consistency Score ──
        # Higher score = more consistent/natural. Lower score = flickery/suspicious.
        # flicker_index is std of frame diffs (0.02-0.12 range typical for handheld)
        # sign_changes is ratio of slope flips (0.1-0.4 range typical for handheld)
        temporal_score = max(0.0, 100.0 - (flicker_index * 300.0 + sign_changes * 80.0))
        
        # ── Jitter-Triggered Sigmoid Boost (Section 4.65-66) ──
        score_boost = 0.0
        if flicker_index > 0.08 or sign_changes > 0.3:
            # Sigmoid lift for temporal artifacts
            def sigmoid(x): return 1 / (1 + math.exp(-x))
            # Center sigmoid at handheld-tolerant thresholds
            jitter_signal = (flicker_index - 0.10) * 40 + (sign_changes - 0.35) * 15
            lift = sigmoid(jitter_signal) * 15.0  # Up to 15% lift
            score_boost = lift

        # ── Frequency Domain Score ──
        freq_score = float(np.mean(all_freq_scores)) if all_freq_scores else 0.0
        
        # ── Compression Score ──
        comp_score = float(np.mean(all_comp_scores)) if all_comp_scores else 15.0
        
        # ── Optical Flow Score ──
        # Low coefficient of variation = suspiciously uniform motion = more likely fake
        if all_flow_covs:
            avg_cov = float(np.mean(all_flow_covs))
            # Natural videos typically have CoV > 1.0, deepfakes often < 0.5
            flow_anomaly = max(0.0, (1.0 - avg_cov) * 50.0)  # 0-50 range
        else:
            flow_anomaly = 0.0
        
        # ── Biometric Forensics ──
        pulse_score = 50.0  # Default to Inconclusive instead of Authentic
        if all_skin_rgbs:
            pulse_score = self.physiological_pulse_analysis(np.array(all_skin_rgbs), fps)
        
        eye_score = float(np.mean(all_eye_scores)) if all_eye_scores else 0.0

        # Adjust general score based on biometrics
        # If biometrics fail, we significantly boost the overall fake score
        bio_penalty = 0.0
        if (pulse_score > 70 or eye_score > 70) and total_faces_scanned > 0:
            bio_penalty = 15.0

        # ── General Scores ──
        gen_ai_score = float(np.mean(all_gen_scores)) if all_gen_scores else 50.0
        noise_score = float(np.mean(all_noise_scores)) if all_noise_scores else 0.0
        spec_score = float(np.mean(all_spec_scores)) if all_spec_scores else 0.0
        
        # ── Evidence Mapping (Section 5) ──
        discrepancy_score = abs(neural_score - gen_ai_score)
        
        # ── Final Weighted Score ──
        if total_faces_scanned > 0:
            # Face-centric weights biased toward biometrics and physics
            ensemble_base = (
                neural_score * 0.40 +              # Face deepfake detector (increased)
                pulse_score * 0.15 +               # Physiological pulse (rPPG)
                eye_score * 0.10 +                 # Ocular symmetry (physics)
                gen_ai_score * 0.10 +              # General AI image classifier
                freq_score * 0.05 +                # DCT frequency
                (100.0 - temporal_score) * 0.08 +  # Temporal anomalies
                comp_score * 0.04 +                # Compression artifacts (lowered)
                flow_anomaly * 0.04 +              # Optical flow anomalies
                noise_score * 0.02 +               # PRNU absence
                spec_score * 0.02                  # Spectral decay
            )
            
            # Agreement-Based Signal Preservation (Robust FPR Edition):
            # Prioritize the max score only if there is a secondary supporting signal
            vit_p, npr_p = neural_score/100.0, gen_ai_score/100.0
            
            # primary_agreement: any secondary primary signal > 40% anomaly
            secondary_signals = [pulse_score, eye_score, freq_score * 2] # scaled for p
            has_agreement = any(s > 45.0 for s in secondary_signals) or (vit_p > 0.4 and npr_p > 0.4)
            
            if max(vit_p, npr_p) > 0.75 or (max(vit_p, npr_p) > 0.5 and has_agreement):
                # High confidence or agreed signal preservation
                combined_prob = (max(vit_p, npr_p) * 0.8 + min(vit_p, npr_p) * 0.2) * 100.0
            else:
                # Conservative average to prevent beauty filters/noise from false-flagging
                combined_prob = (vit_p * 0.5 + npr_p * 0.5) * 100.0
                
            final_algorithmic = combined_prob * 0.7 + ensemble_base * 0.3
        else:
            # Whole-scene weights (no faces)
            # Whole-scene weights (no faces)
            ensemble_base = (
                gen_ai_score * 0.45 +              # General AI image classifier
                noise_score * 0.15 +               # PRNU absence
                spec_score * 0.15 +                # Spectral decay
                freq_score * 0.15 +                # DCT frequency (whole frame)
                (100.0 - temporal_score) * 0.05 +  # Temporal anomalies
                flow_anomaly * 0.05                # Optical flow anomalies
            )
            
            if gen_ai_score > 70.0:
                final_algorithmic = gen_ai_score * 0.6 + ensemble_base * 0.4
            else:
                final_algorithmic = ensemble_base
            
        final_algorithmic = min(100.0, max(0.0, final_algorithmic + score_boost + bio_penalty))
        
        # Fit results into existing schema
        result_template = {
            "score": round(float(final_algorithmic), 1),
            "is_deepfake": bool(final_algorithmic >= 50.0),
            "certainty": "high" if final_algorithmic > 75.0 else "medium" if final_algorithmic > 40.0 else "low",
            "probability": round(float(final_algorithmic / 100.0), 4),
            "flicker_index": round(float(flicker_index), 4),
            "discrepancy_score": round(float(discrepancy_score), 2),
            "tta_coverage": int(total_faces_scanned * 11),
            "details": {
                "neural_artifacts": round(float(neural_score), 1),
                "frequency_domain": round(float(freq_score), 1),
                "temporal_consistency": round(float(max(0.0, 100.0 - temporal_score)), 1),
                "physiological_pulse": round(float(pulse_score), 1),
                "eye_symmetry": round(float(eye_score), 1),
                "compression_artifacts": round(float(comp_score), 1),
                "logical_consistency": 0.0,  # Pending Gemini
                "general_ai_score": round(float(gen_ai_score), 1),
                "noise_residual": round(float(noise_score), 1),
                "spectral_decay": round(float(spec_score), 1)
            },
            "gemini_context": "Deep context structural extraction running in background layer...",
            "per_frame": [],
            "face_crops": sorted(face_crop_data, key=lambda x: x["score"], reverse=True)[:6],
            "metadata": {
                "width": int(width), "height": int(height), "fps": round(float(fps), 1), "duration": round(float(duration), 2),
                "total_frames": int(total_frames), "frames_analyzed": int(num_sample),
                "faces_detected": int(total_faces_scanned),
                "tta_coverage": int(total_faces_scanned * 11)
            },
            "analysis_log": [],
            "processing_time_ms": int((time.time() - t_start) * 1000)
        }
        
        yield {"status": "tentative", "result": result_template}
        
        try:
            gemini_score, gemini_reasoning = gemini_future.result(timeout=120)
        except Exception as e:
            gemini_score, gemini_reasoning = 50.0, "Native forensics skipped or failed."
            
        # Final result is solely based on local algorithmic analysis
        result_template["score"] = round(float(final_algorithmic), 1)
        result_template["is_deepfake"] = bool(final_algorithmic >= 50.0)
        result_template["certainty"] = "high" if final_algorithmic > 75.0 else "medium" if final_algorithmic > 40.0 else "low"
        result_template["details"]["logical_consistency"] = round(float(gemini_score), 1)
        result_template["gemini_context"] = str(gemini_reasoning)
        result_template["processing_time_ms"] = int((time.time() - t_start) * 1000)
        
        yield {"status": "complete", "result": result_template}
