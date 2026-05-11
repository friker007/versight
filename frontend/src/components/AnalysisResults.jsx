import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Download, RotateCcw, Cpu, Waves, Sparkles, History, Film, Scan, CheckCircle2, AlertTriangle, X, ZoomIn, Brain, Fingerprint, Activity, Heart, Eye, ShieldCheck, ShieldAlert, User } from 'lucide-react';

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
  const identities = results.identities || [];
  const [activeId, setActiveId] = useState(identities.length > 0 ? identities[0].identity_id : null);

  const overall_score = results.score ?? 0;
  const video_metadata = results.metadata || {};
  const isDeepfake = results.is_deepfake ?? (overall_score >= 50);

  const activeIdentity = identities.find(i => i.identity_id === activeId) || identities[0];

  return (
    <motion.div variants={stagger} initial="hidden" animate="show" style={{ width: '100%', maxWidth: 1100, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 40, padding: '0 16px' }}>

      {/* ═══ HEADER ═══ */}
      <motion.div variants={fadeUp} style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'flex-end', gap: 24, borderBottom: '1px solid var(--border)', paddingBottom: 24 }}>
        <div>
          <div className="caps-label" style={{ color: 'var(--accent)', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ width: 24, height: 1.5, background: 'var(--accent)', display: 'inline-block' }} />
            Multi-Subject Identity Audit
          </div>
          <h1 style={{ fontFamily: "'Lora', serif", fontSize: 'clamp(2rem, 4vw, 3.5rem)', fontWeight: 500, lineHeight: 1.1, color: 'var(--text)' }}>
            Identity{' '}<br /><span style={{ fontStyle: 'italic', color: 'var(--text-muted)' }}>Risk Breakdown.</span>
          </h1>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <button className="editorial-btn"><Download size={14} /> Export PDF</button>
          <button onClick={onRestart} className="editorial-btn primary"><RotateCcw size={14} /> New Analysis</button>
        </div>
      </motion.div>

      {/* ═══ GLOBAL OVERVIEW ═══ */}
      <motion.div variants={fadeUp} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 24 }}>
          <div className="editorial-card" style={{ padding: '28px', display: 'flex', alignItems: 'center', gap: 24 }}>
            <div style={{ position: 'relative', width: 100, height: 100, flexShrink: 0 }}>
              <svg width={100} height={100} viewBox="0 0 100 100" style={{ transform: 'rotate(-90deg)' }}>
                <circle cx={50} cy={50} r={46} fill="none" stroke="var(--border)" strokeWidth={3} />
                <motion.circle
                  cx={50} cy={50} r={46} fill="none"
                  stroke={isDeepfake ? 'var(--warning)' : 'var(--success)'}
                  strokeWidth={5}
                  strokeDasharray={289}
                  initial={{ strokeDashoffset: 289 }}
                  animate={{ strokeDashoffset: 289 - (289 * overall_score) / 100 }}
                  transition={{ duration: 1.5 }}
                  strokeLinecap="round"
                />
              </svg>
              <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.8rem', fontWeight: 500, color: 'var(--text)', fontFamily: "'Lora', serif" }}>
                {overall_score.toFixed(0)}%
              </div>
            </div>
            <div>
              <h3 style={{ fontFamily: "'Lora', serif", fontSize: '1.2rem', marginBottom: 8, color: 'var(--text)' }}>Peak Vector Score</h3>
              <div style={{
                display: 'inline-flex', alignItems: 'center', gap: 6, padding: '6px 12px', borderRadius: 6,
                background: isDeepfake ? 'rgba(200,75,75,0.1)' : 'rgba(91,140,90,0.1)',
                border: `1px solid ${isDeepfake ? 'rgba(200,75,75,0.2)' : 'rgba(91,140,90,0.2)'}`,
                color: isDeepfake ? 'var(--warning)' : 'var(--success)', fontSize: '0.75rem', fontWeight: 600,
              }}>
                {isDeepfake ? <AlertTriangle size={14} /> : <CheckCircle2 size={14} />}
                {isDeepfake ? 'Synthetic Signal Detected' : 'Clean Integrity'}
              </div>
            </div>
          </div>

          {/* Metadata short-strip */}
          <div style={{ padding: '20px 24px', background: 'var(--surface-raised)', borderRadius: 12, display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 10 }}>
            <MetaRow label="Resolution" value={`${video_metadata?.width || 0}x${video_metadata?.height || 0}`} />
            <MetaRow label="Detection Pool" value={`${video_metadata?.frames_analyzed || 0} Frames`} />
            <MetaRow label="Cluster Total" value={`${identities.length} Identified Subjects`} />
          </div>
      </motion.div>

      {/* ═══ IDENTITY PICKER ═══ */}
      <motion.section variants={fadeUp}>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 12, marginBottom: 20 }}>
          <h2 style={{ fontFamily: "'Lora', serif", fontSize: '1.3rem', color: 'var(--text)' }}>Detected Identities</h2>
          <span className="caps-label" style={{ opacity: 0.6, fontSize: '0.55rem' }}>Select subject for audit details</span>
        </div>

        <div style={{ display: 'flex', gap: 16, overflowX: 'auto', paddingBottom: 12 }}>
          {identities.map((person) => {
            const isActive = person.identity_id === activeId;
            const isHighRisk = person.score >= 50;
            return (
              <motion.button
                key={person.identity_id}
                whileHover={{ y: -4 }}
                whileTap={{ scale: 0.97 }}
                onClick={() => setActiveId(person.identity_id)}
                style={{
                  flexShrink: 0, display: 'flex', alignItems: 'center', gap: 14,
                  background: isActive ? 'var(--surface-raised)' : 'transparent',
                  border: `1px solid ${isActive ? 'var(--accent)' : 'var(--border)'}`,
                  borderRadius: 12, padding: '10px 16px', cursor: 'pointer',
                  transition: 'all 0.2s ease', textAlign: 'left',
                  minWidth: 200
                }}
              >
                <div style={{ position: 'relative', width: 48, height: 48, borderRadius: '50%', overflow: 'hidden', border: `2px solid ${isHighRisk ? 'var(--warning)' : 'var(--success)'}`, flexShrink: 0 }}>
                  <img src={`data:image/jpeg;base64,${person.avatar}`} style={{ width: '100%', height: '100%', objectFit: 'cover' }} alt={person.name} />
                </div>
                <div>
                  <div style={{ fontFamily: "'Lora', serif", fontWeight: 500, color: 'var(--text)', fontSize: '0.95rem' }}>{person.name}</div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 4 }}>
                    <div style={{ width: 6, height: 6, borderRadius: '50%', background: isHighRisk ? 'var(--warning)' : 'var(--success)' }} />
                    <span className="caps-label" style={{ fontSize: '0.55rem', color: isHighRisk ? 'var(--warning)' : 'var(--text-muted)' }}>{person.score.toFixed(0)}% Risk</span>
                  </div>
                </div>
              </motion.button>
            );
          })}
          {identities.length === 0 && (
            <div style={{ padding: '20px', color: 'var(--text-muted)', fontStyle: 'italic', fontSize: '0.9rem' }}>No unique subjects resolved.</div>
          )}
        </div>
      </motion.section>

      {/* ═══ ACTIVE SUBJECT DETAILS ═══ */}
      {activeIdentity && (
        <AnimatePresence mode="wait">
          <motion.div
            key={activeIdentity.identity_id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.4 }}
            style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 32 }}
          >
            {/* LEFT SUB: Vector Checklist */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
              <div className="caps-label" style={{ borderBottom: '1px solid var(--border)', paddingBottom: 10 }}>Security Vector Checklist</div>
              {activeIdentity.vector_audit?.map((v, idx) => (
                <div key={v.id} className="editorial-card" style={{ padding: '20px', display: 'flex', gap: 16, alignItems: 'flex-start', borderLeft: `3px solid ${v.status === 'PASS' ? 'var(--success)' : 'var(--warning)'}` }}>
                  <div style={{ color: v.status === 'PASS' ? 'var(--success)' : 'var(--warning)', flexShrink: 0, marginTop: 2 }}>
                    {v.status === 'PASS' ? <ShieldCheck size={24} /> : <ShieldAlert size={24} />}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 4 }}>
                      <h4 style={{ fontFamily: "'Lora', serif", fontSize: '1.05rem', color: 'var(--text)' }}>{v.label}</h4>
                      <span className="caps-label" style={{ fontSize: '0.55rem', color: v.status === 'PASS' ? 'var(--success)' : 'var(--warning)' }}>{v.status}</span>
                    </div>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>{v.desc}</p>
                  </div>
                </div>
              ))}

              {/* Gemini Note attached to current selection context */}
              <div style={{ marginTop: 10, padding: '16px', background: 'rgba(255,255,255,0.02)', borderRadius: 10, border: '1px dashed var(--border)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
                  <Sparkles size={12} style={{ color: 'var(--accent)' }} />
                  <span className="caps-label" style={{ fontSize: '0.55rem' }}>AI Forensics Note</span>
                </div>
                <p style={{ fontSize: '0.8rem', fontStyle: 'italic', color: 'var(--text)', lineHeight: 1.5, opacity: 0.8 }}>
                  "{results.gemini_context || 'Baseline pattern consistent.'}"
                </p>
              </div>
            </div>

            {/* RIGHT SUB: Primary Evidence Heatmap */}
            <div>
               <div className="caps-label" style={{ borderBottom: '1px solid var(--border)', paddingBottom: 10, marginBottom: 20 }}>Deepest Anomaly Scan</div>
               <div 
                 className="editorial-card" 
                 style={{ padding: 0, overflow: 'hidden', cursor: 'zoom-in' }}
                 onClick={() => setExpandedCrop({
                    heatmap: activeIdentity.heatmap,
                    original: activeIdentity.avatar,
                    score: activeIdentity.score,
                    frame_index: "Peak"
                 })}
               >
                 <div style={{ position: 'relative', aspectRatio: '16/9' }}>
                   <img 
                     src={`data:image/jpeg;base64,${activeIdentity.heatmap}`} 
                     style={{ width: '100%', height: '100%', objectFit: 'cover' }} 
                     alt="Subject Heatmap" 
                   />
                   <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(transparent, rgba(0,0,0,0.6))' }} />
                   <div style={{ position: 'absolute', bottom: 16, left: 16, color: '#fff' }}>
                     <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                       <Scan size={16} style={{ color: 'var(--accent)' }} />
                       <span style={{ fontFamily: "'Lora', serif", fontWeight: 500 }}>Forensic Attention View</span>
                     </div>
                   </div>
                 </div>
                 <div style={{ padding: '16px', fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                   Model focus distributed across high-risk biometric landmarks for <b>{activeIdentity.name}</b>. Highlighted areas (Red) are mathematically aberrant.
                 </div>
               </div>
            </div>
          </motion.div>
        </AnimatePresence>
      )}

      {/* ═══ LIGHTBOX (Reused logic from previous) ═══ */}
      <AnimatePresence>
        {expandedCrop && (
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            onClick={() => setExpandedCrop(null)}
            style={{ position: 'fixed', inset: 0, zIndex: 9999, background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(12px)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24, cursor: 'pointer' }}
          >
            <motion.div
              initial={{ scale: 0.85 }} animate={{ scale: 1 }} exit={{ scale: 0.85 }}
              onClick={(e) => e.stopPropagation()}
              style={{ background: 'var(--surface)', borderRadius: 16, border: '1px solid var(--border)', maxWidth: 800, width: '100%', overflow: 'hidden', cursor: 'default' }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '16px 20px', borderBottom: '1px solid var(--border)' }}>
                <span style={{ fontFamily: "'Lora', serif", fontWeight: 500 }}>Attention Depth Map</span>
                <button onClick={() => setExpandedCrop(null)} style={{ background: 'none', border: 'none', color: '#fff', cursor: 'pointer' }}><X size={20} /></button>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', background: '#000' }}>
                 <img src={`data:image/jpeg;base64,${expandedCrop.original}`} style={{ width: '100%', objectFit: 'cover' }} alt="Original" />
                 <img src={`data:image/jpeg;base64,${expandedCrop.heatmap}`} style={{ width: '100%', objectFit: 'cover' }} alt="Heatmap" />
              </div>
              <div style={{ padding: '20px', textAlign: 'center' }}>
                <span style={{ fontFamily: "'Lora', serif", fontSize: '1.5rem', color: expandedCrop.score >= 50 ? 'var(--warning)' : 'var(--success)' }}>{expandedCrop.score}% Anomaly Strength</span>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

function MetaRow({ label, value }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', paddingBottom: 6 }}>
      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{label}</span>
      <span className="font-mono" style={{ fontSize: '0.75rem', color: 'var(--text)', fontWeight: 600 }}>{value}</span>
    </div>
  );
}
