import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Moon, Sun, Sparkles, Activity, Database } from 'lucide-react';
import UploadWidget from './components/UploadWidget';
import AnalysisResults from './components/AnalysisResults';
import ProcessingScanner from './components/ProcessingScanner';
import ParticlesBackground from './components/ParticlesBackground';

export default function App() {
  const [status, setStatus] = useState('idle');
  const [results, setResults] = useState(null);
  const [activeMedia, setActiveMedia] = useState({ file: null, url: '' });
  const [theme, setTheme] = useState('dark');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme(p => (p === 'dark' ? 'light' : 'dark'));

  const handleStart = (file, url) => {
    setActiveMedia({ file, url });
    setStatus('processing');
  };

  const handleComplete = (data) => {
    setResults(data);
    setStatus('results');
  };

  const handleRestart = () => {
    setResults(null);
    setActiveMedia({ file: null, url: '' });
    setStatus('idle');
  };

  const fade = {
    initial: { opacity: 0, y: 24 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -16 },
    transition: { duration: 0.55, ease: [0.22, 1, 0.36, 1] },
  };

  return (
    <div style={{ backgroundColor: 'var(--bg)', color: 'var(--text)', minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', transition: 'background-color 0.5s ease, color 0.5s ease' }}>
      <ParticlesBackground />
      {/* ═══════════ NAV ═══════════ */}
      <motion.nav
        initial={{ opacity: 0, y: -16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7 }}
        style={{ position: 'relative', zIndex: 10, width: '100%', maxWidth: 1200, display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '28px 32px', boxSizing: 'border-box' }}
      >
        <span
          onClick={handleRestart}
          style={{ fontFamily: "'Lora', serif", fontSize: '1.75rem', fontWeight: 600, cursor: 'pointer', letterSpacing: '-0.02em', color: 'var(--text)' }}
        >
          Versight.
        </span>

        <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
          <span className="caps-label" style={{ cursor: 'pointer', fontSize: '0.7rem', letterSpacing: '0.15em', color: 'var(--text-muted)' }}>Manifesto</span>
          <span className="caps-label" style={{ cursor: 'pointer', fontSize: '0.7rem', letterSpacing: '0.15em', color: 'var(--text-muted)' }}>Protocol</span>
          <div style={{ width: 1, height: 16, background: 'var(--border)' }} />
          <button
            onClick={toggleTheme}
            style={{ background: 'none', border: '1px solid var(--border)', borderRadius: 6, width: 36, height: 36, display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', color: 'var(--text-muted)' }}
            title="Toggle Theme"
          >
            {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
          </button>
        </div>
      </motion.nav>

      {/* ═══════════ MAIN ═══════════ */}
      <main style={{ position: 'relative', zIndex: 10, flex: 1, width: '100%', maxWidth: 960, padding: '0 24px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <AnimatePresence mode="wait">

          {/* ─── IDLE ─── */}
          {status === 'idle' && (
            <motion.div key="idle" {...fade} style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>

              {/* Hero */}
              <div style={{ textAlign: 'center', paddingTop: 80, paddingBottom: 72, maxWidth: 720 }}>
                <motion.div
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.15, duration: 0.4 }}
                  style={{ marginBottom: 28 }}
                >
                  <span className="caps-label" style={{ fontSize: '0.6rem', letterSpacing: '0.2em', paddingBottom: 4, borderBottom: '1.5px solid var(--accent)', color: 'var(--accent)' }}>
                    ISSUE 04 — EDITORIAL REVIEW PROTOCOL
                  </span>
                </motion.div>

                <h1 style={{ fontFamily: "'Lora', serif", fontSize: 'clamp(2.4rem, 6vw, 5rem)', fontWeight: 500, lineHeight: 1.08, letterSpacing: '-0.02em', marginBottom: 24, color: 'var(--text)' }}>
                  Verify the integrity of{' '}
                  <br />
                  <span style={{ fontStyle: 'italic', color: 'var(--text-muted)' }}>digital media.</span>
                </h1>

                <p style={{ color: 'var(--text-muted)', fontSize: '1.05rem', lineHeight: 1.7, maxWidth: 560, margin: '0 auto' }}>
                  An elegant, archival-grade forensic instrument designed for the AI era.
                  Detecting synthetic alterations with uncompromising precision.
                </p>
              </div>

              {/* Upload */}
              <div style={{ width: '100%', maxWidth: 640, marginBottom: 100 }}>
                <UploadWidget onSelect={handleStart} />
              </div>

              {/* Features */}
              <div style={{ width: '100%', borderTop: '1px solid var(--border)', paddingTop: 64, paddingBottom: 80, display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 48 }}>
                <Feature icon={<Database size={22} strokeWidth={1.5} />} title="Stateless Privacy." desc="Files are inspected in-memory and never retained. Absolute editorial confidentiality." delay={0.1} />
                <Feature icon={<Sparkles size={22} strokeWidth={1.5} />} title="Neural Inspection." desc="Multi-layer CNN architectures cross-referenced with Gemini logical reasoning." delay={0.2} />
                <Feature icon={<Activity size={22} strokeWidth={1.5} />} title="Optical Coherence." desc="Sub-pixel consistency checking isolating temporal anomalies and lighting physics." delay={0.3} />
              </div>
            </motion.div>
          )}

          {/* ─── PROCESSING & SOCKET LAYER ─── */}
          {(status === 'processing' || status === 'results') && (
            <div key="processing-layer" style={{ display: status === 'processing' ? 'block' : 'none', width: '100%', padding: '80px 0' }}>
              <motion.div {...fade}>
                <ProcessingScanner
                  file={activeMedia.file}
                  url={activeMedia.url}
                  onTentative={(data) => {
                    // Surface immediate results, keep connection alive invisibly
                    setResults(data);
                    setStatus('results');
                  }}
                  onComplete={(data) => {
                    // Smartly update results with identical state when backend fully finishes
                    setResults(data);
                    setStatus('results');
                  }}
                  onError={(err) => { console.error(err); setStatus('idle'); alert(`Inspection Error: ${err}`); }}
                />
              </motion.div>
            </div>
          )}

          {/* ─── RESULTS ─── */}
          {status === 'results' && (
            <motion.div key="results" {...fade} style={{ width: '100%', padding: '40px 0 80px' }}>
              <AnalysisResults results={results} onRestart={handleRestart} />
            </motion.div>
          )}

        </AnimatePresence>
      </main>

      {/* ═══════════ FOOTER ═══════════ */}
      <footer style={{ position: 'relative', zIndex: 10, width: '100%', borderTop: '1px solid var(--border)', padding: '24px 32px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
        <span style={{ fontFamily: "'Lora', serif", fontStyle: 'italic' }}>Versight Digital Forensics © {new Date().getFullYear()}</span>
        <span className="caps-label" style={{ opacity: 0.5 }}>Volume 4 — Issue 02</span>
      </footer>
    </div>
  );
}

/* ─── Feature Card ─── */
function Feature({ icon, title, desc, delay }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay }}
      style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', gap: 16 }}
    >
      <div style={{ width: 48, height: 48, borderBottom: '2px solid var(--accent)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent)', marginBottom: 4 }}>
        {icon}
      </div>
      <h3 style={{ fontFamily: "'Lora', serif", fontSize: '1.35rem', fontWeight: 500, color: 'var(--text)', marginBottom: 4 }}>{title}</h3>
      <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', lineHeight: 1.65, maxWidth: 260 }}>{desc}</p>
    </motion.div>
  );
}
