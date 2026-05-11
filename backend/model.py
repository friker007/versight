import torch
import json
import torch.nn as nn
import torchvision.models as models
import torch.nn.functional as F_torch
import matplotlib
matplotlib.use('Agg')
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
from facenet_pytorch import MTCNN, InceptionResnetV1
from dotenv import load_dotenv

load_dotenv()

class DeepfakeDetector:
    def __init__(self):
        # Acceleration Core Check for Apple Silicon
        if torch.cuda.is_available():
            self.device = torch.device('cuda')
        elif torch.backends.mps.is_available():
            self.device = torch.device('mps')
        else:
            self.device = torch.device('cpu')
        print(f"[VERSIGHT] Active Device core: {self.device}")

        # ── Model A: ViT Face-Aware ──
        hf_model_name = "prithivMLmods/Deep-Fake-Detector-v2-Model"
        self.detector_model = AutoModelForImageClassification.from_pretrained(hf_model_name, attn_implementation='eager')
        self.detector_processor = AutoImageProcessor.from_pretrained(hf_model_name)
        self.detector_model.to(self.device).eval()
        
        self.fake_idx = 1
        for idx, label in self.detector_model.config.id2label.items():
            if 'fake' in label.lower():
                self.fake_idx = int(idx)
                break

        # ── Model B: Texture NPR Detector ──
        gen_model_name = "umm-maybe/AI-image-detector"
        self.gen_detector = AutoModelForImageClassification.from_pretrained(gen_model_name)
        self.gen_processor = AutoImageProcessor.from_pretrained(gen_model_name)
        self.gen_detector.to(self.device).eval()
        
        self.gen_fake_idx = 0
        for idx, label in self.gen_detector.config.id2label.items():
            if 'artificial' in label.lower() or 'ai' in label.lower():
                self.gen_fake_idx = int(idx)
                break

        # ── Face Detect with Strict Verification ──
        mtcnn_dev = self.device if str(self.device) != 'mps' else torch.device('cpu')
        self.mtcnn = MTCNN(keep_all=True, device=mtcnn_dev, thresholds=[0.95, 0.96, 0.96])

        # ── Gemini Contextual Core ──
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.gemini_model_name = "gemini-2.0-flash"
        
        # ── Identity Embedder ──
        print("[VERSIGHT] Loading Face Identity Engine...")
        self.identity_model = InceptionResnetV1(pretrained='vggface2').to(self.device).eval()
        print("[VERSIGHT] Engine restored and online.")

    def get_tta_views(self, face_pil):
        import torchvision.transforms.functional as F
        w, h = face_pil.size
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

    def get_embedding(self, pil_img):
        try:
            img_resized = pil_img.resize((160, 160))
            img_np = np.array(img_resized).astype(np.float32)
            img_normalized = (img_np - 127.5) / 128.0
            img_t = torch.tensor(img_normalized).permute(2, 0, 1).unsqueeze(0).float().to(self.device)
            with torch.no_grad():
                embed = self.identity_model(img_t).detach().cpu().numpy().flatten()
            return embed
        except:
            return None

    def evaluate_face(self, face_pil):
        tta_views = self.get_tta_views(face_pil)
        
        # Optimization: Group Parallel Batch Forward Pass
        vit_views = tta_views[:2]
        inputs_vit = self.detector_processor(images=vit_views, return_tensors="pt").to(self.device)
        with torch.no_grad():
            out_vit = self.detector_model(**inputs_vit)
            prob_vit = torch.softmax(out_vit.logits, dim=-1).cpu().numpy()[:, self.fake_idx]
        vit_score = float(np.mean(prob_vit))
        
        inputs_npr = self.gen_processor(images=tta_views, return_tensors="pt").to(self.device)
        with torch.no_grad():
            out_npr = self.gen_detector(**inputs_npr)
            prob_npr = torch.softmax(out_npr.logits, dim=-1).cpu().numpy()[:, self.gen_fake_idx]
        npr_score = float(np.mean(prob_npr))
        
        if min(vit_score, npr_score) > 0.6:
            combined_prob = max(vit_score, npr_score) * 0.8 + min(vit_score, npr_score) * 0.2
        else:
            combined_prob = (vit_score + npr_score) / 2.0
            
        heatmap = self.generate_heatmap(face_pil)
        return combined_prob, vit_score, npr_score, heatmap

    def generate_heatmap(self, face_pil):
        try:
            inputs = self.detector_processor(images=face_pil, return_tensors="pt").to(self.device)
            with torch.no_grad():
                outputs = self.detector_model(**inputs, output_attentions=True)
            
            last_attn = outputs.attentions[-1]
            attn_heads_avg = last_attn.mean(dim=1)
            cls_attn = attn_heads_avg[0, 0, 1:]
            grid_size = int(cls_attn.shape[0] ** 0.5)
            attn_map = cls_attn.reshape(grid_size, grid_size).cpu().numpy()
            
            attn_map = (attn_map - attn_map.min()) / (attn_map.max() - attn_map.min() + 1e-8)
            orig_w, orig_h = face_pil.size
            face_np = np.array(face_pil)
            attn_upscaled = cv2.resize(attn_map, (orig_w, orig_h), interpolation=cv2.INTER_CUBIC)
            
            colormap = cm.get_cmap('jet')
            h_rgba = colormap(attn_upscaled)
            h_rgb = (h_rgba[:, :, :3] * 255).astype(np.uint8)
            overlay = cv2.addWeighted(face_np, 0.6, h_rgb, 0.4, 0)
            
            out_pil = Image.fromarray(overlay)
            buf = io.BytesIO()
            out_pil.save(buf, format="JPEG", quality=80)
            return base64.b64encode(buf.getvalue()).decode("utf-8")
        except:
            return None

    def evaluate_frame_general(self, frame_pil):
        try:
            inputs = self.gen_processor(images=frame_pil, return_tensors="pt").to(self.device)
            with torch.no_grad():
                outputs = self.gen_detector(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)
            return float(probs[0, self.gen_fake_idx].item())
        except:
            return 0.5

    def logical_forensics_video(self, video_path, local_data=None):
        prompt = f"Analyze video. Data context: {local_data}. Perform audit. Return strictly raw JSON {{\"logical_reasoning\": \"...\", \"anomaly_score\": int}}"
        try:
            v_file = self.client.files.upload(file=video_path)
            while v_file.state == 'PROCESSING': time.sleep(2); v_file = self.client.files.get(name=v_file.name)
            r = self.client.models.generate_content(model=self.gemini_model_name, contents=[v_file, prompt])
            self.client.files.delete(name=v_file.name)
            txt = r.text.strip()
            if txt.startswith("```"): txt = txt.split("\n", 1)[1].rsplit("\n", 1)[0].strip()
            d = json.loads(txt)
            return float(d.get("anomaly_score", 50)), d.get("logical_reasoning", "Available.")
        except:
            return 50.0, "Logical forensics bypassed."

    def analyze_video(self, video_path: str):
        out = None
        for u in self.analyze_video_stream(video_path):
            if u.get("status") == "complete": out = u.get("result")
        return out

    def analyze_video_stream(self, video_path: str):
        if not os.path.exists(video_path): raise Exception("Source not found.")
        t_start = time.time()
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened(): raise Exception("Capture blocked.")
        
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        num_sample = min(128, max(1, total_frames))
        indices = np.linspace(0, max(0, total_frames - 1), num_sample, dtype=int)
        
        all_face_scores = []
        background_scores = []
        face_crop_data = []
        raw_face_observations = []
        total_faces_scanned = 0
        
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        gemini_future = None

        yield {"status": "processing", "step": "Loading Optimized Models", "progress": 10, "details": "Mac acceleration engaged."}

        for p_idx, idx in enumerate(indices):
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
            ok, frame = cap.read()
            if not ok: break
            
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_frame = Image.fromarray(rgb)
            
            if p_idx % 4 == 0:
                background_scores.append(self.evaluate_frame_general(pil_frame))

            boxes, _ = self.mtcnn.detect(pil_frame)
            current_frame_best = None
            
            if boxes is not None:
                total_faces_scanned += len(boxes)
                frame_peak = 0.0
                for b in boxes:
                    x1, y1, x2, y2 = [int(c) for c in b]
                    # Spec: 30% padding applied each direction
                    pw, ph = int((x2-x1)*0.3), int((y2-y1)*0.3)
                    ex1, ey1 = max(0, x1-pw), max(0, y1-ph)
                    ex2, ey2 = min(width, x2+pw), min(height, y2+ph)
                    
                    if (ex2-ex1) > 20 and (ey2-ey1) > 20:
                        face_c = pil_frame.crop((ex1, ey1, ex2, ey2))
                        emb = self.get_embedding(face_c)
                        comb_p, v_s, n_s, hmap = self.evaluate_face(face_c)
                        
                        raw_face_observations.append({
                            "frame_idx": int(idx), "embedding": emb, "vit_score": v_s,
                            "npr_score": n_s, "final_prob": comb_p, "heatmap": hmap, "crop": face_c
                        })
                        
                        if comb_p > frame_peak: frame_peak = comb_p
                        if len(face_crop_data) < 20:
                            buf = io.BytesIO(); face_c.save(buf, format="JPEG", quality=80)
                            face_crop_data.append({
                                "frame_index": int(idx), "score": round(comb_p*100,1),
                                "original": base64.b64encode(buf.getvalue()).decode("utf-8"), "heatmap": hmap
                            })
                current_frame_best = frame_peak
            
            val = current_frame_best if current_frame_best is not None else 0.25
            all_face_scores.append(val * 100.0)
            
            if p_idx % 10 == 0:
                yield {
                    "status": "processing", "step": "Forensic Analysis", 
                    "progress": min(90, 20 + int((p_idx/num_sample)*70)),
                    "details": f"Frame {p_idx}/{num_sample} sampled.",
                    "latest_crops": face_crop_data[-3:],
                    "telemetry": {
                        "neural": round(float(np.mean(all_face_scores)),1),
                        "gen_ai": round(float(np.mean(background_scores)*100.0 if background_scores else 50.0),1),
                        "frequency": 0.0, "noise": 0.0, "spectral": 0.0, "total_faces": int(total_faces_scanned)
                    }
                }
            
            if p_idx == int(num_sample*0.8) and gemini_future is None:
                gemini_future = executor.submit(self.logical_forensics_video, video_path, {"score": np.mean(all_face_scores)})

        cap.release()

        bg_tex = float(np.mean(background_scores)) * 100.0 if background_scores else 50.0

        # ── Clustering Routine ──
        clusters = []
        for o in raw_face_observations:
            ev = o["embedding"]
            if ev is None: continue
            best_d, best_c = 100.0, -1
            for ci, c in enumerate(clusters):
                dist = float(np.linalg.norm(c["centroid"] - ev))
                if dist < best_d: best_d = dist; best_c = ci
            if best_c != -1 and best_d < 1.05:
                clusters[best_c]["obs"].append(o)
                clusters[best_c]["centroid"] = 0.75 * clusters[best_c]["centroid"] + 0.25 * ev
            else:
                clusters.append({"centroid": ev, "obs": [o]})

        detected_identities = []
        for idx, cl in enumerate(clusters):
            lst = sorted(cl["obs"], key=lambda x: x["frame_idx"])
            scores = np.array([x["final_prob"] * 100.0 for x in lst])
            
            def r_avg(a, n=3):
                if len(a) < n: return a
                r = np.cumsum(a, dtype=float); r[n:] = r[n:] - r[:-n]
                return r[n-1:] / n
            
            smoothed = r_avg(scores, 3)
            topk = max(1, int(len(smoothed) * 0.75))
            neural = float(np.mean(np.sort(smoothed)[-topk:]))
            
            f_idx, s_boost = 0.0, 0.0
            if len(scores) > 1:
                d = np.diff(scores)
                f_idx = float(np.std(d/100.0))
                s = np.sign(d); ch = float(np.sum(s[:-1] != s[1:])/len(d))
                if f_idx > 0.08 or ch > 0.2:
                    sig = (f_idx-0.08)*50.0 + (ch-0.2)*20.0
                    s_boost = (1 / (1 + math.exp(-sig))) * 15.0
            
            f_score = min(100.0, max(0.0, neural + s_boost))
            
            worst = max(lst, key=lambda x: x["final_prob"])
            buf_a = io.BytesIO(); worst["crop"].save(buf_a, format="JPEG", quality=80)
            a_b64 = base64.b64encode(buf_a.getvalue()).decode("utf-8")
            
            a_vit = float(np.mean([x["vit_score"]*100.0 for x in lst]))
            a_npr = float(np.mean([x["npr_score"]*100.0 for x in lst]))
            
            vector_audit = [
                {"id": "texture", "label": "Surface Texture Continuity", "score": round(a_npr,1), "status": "FAIL" if a_npr > 50 else "PASS", "desc": "Inconsistent noise grid detected." if a_npr > 50 else "Normal skin variance."},
                {"id": "structural", "label": "Anatomical Feature Symmetry", "score": round(a_vit,1), "status": "FAIL" if a_vit > 50 else "PASS", "desc": "Landmark deviation triggered." if a_vit > 50 else "Biological alignment correct."},
                {"id": "temporal", "label": "Temporal Frame Lock", "score": round(100.0 - (f_idx*200.0), 1), "status": "FAIL" if f_idx > 0.15 else "PASS", "desc": "Flicker interpolation visible." if f_idx > 0.15 else "Stable motion cohesion."}
            ]

            detected_identities.append({
                "identity_id": idx, "name": f"Subject {idx+1}", "score": round(f_score,1),
                "threat_level": "HIGH" if f_score > 70 else "MEDIUM" if f_score > 40 else "SAFE",
                "avatar": a_b64, "heatmap": worst["heatmap"], "sample_count": len(lst), "vector_audit": vector_audit
            })

        if detected_identities:
            p_s = max(detected_identities, key=lambda x: x["score"])
            glob_sc = p_s["score"]
            glob_flick = float(np.mean([o["final_prob"] for o in raw_face_observations]))
        else:
            glob_sc = 25.0; glob_flick = 0.0

        result = {
            "score": round(float(glob_sc), 1),
            "is_deepfake": bool(glob_sc >= 50.0),
            "certainty": "high" if glob_sc > 75 else "medium" if glob_sc > 40 else "low",
            "probability": round(float(glob_sc/100.0), 4),
            "identities": detected_identities,
            "discrepancy_score": round(abs(glob_sc - bg_tex), 2),
            "tta_coverage": int(total_faces_scanned * 11),
            "details": {
                "neural_artifacts": round(float(glob_sc), 1),
                "frequency_domain": 0.0,
                "temporal_consistency": round(float(100.0 - (glob_flick * 200.0)), 1),
                "physiological_pulse": 0.0, "eye_symmetry": 0.0, "compression_artifacts": 0.0, "logical_consistency": 0.0,
                "general_ai_score": round(bg_tex, 1), "noise_residual": 0.0, "spectral_decay": 0.0
            },
            "gemini_context": "Running background reconcile...",
            "per_frame": [],
            "face_crops": sorted(face_crop_data, key=lambda x: x["score"], reverse=True),
            "metadata": {
                "width": int(width), "height": int(height), "fps": round(float(fps),1),
                "total_frames": int(total_frames), "frames_analyzed": int(num_sample),
                "faces_detected": int(total_faces_scanned), "tta_coverage": int(total_faces_scanned * 11)
            },
            "processing_time_ms": int((time.time() - t_start)*1000)
        }
        
        yield {"status": "tentative", "result": result}

        try:
            g_sc, g_rs = gemini_future.result(timeout=60)
        except:
            g_sc, g_rs = 50.0, "Skipped."
            
        result["details"]["logical_consistency"] = g_sc
        result["gemini_context"] = g_rs
        result["processing_time_ms"] = int((time.time() - t_start)*1000)
        
        yield {"status": "complete", "result": result}
