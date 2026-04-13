import os

ui_path = r"d:\versight\versight_with_backend\versight\frontend\src\components\AnalysisResults.jsx"
with open(ui_path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Imports
code = code.replace("Activity, Waves, Eye, Cpu } from 'lucide-react';", "Activity, Waves, Eye, Cpu, Sparkles } from 'lucide-react';")

# 2. Destructure
code = code.replace("const { is_deepfake, score, details, per_frame, face_crops, metadata, analysis_log, processing_time_ms } = result;", "const { is_deepfake, score, details, per_frame, face_crops, metadata, analysis_log, processing_time_ms, gemini_context } = result;")

# 3. Add Gauge
gauge_logic = '''          <ScoreGauge
            icon={<Monitor size={16} />}
            title="Compression Artifacts"
            score={details?.compression_artifacts || 0}
            desc="Re-encoding signatures and Laplacian smoothness analysis at 8×8 block boundaries"
          />
          <ScoreGauge
            icon={<Sparkles size={16} />}
            title="Logical Consistency"
            score={details?.logical_consistency || 0}
            desc="Gemini multi-modal contextual analysis detecting impossible physics or logical contradictions"
          />'''
code = code.replace('''          <ScoreGauge
            icon={<Monitor size={16} />}
            title="Compression Artifacts"
            score={details?.compression_artifacts || 0}
            desc="Re-encoding signatures and Laplacian smoothness analysis at 8×8 block boundaries"
          />''', gauge_logic)

# 4. Add Gemini Card
gemini_card = '''      {/* ═══════════════ GEMINI CONTEXT AI ═══════════════ */}
      {gemini_context && (
        <div className="bg-[#1a1133]/90 p-6 rounded-2xl border border-purple-500/30 shadow-[0_0_20px_rgba(168,85,247,0.15)] relative overflow-hidden backdrop-blur-xl">
          <div className="absolute top-0 left-0 w-1 bg-gradient-to-b from-purple-400 to-indigo-500 h-full shadow-[0_0_15px_rgba(168,85,247,0.8)]"></div>
          <h3 className="text-xl font-bold mb-3 flex items-center gap-2 text-purple-300">
            <Sparkles size={20} className="text-purple-400 animate-pulse" /> Gemini Contextual Reasoning
          </h3>
          <p className="text-gray-300 leading-relaxed text-[15px] italic font-medium">
            "{gemini_context}"
          </p>
        </div>
      )}

      {/* ═══════════════ VIDEO METADATA ═══════════════ */}'''
code = code.replace("      {/* ═══════════════ VIDEO METADATA ═══════════════ */}", gemini_card)

with open(ui_path, "w", encoding="utf-8") as f:
    f.write(code)

print("UI patched successfully.")
