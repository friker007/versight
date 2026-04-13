import os

model_path = r"d:\versight\versight_with_backend\versight\backend\model.py"
with open(model_path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Imports and init
code = code.replace("import time", '''import time
import json
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))''')

code = code.replace('print("[VERSIGHT] Mathematical Forensics Engine loaded.")', 
'''self.gemini_model = genai.GenerativeModel("gemini-1.5-flash")
        print("[VERSIGHT] Mathematical Forensics Engine & Gemini AI loaded.")''')

# 2. Methods
gemini_methods = '''    # ── Gemini Logical Fact-Checking ──
    def logical_forensics(self, frames_pil):
        prompt = """
You are an elite logical forensics AI. I am providing you with up to 4 uniformly sampled frames from a single video.
Your job is to act as a deepfake fact-checker by analyzing the CONTEXT and PHYSICS of the scene.
Are there impossible physics? Are there public figures doing/saying something historically impossible or extremely out of character? 
Is the lighting or interaction between subjects fundamentally illogical?

Respond STRICTLY with a JSON object containing exactly two keys:
1. "logical_reasoning": A 2-3 sentence paragraph explaining your logical analysis and fact-checking.
2. "anomaly_score": An integer from 0 to 100, where 100 heavily implies the context is an AI-generated or manipulated deepfake, and 0 implies it is logically coherent and perfectly realistic.

Do not use markdown formatting like ```json. Output raw JSON ONLY.
"""
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = self.gemini_model.generate_content([prompt] + frames_pil)
                text = response.text.strip()
                if text.startswith("```json"): text = text[7:-3].strip()
                elif text.startswith("```"): text = text[3:-3].strip()
                data = json.loads(text)
                return float(data.get("anomaly_score", 50)), data.get("logical_reasoning", "Analysis unavailable.")
            except Exception as e:
                print(f"[VERSIGHT] Gemini Logic Error (Attempt {attempt+1}): {e}")
                
        return 50.0, "Logical forensics unavailable due to an API error."

    # ══════════════════════════════════════════'''
code = code.replace("    # ══════════════════════════════════════════", gemini_methods)

# 3. Context frames
context_logic = '''        # Step 3: Per-frame analysis
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

        per_frame_results = []'''
code = code.replace("        # Step 3: Per-frame analysis\n        per_frame_results = []", context_logic)

# 4. Aggregation and Return
agg_logic = '''        final = (neural_score * 0.25 +
                 freq_score * 0.15 +
                 temporal_consistency * 0.15 +
                 physio_score * 0.10 +
                 comp_score_avg * 0.10 +
                 gemini_score * 0.25)
        final = min(100, max(0, final))'''
code = code.replace('''        final = (neural_score * 0.30 +
                 freq_score * 0.20 +
                 temporal_consistency * 0.20 +
                 physio_score * 0.15 +
                 comp_score_avg * 0.15)
        final = min(100, max(0, final))''', agg_logic)

ret_dict = '''                "compression_artifacts": round(comp_score_avg, 1),
                "logical_consistency": round(gemini_score, 1)
            },
            "gemini_context": gemini_reasoning,
            "per_frame": per_frame_results,'''
code = code.replace('''                "compression_artifacts": round(comp_score_avg, 1)
            },
            "per_frame": per_frame_results,''', ret_dict)

with open(model_path, "w", encoding="utf-8") as f:
    f.write(code)

print("model.py patched successfully!")
