import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Download, RotateCcw, Cpu, Waves, Sparkles, History, Film, Scan, CheckCircle2, AlertTriangle, X, ZoomIn, Brain, Fingerprint, Activity, Heart, Eye } from 'lucide-react';

const stagger = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.08, delayChildren: 0.1 } },
};
const fadeUp = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] } },
};

export default function AnalysisResults({ results, onRestart }) {
  if (!results) return null;

  const [expandedCrop, setExpandedCrop] = useState(null);

  // Backend returns: score, details, gemini_context, metadata, per_frame, face_crops
  const overall_score = results.score ?? 0;
  const breakdown = results.details || {};
  const gemini_reasoning = results.gemini_context || '';
  const video_metadata = results.metadata || {};
  const per_frame = results.per_frame || [];
  const face_crops = results.face_crops || [];

  const isDeepfake = results.is_deepfake ?? (overall_score >= 50);
  const confidence = isDeepfake ? overall_score : 100 - overall_score;

  return (
    <motion.div variants={stagger} initial="hidden" animate="show" style={{ width: '100%', maxWidth: 1100, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 48, padding: '0 16px' }}>

      {/* ═══ HEADER ═══ */}
      <motion.div variants={fadeUp} style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'flex-end', gap: 24, borderBottom: '1px solid var(--border)', paddingBottom: 24 }}>
        <div>
          <div className="caps-label" style={{ color: 'var(--accent)', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ width: 24, height: 1.5, background: 'var(--accent)', display: 'inline-block' }} />
            Forensic Dossier v4.2
          </div>
          <h1 style={{ fontFamily: "'Lora', serif", fontSize: 'clamp(2rem, 4vw, 3.5rem)', fontWeight: 500, lineHeight: 1.1, color: 'var(--text)' }}>
            Integrity{' '}<br /><span style={{ fontStyle: 'italic', color: 'var(--text-muted)' }}>Inspection Report.</span>
          </h1>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <button className="editorial-btn"><Download size={14} /> Export PDF</button>
          <button onClick={onRestart} className="editorial-btn primary"><RotateCcw size={14} /> New Analysis</button>
        </div>
      </motion.div>

      {/* ═══ BODY GRID ═══ */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 40, alignItems: 'stretch' }}>
        {/* Responsive: stack verdict on top, details below */}

        {/* ─── LEFT: Verdict ─── */}
        <motion.div variants={fadeUp} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 24 }}>
          <div className="editorial-card" style={{ padding: '36px 32px', textAlign: 'center' }}>
            <h3 style={{ fontFamily: "'Lora', serif", fontSize: '1.15rem', fontWeight: 500, marginBottom: 28, color: 'var(--text)' }}>Authenticity Verdict</h3>

            {/* Ring Gauge */}
            <div style={{ position: 'relative', width: 160, height: 160, margin: '0 auto 28px' }}>
              <svg width={160} height={160} viewBox="0 0 160 160" style={{ position: 'absolute', top: 0, left: 0, transform: 'rotate(-90deg)' }}>
                <circle cx={80} cy={80} r={72} fill="none" stroke="var(--border)" strokeWidth={3} />
                <motion.circle
                  cx={80} cy={80} r={72}
                  fill="none"
                  stroke={isDeepfake ? 'var(--warning)' : 'var(--success)'}
                  strokeWidth={6}
                  strokeDasharray={452.4}
                  initial={{ strokeDashoffset: 452.4 }}
                  animate={{ strokeDashoffset: 452.4 - (452.4 * overall_score) / 100 }}
                  transition={{ duration: 1.8, ease: 'easeOut', delay: 0.4 }}
                  strokeLinecap="round"
                />
              </svg>
              <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                <span style={{ position: 'relative', fontFamily: "'Lora', serif", fontSize: '2.8rem', fontWeight: 500, color: 'var(--text)', lineHeight: 1 }}>
                  {overall_score.toFixed(0)}
                  <span style={{ position: 'absolute', top: '0.3rem', left: '100%', fontSize: '1.4rem', color: 'var(--text-muted)', marginLeft: 4 }}>%</span>
                </span>
                <span className="caps-label" style={{ marginTop: 8, fontSize: '0.55rem' }}>Anomaly Index</span>
              </div>
            </div>

            {/* Badge */}
            <div style={{
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
              padding: '10px 16px', borderRadius: 8,
              background: isDeepfake ? 'rgba(200,75,75,0.1)' : 'rgba(91,140,90,0.1)',
              border: `1px solid ${isDeepfake ? 'rgba(200,75,75,0.2)' : 'rgba(91,140,90,0.2)'}`,
              color: isDeepfake ? 'var(--warning)' : 'var(--success)',
              fontSize: '0.8rem', fontWeight: 500,
            }}>
              {isDeepfake ? <AlertTriangle size={16} /> : <CheckCircle2 size={16} />}
              {isDeepfake ? 'Synthetic Media Detected' : 'Verified Authentic'}
            </div>

            {/* Stats */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginTop: 24, paddingTop: 20, borderTop: '1px solid var(--border)' }}>
              <div style={{ textAlign: 'left' }}>
                <div className="caps-label" style={{ fontSize: '0.5rem', marginBottom: 4 }}>Confidence</div>
                <div style={{ fontFamily: "'Lora', serif", fontSize: '1.3rem', color: 'var(--text)' }}>{confidence.toFixed(1)}%</div>
              </div>
              <div style={{ textAlign: 'left', paddingLeft: 16, borderLeft: '1px solid var(--border)' }}>
                <div className="caps-label" style={{ fontSize: '0.5rem', marginBottom: 4 }}>Risk</div>
                <div style={{ fontFamily: "'Lora', serif", fontSize: '1.3rem', color: isDeepfake ? 'var(--warning)' : 'var(--success)' }}>
                  {isDeepfake ? 'High' : 'Low'}
                </div>
              </div>
            </div>
          </div>

          {/* Metadata */}
          <div style={{ padding: '24px 28px', borderLeft: '3px solid var(--accent)', background: 'var(--surface-raised)', borderRadius: '0 8px 8px 0', display: 'flex', flexDirection: 'column', gap: 14 }}>
            <span className="caps-label" style={{ color: 'var(--text)', marginBottom: 4 }}>Asset Metadata</span>
            <MetaRow label="Format" value={video_metadata?.codec || 'MPEG-4'} />
            <MetaRow label="Resolution" value={`${video_metadata?.width || 1920} × ${video_metadata?.height || 1080}`} />
            <MetaRow label="Frame Rate" value={`${video_metadata?.fps || '24.00'} FPS`} />
            <MetaRow label="Duration" value={`${(video_metadata?.duration || 0).toFixed(2)} sec`} />
          </div>
        </motion.div>

        {/* ─── RIGHT: Detail panels ─── */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 40 }}>

          {/* Neural Gauges */}
          <motion.section variants={fadeUp}>
            <SectionHeader title="Neural Topography" sub="Detailed Channel Analysis" />
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '24px 32px' }}>
              <Gauge icon={<Brain size={18} />} label="General AI Score" value={breakdown?.general_ai_score || 0} desc="Whole-frame ViT assessment for non-face synthetic content (planes, objects, etc)." delay={0.1} />
              <Gauge icon={<Cpu size={18} />} label="Spatial CNN" value={breakdown?.neural_artifacts || 0} desc="Texture-frequency domain inspection targeting GAN/Diffusion artifacts on faces." delay={0.2} />
              <Gauge icon={<Waves size={18} />} label="Spectral Consistency" value={breakdown?.frequency_domain || 0} desc="Error Level Analysis and DCT coefficient mapping." delay={0.3} />
              <Gauge icon={<Fingerprint size={18} />} label="Noise Residual" value={breakdown?.noise_residual || 0} desc="PRNU extraction: detects absence of authentic camera sensor noise." delay={0.4} />
              <Gauge icon={<Activity size={18} />} label="Spectral Decay" value={breakdown?.spectral_decay || 0} desc="Evaluates deviation from natural 1/f frequency power law." delay={0.5} />
              <Gauge icon={<History size={18} />} label="Temporal Variance" value={breakdown?.temporal_consistency || 0} desc="Frame-to-frame identity persistence and optical flow analysis." delay={0.6} />
              <Gauge icon={<Heart size={18} />} label="Physiological Pulse" value={breakdown?.physiological_pulse || 0} desc="Detects sub-perceptual heartbeat signals (rPPG). Absent in AI faces." delay={0.7} />
              <Gauge icon={<Eye size={18} />} label="Ocular Symmetry" value={breakdown?.eye_symmetry || 0} desc="Analyzes physics-based reflection consistency between both pupils." delay={0.8} />
            </div>
          </motion.section>

          {/* AI Insight Quote */}
          <motion.section variants={fadeUp} style={{ padding: '28px 28px', background: 'var(--surface-raised)', borderRadius: 12, border: '1px solid var(--border)', position: 'relative', overflowWrap: 'break-word', wordBreak: 'break-word' }}>
            <div style={{ position: 'absolute', top: -12, left: 28, background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 6, padding: '4px 12px', display: 'flex', alignItems: 'center', gap: 6 }}>
              <Sparkles size={10} style={{ color: 'var(--accent)' }} />
              <span className="caps-label" style={{ color: 'var(--accent)', fontSize: '0.55rem' }}>Contextual Intelligence</span>
            </div>
            <p style={{ fontFamily: "'Lora', serif", fontSize: '1.15rem', lineHeight: 1.7, fontStyle: 'italic', color: 'var(--text)', opacity: 0.9, marginTop: 8 }}>
              "{gemini_reasoning || 'No significant contextual or logical anomalies identified within the examined narrative sequence.'}"
            </p>
          </motion.section>

          {/* Evidence */}
          <motion.section variants={fadeUp} style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>
            <EvidenceRow title="Temporal Extraction" icon={<Film size={16} />} items={per_frame} isFrame count={(per_frame || []).length} />
          </motion.section>

          {/* ═══ FACE HEATMAP GALLERY ═══ */}
          <motion.section variants={fadeUp}>
            <SectionHeader title="Forensic Attention Maps" sub="Model Focus Regions" />
            {face_crops.length > 0 ? (
              <>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', lineHeight: 1.6, marginBottom: 24 }}>
                  These heatmaps reveal which facial regions the neural detector focused on when evaluating each face. 
                  <span style={{ color: 'var(--warning)' }}> Red </span> indicates high model attention (suspected manipulation), 
                  <span style={{ color: 'var(--success)' }}> blue </span> indicates low attention (appears natural).
                </p>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
                  gap: 20,
                }}>
                  {face_crops.map((crop, i) => (
                    <motion.div
                      key={`crop-${i}`}
                      initial={{ opacity: 0, scale: 0.92 }}
                      whileInView={{ opacity: 1, scale: 1 }}
                      whileHover={{ scale: 1.03, boxShadow: 'var(--shadow-card-hover)' }}
                      whileTap={{ scale: 0.98 }}
                      viewport={{ once: true }}
                      transition={{ duration: 0.3 }}
                      className="editorial-card"
                      onClick={() => setExpandedCrop(crop)}
                      style={{ overflow: 'hidden', padding: 0, cursor: 'pointer' }}
                    >
                      {/* Image pair: Original + Heatmap */}
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 0, alignItems: 'stretch' }}>
                        {/* Original */}
                        <div style={{ position: 'relative', overflow: 'hidden' }}>
                          {crop.original && (
                            <img
                              src={`data:image/jpeg;base64,${crop.original}`}
                              alt={`Face ${i + 1}`}
                              style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}
                            />
                          )}
                          <div style={{
                            position: 'absolute', bottom: 6, left: 6,
                            background: 'rgba(0,0,0,0.65)', backdropFilter: 'blur(8px)',
                            padding: '2px 8px', borderRadius: 4,
                            fontSize: '0.55rem', fontFamily: "'Inter', sans-serif", fontWeight: 600, color: '#fff',
                            textTransform: 'uppercase', letterSpacing: '0.1em',
                          }}>
                            Original
                          </div>
                        </div>

                        {/* Heatmap */}
                        <div style={{ position: 'relative', overflow: 'hidden' }}>
                          {crop.heatmap ? (
                            <img
                              src={`data:image/jpeg;base64,${crop.heatmap}`}
                              alt={`Heatmap ${i + 1}`}
                              style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}
                            />
                          ) : (
                            <div style={{ width: '100%', aspectRatio: '1', background: 'var(--surface-raised)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                              <Scan size={20} style={{ color: 'var(--text-muted)', opacity: 0.3 }} />
                            </div>
                          )}
                          <div style={{
                            position: 'absolute', bottom: 6, left: 6,
                            background: 'rgba(0,0,0,0.65)', backdropFilter: 'blur(8px)',
                            padding: '2px 8px', borderRadius: 4,
                            fontSize: '0.55rem', fontFamily: "'Inter', sans-serif", fontWeight: 600, color: 'var(--accent)',
                            textTransform: 'uppercase', letterSpacing: '0.1em',
                          }}>
                            Attention Map
                          </div>
                        </div>
                      </div>

                      {/* Footer bar */}
                      <div style={{
                        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                        padding: '10px 14px',
                        borderTop: '1px solid var(--border)',
                        background: 'var(--surface)',
                      }}>
                        <span className="caps-label" style={{ fontSize: '0.55rem' }}>Frame #{crop.frame_index}</span>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <ZoomIn size={12} style={{ color: 'var(--text-muted)', opacity: 0.5 }} />
                          <span className="caps-label" style={{ fontSize: '0.5rem' }}>Anomaly</span>
                          <span className="font-mono" style={{
                            fontSize: '0.85rem',
                            fontWeight: 700,
                            color: crop.score >= 50 ? 'var(--warning)' : 'var(--success)',
                          }}>
                            {crop.score}%
                          </span>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </>
            ) : (
              <p style={{ color: 'var(--text-muted)', fontStyle: 'italic', fontSize: '0.85rem' }}>
                Attention maps will appear here once face regions are isolated and processed.
              </p>
            )}
          </motion.section>
        </div>
      </div>

      {/* ═══ EXPANDED HEATMAP LIGHTBOX ═══ */}
      <AnimatePresence>
        {expandedCrop && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.25 }}
            onClick={() => setExpandedCrop(null)}
            style={{
              position: 'fixed', inset: 0, zIndex: 9999,
              background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(12px)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              padding: 24, cursor: 'pointer',
            }}
          >
            <motion.div
              initial={{ scale: 0.85, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.85, opacity: 0 }}
              transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
              onClick={(e) => e.stopPropagation()}
              style={{
                background: 'var(--surface)', borderRadius: 16,
                border: '1px solid var(--border)',
                boxShadow: '0 24px 80px rgba(0,0,0,0.5)',
                maxWidth: 800, width: '100%', overflow: 'hidden',
                cursor: 'default',
              }}
            >
              {/* Header */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px 20px', borderBottom: '1px solid var(--border)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <Scan size={16} style={{ color: 'var(--accent)' }} />
                  <span style={{ fontFamily: "'Lora', serif", fontSize: '1.1rem', fontWeight: 500, color: 'var(--text)' }}>
                    Frame #{expandedCrop.frame_index} — Attention Detail
                  </span>
                </div>
                <button
                  onClick={() => setExpandedCrop(null)}
                  style={{
                    background: 'var(--surface-raised)', border: '1px solid var(--border)',
                    borderRadius: 8, width: 32, height: 32,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    cursor: 'pointer', color: 'var(--text-muted)',
                  }}
                >
                  <X size={16} />
                </button>
              </div>

              {/* Expanded images */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 0, alignItems: 'stretch' }}>
                <div style={{ position: 'relative', overflow: 'hidden' }}>
                  {expandedCrop.original && (
                    <img src={`data:image/jpeg;base64,${expandedCrop.original}`} alt="Original" style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }} />
                  )}
                  <div style={{ position: 'absolute', bottom: 10, left: 10, background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(8px)', padding: '4px 12px', borderRadius: 6, fontSize: '0.65rem', fontWeight: 600, color: '#fff', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Original</div>
                </div>
                <div style={{ position: 'relative', overflow: 'hidden' }}>
                  {expandedCrop.heatmap && (
                    <img src={`data:image/jpeg;base64,${expandedCrop.heatmap}`} alt="Heatmap" style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }} />
                  )}
                  <div style={{ position: 'absolute', bottom: 10, left: 10, background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(8px)', padding: '4px 12px', borderRadius: 6, fontSize: '0.65rem', fontWeight: 600, color: 'var(--accent)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Attention Map</div>
                </div>
              </div>

              {/* ═══ DETAILED FORENSIC PANEL ═══ */}
              <div style={{ borderTop: '1px solid var(--border)', padding: '20px 24px' }}>
                {/* Verdict Row */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
                  <div style={{
                    display: 'flex', alignItems: 'center', gap: 8,
                    padding: '6px 14px', borderRadius: 6,
                    background: expandedCrop.score >= 50 ? 'rgba(200,75,75,0.1)' : 'rgba(91,140,90,0.1)',
                    border: `1px solid ${expandedCrop.score >= 50 ? 'rgba(200,75,75,0.2)' : 'rgba(91,140,90,0.2)'}`,
                    color: expandedCrop.score >= 50 ? 'var(--warning)' : 'var(--success)',
                    fontSize: '0.75rem', fontWeight: 600,
                  }}>
                    {expandedCrop.score >= 50 ? <AlertTriangle size={14} /> : <CheckCircle2 size={14} />}
                    {expandedCrop.score >= 50 ? 'Suspected Manipulation' : 'Appears Natural'}
                  </div>
                  <span className="font-mono" style={{ fontSize: '1.6rem', fontWeight: 700, color: expandedCrop.score >= 50 ? 'var(--warning)' : 'var(--success)' }}>
                    {expandedCrop.score}%
                  </span>
                </div>

                {/* Metric Grid */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 16, marginBottom: 20 }}>
                  {/* Neural Score */}
                  <div style={{ padding: '12px 14px', background: 'var(--surface-raised)', borderRadius: 8, border: '1px solid var(--border)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <Cpu size={13} style={{ color: 'var(--accent)' }} />
                        <span className="caps-label" style={{ fontSize: '0.5rem' }}>Neural Detection</span>
                      </div>
                      <span className="font-mono" style={{ fontSize: '0.8rem', fontWeight: 700, color: expandedCrop.score >= 50 ? 'var(--warning)' : 'var(--success)' }}>
                        {expandedCrop.score}%
                      </span>
                    </div>
                    <div style={{ width: '100%', height: 3, background: 'var(--border)', borderRadius: 2, overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: `${expandedCrop.score}%`, background: expandedCrop.score >= 50 ? 'var(--warning)' : 'var(--success)', borderRadius: 2 }} />
                    </div>
                    <p style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: 6, lineHeight: 1.4 }}>
                      ViT pretrained model confidence for synthetic manipulation via 11-view TTA.
                    </p>
                  </div>

                  {/* DCT Frequency */}
                  <div style={{ padding: '12px 14px', background: 'var(--surface-raised)', borderRadius: 8, border: '1px solid var(--border)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <Waves size={13} style={{ color: 'var(--accent)' }} />
                        <span className="caps-label" style={{ fontSize: '0.5rem' }}>DCT Frequency</span>
                      </div>
                      <span className="font-mono" style={{ fontSize: '0.8rem', fontWeight: 700, color: (expandedCrop.freq_score || 0) > 50 ? 'var(--warning)' : 'var(--success)' }}>
                        {expandedCrop.freq_score ?? '—'}%
                      </span>
                    </div>
                    <div style={{ width: '100%', height: 3, background: 'var(--border)', borderRadius: 2, overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: `${expandedCrop.freq_score || 0}%`, background: (expandedCrop.freq_score || 0) > 50 ? 'var(--warning)' : 'var(--success)', borderRadius: 2 }} />
                    </div>
                    <p style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: 6, lineHeight: 1.4 }}>
                      {(expandedCrop.freq_score || 0) > 60
                        ? 'High-frequency GAN fingerprints detected in DCT domain.'
                        : (expandedCrop.freq_score || 0) > 30
                        ? 'Minor spectral irregularities in frequency coefficients.'
                        : 'Frequency spectrum consistent with natural camera capture.'}
                    </p>
                  </div>

                  {/* Compression */}
                  <div style={{ padding: '12px 14px', background: 'var(--surface-raised)', borderRadius: 8, border: '1px solid var(--border)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <Film size={13} style={{ color: 'var(--accent)' }} />
                        <span className="caps-label" style={{ fontSize: '0.5rem' }}>Compression Ghosts</span>
                      </div>
                      <span className="font-mono" style={{ fontSize: '0.8rem', fontWeight: 700, color: (expandedCrop.comp_score || 0) > 50 ? 'var(--warning)' : 'var(--success)' }}>
                        {expandedCrop.comp_score ?? '—'}%
                      </span>
                    </div>
                    <div style={{ width: '100%', height: 3, background: 'var(--border)', borderRadius: 2, overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: `${expandedCrop.comp_score || 0}%`, background: (expandedCrop.comp_score || 0) > 50 ? 'var(--warning)' : 'var(--success)', borderRadius: 2 }} />
                    </div>
                    <p style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: 6, lineHeight: 1.4 }}>
                      {(expandedCrop.comp_score || 0) > 60
                        ? 'Double-JPEG re-compression artifacts suggest image splicing.'
                        : (expandedCrop.comp_score || 0) > 30
                        ? 'Mild compression anomalies — may indicate editing pipeline.'
                        : 'Compression profile consistent with single-pass encoding.'}
                    </p>
                  </div>

                  {/* Face Region */}
                  <div style={{ padding: '12px 14px', background: 'var(--surface-raised)', borderRadius: 8, border: '1px solid var(--border)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <Scan size={13} style={{ color: 'var(--accent)' }} />
                        <span className="caps-label" style={{ fontSize: '0.5rem' }}>Face Region</span>
                      </div>
                      <span className="font-mono" style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                        {expandedCrop.face_width ?? '?'}×{expandedCrop.face_height ?? '?'}px
                      </span>
                    </div>
                    <p style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: 4, lineHeight: 1.4 }}>
                      {((expandedCrop.face_width || 0) * (expandedCrop.face_height || 0)) > 40000
                        ? 'High-resolution face capture — strong signal quality for analysis.'
                        : ((expandedCrop.face_width || 0) * (expandedCrop.face_height || 0)) > 10000
                        ? 'Moderate face resolution — adequate for forensic inference.'
                        : 'Low-resolution face capture — detection confidence may be reduced.'}
                    </p>
                  </div>
                </div>

                {/* Attention Interpretation */}
                <div style={{ padding: '12px 16px', background: 'var(--surface-raised)', borderRadius: 8, border: '1px solid var(--border)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                    <Sparkles size={13} style={{ color: 'var(--accent)' }} />
                    <span className="caps-label" style={{ fontSize: '0.55rem', color: 'var(--accent)' }}>Attention Interpretation</span>
                  </div>
                  <p style={{ fontFamily: "'Lora', serif", fontSize: '0.85rem', lineHeight: 1.6, fontStyle: 'italic', color: 'var(--text)', opacity: 0.85 }}>
                    {expandedCrop.score > 70
                      ? 'The model\'s attention is strongly concentrated on specific facial regions, suggesting localized artifacts consistent with face-swap or generation techniques. The red hotspots indicate where the neural detector identified the strongest manipulation signatures.'
                      : expandedCrop.score > 55
                      ? 'Moderate attention clustering detected around facial features. The model identified some regions that deviate from natural patterns, possibly indicating cosmetic filtering, partial editing, or early signs of synthetic generation.'
                      : expandedCrop.score > 35
                      ? 'The attention distribution is relatively diffuse across the face, with no strong concentration on specific regions. Minor hotspots may correspond to makeup, lighting artifacts, or normal facial asymmetry rather than manipulation.'
                      : 'The attention map shows a natural, evenly distributed pattern with no suspicious concentration points. This face appears to exhibit authentic pixel-level characteristics consistent with unaltered camera footage.'}
                  </p>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

/* ─── Sub-components ─── */

function SectionHeader({ title, sub }) {
  return (
    <div style={{ display: 'flex', alignItems: 'baseline', gap: 12, borderBottom: '1px solid var(--border)', paddingBottom: 12, marginBottom: 24 }}>
      <h2 style={{ fontFamily: "'Lora', serif", fontSize: '1.5rem', fontWeight: 500, color: 'var(--text)' }}>{title}</h2>
      <span className="caps-label" style={{ opacity: 0.6, fontSize: '0.55rem' }}>{sub}</span>
    </div>
  );
}

function MetaRow({ label, value }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', borderBottom: '1px dashed var(--border)', paddingBottom: 8 }}>
      <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{label}</span>
      <span className="font-mono" style={{ fontSize: '0.75rem', color: 'var(--text)', background: 'var(--surface)', padding: '2px 8px', borderRadius: 4 }}>{value}</span>
    </div>
  );
}

function Gauge({ icon, label, value, desc, delay }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{ color: 'var(--accent)', background: 'var(--accent-light)', padding: 6, borderRadius: 6, display: 'flex' }}>{icon}</div>
          <span style={{ fontFamily: "'Lora', serif", fontSize: '1rem', fontWeight: 500, color: 'var(--text)' }}>{label}</span>
        </div>
        <span className="font-mono" style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--accent)' }}>{value}%</span>
      </div>
      <div style={{ width: '100%', height: 5, background: 'var(--border)', borderRadius: 3, overflow: 'hidden' }}>
        <motion.div
          style={{ height: '100%', background: 'var(--accent)', borderRadius: 3 }}
          initial={{ width: '0%' }}
          animate={{ width: `${value}%` }}
          transition={{ duration: 1.2, ease: 'easeOut', delay }}
        />
      </div>
      <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: 1.5, marginTop: 2 }}>{desc}</p>
    </div>
  );
}

