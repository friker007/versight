import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Loader2, Scan } from 'lucide-react';

export default function ProcessingScanner({ file, url, onComplete, onTentative, onError }) {
  const [progress, setProgress] = useState(0);
  const [step, setStep] = useState('Initializing review protocol...');
  const [details, setDetails] = useState('');
  const [liveCrops, setLiveCrops] = useState([]);

  useEffect(() => {
    const controller = new AbortController();

    const run = async () => {
      try {
        const host = window.location.hostname;
        const apiBase = `http://${host}:8010`;
        let endpoint = '';
        let formData = new FormData();
        let body = null;

        if (file) {
          endpoint = `${apiBase}/api/analyze/stream/upload`;
          formData.append('file', file);
          body = formData;
        } else if (url) {
          endpoint = `${apiBase}/api/analyze/stream/url`;
          body = JSON.stringify({ url });
        }

        const res = await fetch(endpoint, {
          method: 'POST',
          headers: url ? { 'Content-Type': 'application/json' } : {},
          body,
          signal: controller.signal
        });

        if (!res.ok) throw new Error('Network response was not ok');

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n\n');
          buffer = lines.pop(); // Keep incomplete chunk

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = JSON.parse(line.substring(6));
              if (data.status === 'processing') {
                setProgress(p => Math.max(p, data.progress));
                setStep(data.step);
                if (data.details) setDetails(data.details);
              } else if (data.status === 'tentative') {
                // Extract face crops from tentative results for live preview
                if (data.result?.face_crops?.length > 0) {
                  setLiveCrops(data.result.face_crops);
                }
                if (onTentative) onTentative(data.result);
              } else if (data.status === 'complete') {
                setProgress(100);
                setStep('Finalizing editorial report...');
                if (data.result?.face_crops?.length > 0) {
                  setLiveCrops(data.result.face_crops);
                }
                setTimeout(() => {
                  onComplete(data.result);
                }, 800);
              } else if (data.status === 'error') {
                throw new Error(data.detail);
              }
            }
          }
        }
      } catch (err) {
        if (err.name !== 'AbortError') {
          onError(err.message);
        }
      }
    };

    run();

    return () => {
      controller.abort();
    };
  }, [file, url]);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.97 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6 }}
      style={{ width: '100%', maxWidth: 700, margin: '0 auto', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 32 }}
    >
      <div className="editorial-card" style={{ width: '100%', padding: '64px 48px', display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>

        {/* Spinner */}
        <div style={{ position: 'relative', width: 96, height: 96, marginBottom: 40, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          {/* Outer ring */}
          <svg width={96} height={96} style={{ position: 'absolute' }}>
            <circle cx={48} cy={48} r={44} fill="none" stroke="var(--border)" strokeWidth={2} />
            <motion.circle
              cx={48} cy={48} r={44}
              fill="none" stroke="var(--accent)" strokeWidth={3}
              strokeDasharray={276.5}
              initial={{ strokeDashoffset: 276.5 }}
              animate={{ strokeDashoffset: 276.5 - (276.5 * progress) / 100 }}
              transition={{ duration: 0.8, ease: 'easeOut' }}
              strokeLinecap="round"
              style={{ transform: 'rotate(-90deg)', transformOrigin: '50% 50%' }}
            />
          </svg>
          <Loader2 size={28} style={{ color: 'var(--accent)', animation: 'spin 2s linear infinite' }} />
        </div>

        <h2 style={{ fontFamily: "'Lora', serif", fontSize: '1.6rem', fontWeight: 500, marginBottom: 12, color: 'var(--text)' }}>
          Inspecting Media
        </h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', minHeight: 28, marginBottom: 8, transition: 'all 0.3s ease' }}>
          {step}
        </p>
        {details && (
          <p className="font-mono" style={{ color: 'var(--text-muted)', fontSize: '0.7rem', marginBottom: 24, opacity: 0.6 }}>
            {details}
          </p>
        )}

        {/* Progress bar */}
        <div style={{ width: '100%', height: 4, background: 'var(--border)', borderRadius: 2, overflow: 'hidden', marginBottom: 16 }}>
          <motion.div
            style={{ height: '100%', background: 'var(--accent)', borderRadius: 2 }}
            initial={{ width: '0%' }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.6, ease: 'easeOut' }}
          />
        </div>

        <div style={{ width: '100%', display: 'flex', justifyContent: 'space-between' }}>
          <span className="caps-label" style={{ fontSize: '0.55rem' }}>ANALYSIS IN PROGRESS</span>
          <span className="font-mono" style={{ fontSize: '0.75rem', color: 'var(--accent)', fontWeight: 600 }}>{Math.round(progress)}%</span>
        </div>
      </div>

      {/* ═══ LIVE HEATMAP FEED ═══ */}
      <AnimatePresence>
        {liveCrops.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            style={{ width: '100%' }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
              <Scan size={14} style={{ color: 'var(--accent)' }} />
              <span className="caps-label" style={{ color: 'var(--accent)', fontSize: '0.6rem' }}>
                LIVE FACE ISOLATIONS — ATTENTION HEATMAPS
              </span>
            </div>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))',
              gap: 12,
            }}>
              {liveCrops.slice(0, 6).map((crop, i) => (
                <motion.div
                  key={`live-${i}`}
                  initial={{ opacity: 0, scale: 0.85 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.4, delay: i * 0.08 }}
                  style={{
                    borderRadius: 10,
                    overflow: 'hidden',
                    border: '1px solid var(--border)',
                    background: 'var(--surface)',
                  }}
                >
                  {/* Heatmap overlay image */}
                  {crop.heatmap ? (
                    <img
                      src={`data:image/jpeg;base64,${crop.heatmap}`}
                      alt={`Attention heatmap ${i + 1}`}
                      style={{ width: '100%', aspectRatio: '1', objectFit: 'cover', display: 'block' }}
                    />
                  ) : crop.original ? (
                    <img
                      src={`data:image/jpeg;base64,${crop.original}`}
                      alt={`Face crop ${i + 1}`}
                      style={{ width: '100%', aspectRatio: '1', objectFit: 'cover', display: 'block' }}
                    />
                  ) : (
                    <div style={{ width: '100%', aspectRatio: '1', background: 'var(--surface-raised)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <Scan size={20} style={{ color: 'var(--text-muted)', opacity: 0.3 }} />
                    </div>
                  )}

                  {/* Score badge */}
                  <div style={{
                    padding: '6px 10px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    borderTop: '1px solid var(--border)',
                  }}>
                    <span className="caps-label" style={{ fontSize: '0.5rem' }}>F#{crop.frame_index}</span>
                    <span className="font-mono" style={{
                      fontSize: '0.7rem',
                      fontWeight: 600,
                      color: crop.score > 55 ? 'var(--warning)' : 'var(--success)',
                    }}>
                      {crop.score}%
                    </span>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </motion.div>
  );
}
