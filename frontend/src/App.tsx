import { useState } from 'react'
import Transcriber from './components/Transcriber'

type ModelType = 'whisper' | 'wav2vec2'

interface Result {
  text: string
  model_type: string
  metrics?: { wer: number; cer: number }
  error_breakdown?: {
    substitutions: number
    deletions: number
    insertions: number
    hits: number
  }
}

function App() {
  const [model, setModel] = useState<ModelType>('whisper')
  const [result, setResult] = useState<Result | null>(null)
  const [loading, setLoading] = useState(false)
  const [reference, setReference] = useState('')

  return (
    <div className="app">
      <header className="header">
        <h1>Cebuano ASR</h1>
        <p>Fine-tuned Whisper & Wav2Vec2 for Cebuano Speech Recognition</p>
      </header>

      <div className="model-selector">
        <button
          className={model === 'whisper' ? 'active' : ''}
          onClick={() => setModel('whisper')}
        >
          Whisper-small
        </button>
        <button
          className={model === 'wav2vec2' ? 'active' : ''}
          onClick={() => setModel('wav2vec2')}
        >
          XLS-R 300M
        </button>
      </div>

      <Transcriber
        model={model}
        onResult={setResult}
        loading={loading}
        setLoading={setLoading}
      />

      {result && (
        <div className="result">
          <h3>Transcription</h3>
          <div className="transcription-box">{result.text}</div>

          <div className="reference-input">
            <label>Reference text (optional — for WER/CER):</label>
            <textarea
              value={reference}
              onChange={(e) => setReference(e.target.value)}
              placeholder="Enter ground truth transcription..."
              rows={3}
            />
          </div>

          {result.metrics && (
            <div className="metrics">
              <div className="metric-card">
                <span className="metric-value">{result.metrics.wer}%</span>
                <span className="metric-label">WER</span>
              </div>
              <div className="metric-card">
                <span className="metric-value">{result.metrics.cer}%</span>
                <span className="metric-label">CER</span>
              </div>
              {result.error_breakdown && (
                <>
                  <div className="metric-card">
                    <span className="metric-value">{result.error_breakdown.substitutions}</span>
                    <span className="metric-label">Substitutions</span>
                  </div>
                  <div className="metric-card">
                    <span className="metric-value">{result.error_breakdown.deletions}</span>
                    <span className="metric-label">Deletions</span>
                  </div>
                  <div className="metric-card">
                    <span className="metric-value">{result.error_breakdown.insertions}</span>
                    <span className="metric-label">Insertions</span>
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default App
