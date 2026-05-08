import { useState, useEffect } from 'react'
import Hero from './components/Hero'
import ModelOverview from './components/ModelOverview'
import DatasetBrowser from './components/DatasetBrowser'
import Hyperparams from './components/Hyperparams'
import LiveComparison from './components/LiveComparison'
import TrainingCurves from './components/TrainingCurves'
import ErrorAnalysis from './components/ErrorAnalysis'

interface Models {
  baseline: { id: string; parameters: number; architecture: string; task: string }
  finetuned: { id: string; test_wer: number; test_cer: number; train_steps: number; dataset: string; per_language: Record<string, { mean_wer: number; n: number }> }
}

interface HyperparamsData {
  base_model: string; parameters: number; per_device_train_batch_size: number
  gradient_accumulation_steps: number; effective_batch_size: number
  learning_rate: number; warmup_steps: number; max_steps: number
  gradient_checkpointing: boolean; mixed_precision: string
  generation_max_length: number; seed: number
}

interface Metrics {
  test_wer: number; test_cer: number; train_steps: number
  per_language: Record<string, { mean_wer: number; n: number }>
  error_breakdown: { substitutions: number; deletions: number; insertions: number; hits: number }
  n_samples: number
}

interface SampleItem {
  filename: string; language: string; language_code: string
  label: string; duration_sec: number; url: string
}

interface Transcription {
  rank: number; wer: number; cer: number; language: string
  reference: string; prediction: string
}

function App() {
  const [models, setModels] = useState<Models | null>(null)
  const [hyperparams, setHyperparams] = useState<HyperparamsData | null>(null)
  const [metrics, setMetrics] = useState<Metrics | null>(null)
  const [samples, setSamples] = useState<SampleItem[]>([])
  const [transcriptions, setTranscriptions] = useState<Transcription[]>([])

  useEffect(() => {
    async function fetchAll() {
      const [mRes, hRes, metRes, _cRes, sRes, tRes] = await Promise.all([
        fetch('/api/training/models').then(r => r.json()),
        fetch('/api/training/hyperparams').then(r => r.json()),
        fetch('/api/training/metrics').then(r => r.json()),
        fetch('/api/training/curves').then(r => r.json()),
        fetch('/api/samples').then(r => r.json()),
        fetch('/api/training/samples').then(r => r.json()),
      ])
      setModels(mRes)
      setHyperparams(hRes)
      setMetrics(metRes)
      setSamples(Array.isArray(sRes) ? sRes : [])
      setTranscriptions(Array.isArray(tRes) ? tRes : [])
    }
    fetchAll()
  }, [])

  return (
    <div className="app">
      <Hero models={models} />
      <ModelOverview />
      <DatasetBrowser samples={samples} />
      <Hyperparams hyperparams={hyperparams} />
      <LiveComparison />
      <TrainingCurves />
      <ErrorAnalysis metrics={metrics} transcriptions={transcriptions} />
    </div>
  )
}

export default App
