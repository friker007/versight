import os

model_path = r"d:\versight\versight_with_backend\versight\backend\model.py"
with open(model_path, "r", encoding="utf-8") as f:
    code = f.read()

# Normalize line endings to avoid \r\n issues
code = code.replace("\r\n", "\n")

# 1. Method injection
anchor1 = "    # ══════════════════════════════════════════\n    #  Main Analysis Pipeline"
if anchor1 not in code: raise Exception("Anchor 1 not found")

gemini_method = """    # ── Gemini Logical Fact-Checking ──
    def logical_forensics(self, frames_pil):
        prompt = '''You are an elite visual forensics AI. I am providing you with up to 4 uniformly sampled frames from a video.
Your job is to act as a deepfake visual fact-checker. You must heavily scrutinize the CONTEXT, PHYSICS, and UNCANNY VISUALS of the scene.
Are the facial features too perfect, shiny, or unnaturally smoothed? Do the eyes/teeth look synthetic? Does the lighting on the subject truly match the background? Are the facial expressions slightly robotic, "uncanny", or AI-generated? Even if the scene is mundane (like a person sitting and talking), aggressively penalize any AI-generation or deepfake traits you observe.

Respond STRICTLY with a JSON object containing exactly two keys:
1. "logical_reasoning": A 2-3 sentence paragraph explaining your visual analysis and why it looks natural or synthetic.
2. "anomaly_score": An integer from 0 to 100, where 100 heavily implies the face/context is AI-generated, synthetic, or manipulated, and 0 implies it is a 100% natural, unaltered physical camera recording.'''
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = self.gemini_model.generate_content([prompt] + frames_pil)
                text = response.text.strip()
                if text.startswith("```json"): text = text[7:-3].strip()
                elif text.startswith("```"): text = text[3:-3].strip()
                import json
                data = json.loads(text)
                return float(data.get("anomaly_score", 50)), data.get("logical_reasoning", "Analysis unavailable.")
            except Exception as e:
                print(f"[VERSIGHT] Gemini Logic Error (Attempt {attempt+1}): {e}")
                
        return 50.0, "Logical forensics unavailable due to an API error."

"""
code = code.replace(anchor1, gemini_method + anchor1)

# 2. Execution logic
anchor2 = "        # Step 3: Per-frame analysis\n        per_frame_results = []"
if anchor2 not in code: raise Exception("Anchor 2 not found")

gemini_exec = """        # Step 3: Per-frame analysis
        # ── Pre-extract Gemini Context Frames ──
        t1 = time.time()
        gemini_frames = []
        step = max(1, len(raw_frames) // 4)
        for i in range(0, len(raw_frames), step):
            if len(gemini_frames) < 4:
                rgb = cv2.cvtColor(raw_frames[i][1], cv2.COLOR_BGR2RGB)
                gemini_frames.append(Image.fromarray(rgb))
                
        print(f"[VERSIGHT] Executing Gemini fact-checking on {len(gemini_frames)} frames...")
        gemini_score, gemini_reasoning = self.logical_forensics(gemini_frames)
        t_gemini_ms = int((time.time() - t1) * 1000)
        log_steps.append({"step": "Gemini logical fact-checking", "detail": f"Score: {gemini_score:.1f}%", "time_ms": t_gemini_ms})

        per_frame_results = []"""
code = code.replace(anchor2, gemini_exec)

# 3. Final calculation
anchor3 = """        final = (neural_score * 0.30 +
                 freq_score * 0.20 +
                 temporal_consistency * 0.20 +
                 physio_score * 0.15 +
                 comp_score_avg * 0.15)
        final = min(100, max(0, final))"""
if anchor3 not in code: raise Exception("Anchor 3 not found")

gemini_final = """        final = (neural_score * 0.25 +
                 freq_score * 0.15 +
                 temporal_consistency * 0.15 +
                 physio_score * 0.10 +
                 comp_score_avg * 0.10 +
                 gemini_score * 0.25)
        final = min(100, max(0, final))"""
code = code.replace(anchor3, gemini_final)

# 4. Return Dict
anchor4 = """                "compression_artifacts": round(comp_score_avg, 1)
            },
            "per_frame": per_frame_results,"""
if anchor4 not in code: raise Exception("Anchor 4 not found")

gemini_return = """                "compression_artifacts": round(comp_score_avg, 1),
                "logical_consistency": round(gemini_score, 1)
            },
            "gemini_context": gemini_reasoning,
            "per_frame": per_frame_results,"""
code = code.replace(anchor4, gemini_return)

with open(model_path, "w", encoding="utf-8") as f:
    f.write(code)

print("model.py patched successfully and robustly!")
