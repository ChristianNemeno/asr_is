import { useState, useEffect } from 'react'
import Hero from './components/Hero'
import ModelOverview from './components/ModelOverview'
import ModelComparison from './components/ModelComparison'
import DatasetBrowser from './components/DatasetBrowser'
import DataExploration from './components/DataExploration'
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

interface CurvePoint {
  step: number
  loss: number | null
  eval_loss: number | null
  eval_wer: number | null
  eval_cer: number | null
  learning_rate: number | null
  grad_norm: number | null
}

interface SampleItem {
  filename: string; language: string; language_code: string
  label: string; duration_sec: number; url: string
}

interface ComparisonRow {
  rank: number; language: string; reference: string
  baseline_prediction: string; baseline_wer: number; baseline_cer: number
  finetuned_prediction: string; finetuned_wer: number; finetuned_cer: number
}

function App() {
  const [models, setModels] = useState<Models | null>(null)
  const [hyperparams, setHyperparams] = useState<HyperparamsData | null>(null)
  const [metrics, setMetrics] = useState<Metrics | null>(null)
  const [curves, setCurves] = useState<CurvePoint[]>([])
  const [samples, setSamples] = useState<SampleItem[]>([])
  const [comparisons, setComparisons] = useState<ComparisonRow[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchAll() {
      try {
        const [mRes, hRes, metRes, cRes, sRes, cmpRes] = await Promise.all([
          fetch('/api/training/models').then(r => r.json()),
          fetch('/api/training/hyperparams').then(r => r.json()),
          fetch('/api/training/metrics').then(r => r.json()),
          fetch('/api/training/curves').then(r => r.json()),
          fetch('/api/samples').then(r => r.json()),
          fetch('/api/training/sample-comparison').then(r => r.json()),
        ])
        setModels(mRes)
        setHyperparams(hRes)
        setMetrics(metRes)
        setCurves(Array.isArray(cRes) ? cRes : [])
        setSamples(Array.isArray(sRes) ? sRes : [])
        setComparisons(Array.isArray(cmpRes) ? cmpRes : [])
      } catch (e) {
        console.error(e)
      } finally {
        setLoading(false)
      }
    }
    fetchAll()
  }, [])

  if (loading) {
    return (
      <div className="app loading-state">
        <div className="skeleton-hero" />
        <div className="skeleton-block" />
        <div className="skeleton-block small" />
        <div className="skeleton-block" />
        <div className="skeleton-block small" />
      </div>
    )
  }

  return (
    <div className="app">
      <Hero models={models} />
      <ModelOverview />
      <ModelComparison />
      <DatasetBrowser samples={samples} />
      <DataExploration />
      <Hyperparams hyperparams={hyperparams} />
      <LiveComparison />
      <TrainingCurves curves={curves} />
      <ErrorAnalysis metrics={metrics} comparisons={comparisons} />
    </div>
  )
}

export default App