function EvidenceRow({ title, icon, items, isFrame, count }) {
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border)', paddingBottom: 10, marginBottom: 16 }}>
        <h3 style={{ fontFamily: "'Lora', serif", fontSize: '1.15rem', fontWeight: 500, color: 'var(--text)', display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ color: 'var(--text-muted)' }}>{icon}</span> {title}
        </h3>
        <span className="caps-label" style={{ background: 'var(--surface-raised)', padding: '3px 10px', borderRadius: 4, fontSize: '0.55rem' }}>{count} {isFrame ? 'Keyframes' : 'Regions'}</span>
      </div>
      <div style={{ display: 'flex', gap: 12, overflowX: 'auto', paddingBottom: 8 }}>
        {(!items || items.length === 0) && <p style={{ color: 'var(--text-muted)', fontStyle: 'italic', fontSize: '0.85rem' }}>No {isFrame ? 'keyframes' : 'regions'} extracted.</p>}
        {items?.map((item, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, scale: 0.92 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4, delay: i * 0.07 }}
            style={{ flexShrink: 0, display: 'flex', flexDirection: 'column', gap: 6 }}
          >
            <div style={{
              position: 'relative', overflow: 'hidden', borderRadius: 8,
              border: '1px solid var(--border)',
              width: isFrame ? 200 : 100, height: isFrame ? 130 : 100,
            }}>
              <img
                src={`data:image/jpeg;base64,${item.thumbnail || item.image}`}
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                alt="Evidence"
              />
              <div style={{
                position: 'absolute', top: 6, right: 6,
                background: 'rgba(0,0,0,0.65)', backdropFilter: 'blur(8px)',
                padding: '2px 8px', borderRadius: 4,
                fontSize: '0.6rem', fontFamily: "'JetBrains Mono', monospace", fontWeight: 600, color: '#fff',
              }}>
                {item.score?.toFixed(1)}%
              </div>
            </div>
            <span className="caps-label" style={{ textAlign: 'center', fontSize: '0.5rem', opacity: 0.7 }}>
              {isFrame ? `${item.timestamp?.toFixed(1)}s` : 'Isolated'}
            </span>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
