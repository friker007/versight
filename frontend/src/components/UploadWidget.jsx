import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, Link as LinkIcon, FileImage, X, ArrowRight } from 'lucide-react';

export default function UploadWidget({ onSelect }) {
  const [dragActive, setDragActive] = useState(false);
  const [tab, setTab] = useState('file');
  const [url, setUrl] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const inputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault(); e.stopPropagation();
    setDragActive(e.type === 'dragenter' || e.type === 'dragover');
  };

  const handleDrop = (e) => {
    e.preventDefault(); e.stopPropagation(); setDragActive(false);
    if (e.dataTransfer.files?.[0]) setSelectedFile(e.dataTransfer.files[0]);
  };

  const handleChange = (e) => {
    if (e.target.files?.[0]) setSelectedFile(e.target.files[0]);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (tab === 'file' && selectedFile) onSelect(selectedFile, null);
    else if (tab === 'url' && url.trim()) onSelect(null, url.trim());
  };

  const clear = () => { setSelectedFile(null); setUrl(''); };

  /* ─── Shared card styles ─── */
  const card = {
    background: 'var(--surface)',
    border: '1px solid var(--border)',
    borderRadius: 12,
    padding: '40px 48px',
    boxShadow: 'var(--shadow-card)',
    width: '100%',
    maxWidth: 600,
    margin: '0 auto',
    transition: 'box-shadow 0.3s ease',
  };

  const tabStyle = (active) => ({
    background: 'none',
    border: 'none',
    outline: 'none',
    cursor: 'pointer',
    display: 'flex', alignItems: 'center', gap: 8,
    fontSize: '0.85rem', fontWeight: 500,
    fontFamily: "'Inter', sans-serif",
    color: active ? 'var(--text)' : 'var(--text-muted)',
    paddingBottom: 12,
    borderBottom: active ? '2px solid var(--accent)' : '2px solid transparent',
    transition: 'all 0.25s ease',
  });

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      style={card}
    >
      {/* Tabs */}
      <div style={{ display: 'flex', gap: 32, borderBottom: '1px solid var(--border)', marginBottom: 36 }}>
        <button onClick={() => setTab('file')} style={tabStyle(tab === 'file')}>
          <Upload size={16} /> Direct Upload
        </button>
        <button onClick={() => setTab('url')} style={tabStyle(tab === 'url')}>
          <LinkIcon size={16} /> Web Media
        </button>
      </div>

      {/* Content */}
      <AnimatePresence mode="wait">
        {tab === 'file' ? (
          <motion.form
            key="file"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }}
            transition={{ duration: 0.3 }}
            onSubmit={handleSubmit}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            style={{
              minHeight: 280,
              border: dragActive ? '2px solid var(--accent)' : '1.5px dashed var(--border)',
              borderRadius: 10,
              display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
              background: dragActive ? 'var(--accent-light)' : 'var(--surface-raised)',
              transition: 'all 0.3s ease',
              padding: 40,
            }}
          >
            <input ref={inputRef} type="file" hidden accept="video/mp4,video/quicktime,video/x-msvideo" onChange={handleChange} />

            {!selectedFile ? (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', pointerEvents: 'none' }}>
                <div style={{
                  width: 56, height: 56, borderRadius: 10,
                  border: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'center',
                  color: 'var(--accent)', marginBottom: 20, background: 'var(--surface)',
                }}>
                  <Upload size={24} strokeWidth={1.5} />
                </div>
                <h3 style={{ fontFamily: "'Lora', serif", fontSize: '1.5rem', fontWeight: 500, marginBottom: 8, color: 'var(--text)' }}>
                  Select media to analyze
                </h3>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', lineHeight: 1.6, maxWidth: 280, marginBottom: 24 }}>
                  Drag a file here, or click below to browse your collection.
                </p>
                <div style={{ pointerEvents: 'auto' }}>
                  <button type="button" onClick={() => inputRef.current?.click()} className="editorial-btn" style={{ padding: '10px 28px' }}>
                    Browse Files
                  </button>
                </div>
                <span className="caps-label" style={{ marginTop: 24, opacity: 0.5, fontSize: '0.55rem', letterSpacing: '0.18em' }}>
                  SUPPORTS MP4 / MOV / AVI
                </span>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
                <div style={{ position: 'relative', width: 64, height: 64, borderRadius: 10, border: '1px solid var(--success)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--success)', marginBottom: 20, background: 'var(--surface)' }}>
                  <FileImage size={28} strokeWidth={1.5} />
                  <button
                    type="button"
                    onClick={(e) => { e.preventDefault(); clear(); }}
                    style={{ position: 'absolute', top: -10, right: -10, width: 28, height: 28, borderRadius: 6, border: '1px solid var(--border)', background: 'var(--surface)', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', color: 'var(--text-muted)' }}
                  >
                    <X size={12} />
                  </button>
                </div>
                <div style={{ fontFamily: "'Lora', serif", fontSize: '1.3rem', fontWeight: 500, marginBottom: 6, color: 'var(--text)', maxWidth: '90%', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {selectedFile.name}
                </div>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: 28 }}>
                  {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB — Ready
                </div>
                <button type="submit" className="editorial-btn primary" style={{ padding: '12px 32px', fontSize: '0.85rem' }}>
                  Initialize Scan <ArrowRight size={16} />
                </button>
              </div>
            )}
          </motion.form>
        ) : (
          <motion.form
            key="url"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }}
            transition={{ duration: 0.3 }}
            onSubmit={handleSubmit}
            style={{ display: 'flex', flexDirection: 'column', gap: 20, minHeight: 280, justifyContent: 'center' }}
          >
            <label style={{ fontSize: '0.85rem', fontWeight: 500, color: 'var(--text)', marginBottom: 4 }}>Target Media URL</label>
            <div style={{ position: 'relative' }}>
              <LinkIcon size={18} style={{ position: 'absolute', left: 16, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
              <input
                type="url"
                placeholder="Paste URL (e.g. YouTube, X / Twitter...)"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                required
                style={{
                  width: '100%', padding: '16px 16px 16px 48px',
                  background: 'var(--surface-raised)', border: '1px solid var(--border)', borderRadius: 8,
                  fontSize: '0.95rem', color: 'var(--text)', outline: 'none',
                  fontFamily: "'Inter', sans-serif",
                  transition: 'border-color 0.25s ease',
                }}
                onFocus={(e) => e.target.style.borderColor = 'var(--accent)'}
                onBlur={(e) => e.target.style.borderColor = 'var(--border)'}
              />
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontStyle: 'italic', opacity: 0.8 }}>
              Ensure the URL points directly to media or a supported public platform.
            </p>
            <button
              type="submit"
              disabled={!url.trim()}
              className="editorial-btn primary"
              style={{ width: '100%', justifyContent: 'center', padding: '14px 24px', marginTop: 8, fontSize: '0.85rem', opacity: url.trim() ? 1 : 0.5, cursor: url.trim() ? 'pointer' : 'not-allowed' }}
            >
              Analyze Remote Stream <ArrowRight size={16} />
            </button>
          </motion.form>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
