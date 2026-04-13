import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';

export default function ProcessingScanner({ file, url, onComplete, onTentative, onError }) {
  const [progress, setProgress] = useState(0);
  const [step, setStep] = useState('Initializing review protocol...');

  useEffect(() => {
    const controller = new AbortController();

    const run = async () => {
      try {
        let endpoint = '';
        let formData = new FormData();
        let body = null;

        if (file) {
          endpoint = 'http://127.0.0.1:8010/api/analyze/stream/upload';
          formData.append('file', file);
          body = formData;
        } else if (url) {
          endpoint = 'http://127.0.0.1:8010/api/analyze/stream/url';
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
              } else if (data.status === 'tentative') {
                if (onTentative) onTentative(data.result);
              } else if (data.status === 'complete') {
                setProgress(100);
                setStep('Finalizing editorial report...');
                // Slight delay for visual satisfaction
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
      style={{ width: '100%', maxWidth: 560, margin: '0 auto', display: 'flex', flexDirection: 'column', alignItems: 'center' }}
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
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', minHeight: 28, marginBottom: 32, transition: 'all 0.3s ease' }}>
          {step}
        </p>

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

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </motion.div>
  );
}
