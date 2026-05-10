import { useState, useRef } from 'react'
import { motion, AnimatePresence } from 'motion/react'

interface Result {
  baseline: { text: string; wer?: number; cer?: number; error_breakdown?: { substitutions: number; deletions: number; insertions: number; hits: number } }
  finetuned: { text: string; wer?: number; cer?: number; error_breakdown?: { substitutions: number; deletions: number; insertions: number; hits: number } }
}

function LiveComparison({ section = 'all' }: { section?: 'all' | 'upload' | 'results' }) {
  const showAll = section === 'all'
  const [result, setResult] = useState<Result | null>(null)
  const [loading, setLoading] = useState(false)
  const [reference, setReference] = useState('')
  const fileRef = useRef<HTMLInputElement>(null)

  const handleTranscribe = async () => {
    const file = fileRef.current?.files?.[0]
    if (!file) return

    setLoading(true)
    const formData = new FormData()
    formData.append('file', file)
    if (reference.trim()) formData.append('reference', reference)

    try {
      const res = await fetch('/api/transcribe', { method: 'POST', body: formData })
      const data = await res.json()
      setResult(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="section">
      <h2 className="section-title">Live Comparison: Baseline vs Fine-tuned</h2>

      {(showAll || section === 'upload') && (
      <>
        <div className="upload-area">
        <input type="file" ref={fileRef} accept="audio/*" disabled={loading} />
        <button onClick={handleTranscribe} disabled={loading || !fileRef.current?.files?.length}>
          {loading ? 'Transcribing...' : 'Transcribe Both'}
        </button>
      </div>
      <textarea
        className="ref-input"
        placeholder="Reference text (optional — for WER/CER comparison)"
          rows={2}
          value={reference}
          onChange={e => setReference(e.target.value)}
        />
      </>
      )}
      {(showAll || section === 'results') && (

      <AnimatePresence>
        {result && (
          <motion.div
            className="comparison-grid"
            initial={{ opacity: 0, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4, ease: 'easeOut' }}
          >
            <motion.div
              className="comparison-col"
              initial={{ x: -30, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.1, duration: 0.4 }}
            >
              <h3>Baseline <span className="model-tag">Zero-shot</span></h3>
              <div className="transcription-box">{result.baseline.text}</div>
              {result.baseline.wer != null && (
                <div className="metrics-row">
                  <div className="metric-card small">
                    <span className="metric-value small-val">{result.baseline.wer}%</span>
                    <span className="metric-label">WER</span>
                  </div>
                  <div className="metric-card small">
                    <span className="metric-value small-val">{result.baseline.cer}%</span>
                    <span className="metric-label">CER</span>
                  </div>
                </div>
              )}
              {result.baseline.error_breakdown && (
                <div className="breakdown-row">
                  <span>S: {result.baseline.error_breakdown.substitutions}</span>
                  <span>D: {result.baseline.error_breakdown.deletions}</span>
                  <span>I: {result.baseline.error_breakdown.insertions}</span>
                  <span>H: {result.baseline.error_breakdown.hits}</span>
                </div>
              )}
            </motion.div>
            <motion.div
              className="comparison-col"
              initial={{ x: 30, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.2, duration: 0.4 }}
            >
              <h3>Fine-tuned <span className="model-tag fine-tuned">Our Model</span></h3>
              <div className="transcription-box">{result.finetuned.text}</div>
              {result.finetuned.wer != null && (
                <div className="metrics-row">
                  <div className="metric-card small">
                    <span className="metric-value small-val">{result.finetuned.wer}%</span>
                    <span className="metric-label">WER</span>
                  </div>
                  <div className="metric-card small">
                    <span className="metric-value small-val">{result.finetuned.cer}%</span>
                    <span className="metric-label">CER</span>
                  </div>
                </div>
              )}
              {result.finetuned.error_breakdown && (
                <div className="breakdown-row">
                  <span>S: {result.finetuned.error_breakdown.substitutions}</span>
                  <span>D: {result.finetuned.error_breakdown.deletions}</span>
                  <span>I: {result.finetuned.error_breakdown.insertions}</span>
                  <span>H: {result.finetuned.error_breakdown.hits}</span>
                </div>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
      )}
    </section>
  )
}

export default LiveComparison
