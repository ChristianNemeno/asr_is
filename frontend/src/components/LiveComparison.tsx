import { useState, useRef } from 'react'

interface Result {
  baseline: { text: string; wer?: number; cer?: number; error_breakdown?: { substitutions: number; deletions: number; insertions: number; hits: number } }
  finetuned: { text: string; wer?: number; cer?: number; error_breakdown?: { substitutions: number; deletions: number; insertions: number; hits: number } }
}

function LiveComparison() {
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

      {result && (
        <div className="comparison-grid">
          <div className="comparison-col">
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
          </div>
          <div className="comparison-col">
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
          </div>
        </div>
      )}
    </section>
  )
}

export default LiveComparison
