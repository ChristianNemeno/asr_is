import { useState, useRef, useEffect, useCallback } from 'react'
import { Swiper, SwiperSlide } from 'swiper/react'
import type { Swiper as SwiperType } from 'swiper'
import { Pagination, EffectFade, Keyboard } from 'swiper/modules'
import 'swiper/css'
import 'swiper/css/pagination'
import 'swiper/css/effect-fade'
import './Presentation.css'
import SlideCard, { SubSection } from './SlideCard'
import Hero from './Hero'
import ModelOverview from './ModelOverview'
import ModelComparison from './ModelComparison'
import DatasetBrowser from './DatasetBrowser'
import DataExploration from './DataExploration'
import Hyperparams from './Hyperparams'
import LiveComparison from './LiveComparison'
import TrainingCurves from './TrainingCurves'
import ErrorAnalysis from './ErrorAnalysis'

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

function PerformanceSubSection({ models, section = 'overall' }: { models: Models | null; section?: 'overall' | 'detail' }) {
  if (!models) return null
  if (section === 'overall') {
    return (
      <div className="stat-cards">
        <div className="stat-card glow-border">
          <span className="stat-value">{models.finetuned.test_wer.toFixed(1)}%</span>
          <span className="stat-label">Overall WER</span>
        </div>
        <div className="stat-card glow-border">
          <span className="stat-value">{models.finetuned.test_cer.toFixed(1)}%</span>
          <span className="stat-label">Overall CER</span>
        </div>
        <div className="stat-card glow-border">
          <span className="stat-value">{models.finetuned.train_steps.toLocaleString()}</span>
          <span className="stat-label">Training Steps</span>
        </div>
      </div>
    )
  }
  return (
    <div className="stat-cards">
      {Object.entries(models.finetuned.per_language).map(([lang, v]) => (
        <div className="stat-card glow-border" key={lang}>
          <span className="stat-value">{(v.mean_wer * 100).toFixed(1)}%</span>
          <span className="stat-label">{lang.charAt(0).toUpperCase() + lang.slice(1)} WER</span>
        </div>
      ))}
      <div className="stat-card glow-border">
        <span className="stat-value">~70h</span>
        <span className="stat-label">Training Data</span>
      </div>
      <div className="stat-card glow-border">
        <span className="stat-value">244M</span>
        <span className="stat-label">Parameters</span>
      </div>
    </div>
  )
}

function Presentation({
  models, hyperparams, metrics, curves, samples, comparisons,
}: {
  models: Models | null
  hyperparams: HyperparamsData | null
  metrics: Metrics | null
  curves: CurvePoint[]
  samples: SampleItem[]
  comparisons: ComparisonRow[]
}) {
  const swiperRef = useRef<SwiperType | null>(null)
  const [activeSlideIndex, setActiveSlideIndex] = useState(0)
  const [subIndices, setSubIndices] = useState<number[]>([])

  const slides: { title: string; sections: SubSection[] }[] = [
    {
      title: 'Whisper-small — Filipino & Cebuano ASR',
      sections: [
        { id: 'hero', title: '', content: <Hero models={models} /> },
      ],
    },
    {
      title: 'Model Architecture',
      sections: [
        { id: 'desc', title: 'Architecture & Rationale', content: <ModelOverview section="description" /> },
        { id: 'specs', title: 'Technical Specifications', content: <ModelOverview section="specs" /> },
      ],
    },
    {
      title: 'Performance at a Glance',
      sections: [
        { id: 'overall', title: 'Overall Metrics', content: <PerformanceSubSection models={models} section="overall" /> },
        { id: 'detail', title: 'Per-Language & Training Stats', content: <PerformanceSubSection models={models} section="detail" /> },
      ],
    },
    {
      title: 'Model Comparison',
      sections: [
        { id: 'chart', title: 'Baseline (Zero-shot) vs Fine-tuned', content: <ModelComparison /> },
      ],
    },
    {
      title: 'Dataset Samples',
      sections: [
        { id: 'samples', title: 'Audio Samples', content: <DatasetBrowser samples={samples} section="samples" /> },
        { id: 'composition', title: 'Full Training Dataset Composition', content: <DatasetBrowser samples={samples} section="composition" /> },
        { id: 'splits', title: 'Dataset Splits by Source', content: <DatasetBrowser samples={samples} section="splits" /> },
      ],
    },
    {
      title: 'Data Exploration',
      sections: [
        { id: 'duration', title: 'Audio Duration Distribution', content: <DataExploration section="duration" /> },
        { id: 'wordcount', title: 'Word Count Distribution', content: <DataExploration section="wordcount" /> },
        { id: 'language', title: 'Language Distribution', content: <DataExploration section="language" /> },
        { id: 'waveform', title: 'Sample Waveforms & Mel Spectrograms', content: <DataExploration section="waveform" /> },
      ],
    },
    {
      title: 'Hyperparameters',
      sections: [
        { id: 'params', title: 'Training Configuration', content: <Hyperparams hyperparams={hyperparams} /> },
      ],
    },
    {
      title: 'Training Curves',
      sections: [
        { id: 'loss', title: 'Train & Eval Loss', content: <TrainingCurves curves={curves} section="loss" /> },
        { id: 'wercer', title: 'WER & CER', content: <TrainingCurves curves={curves} section="wercer" /> },
        { id: 'lr', title: 'Learning Rate Schedule', content: <TrainingCurves curves={curves} section="lr" /> },
        { id: 'gradnorm', title: 'Gradient Norm', content: <TrainingCurves curves={curves} section="gradnorm" /> },
      ],
    },
    {
      title: 'Live Comparison: Baseline vs Fine-tuned',
      sections: [
        { id: 'upload', title: 'Upload Audio', content: <LiveComparison section="upload" /> },
        { id: 'results', title: 'Transcription Results', content: <LiveComparison section="results" /> },
      ],
    },
    {
      title: 'Error Analysis',
      sections: [
        { id: 'stats', title: 'Error Statistics', content: <ErrorAnalysis metrics={metrics} comparisons={[]} section="stats" /> },
        { id: 'charts', title: 'WER by Language & Error Breakdown', content: <ErrorAnalysis metrics={metrics} comparisons={[]} section="charts" /> },
        { id: 'table', title: 'Sample Comparison: Baseline vs Fine-tuned', content: <ErrorAnalysis metrics={null} comparisons={comparisons} section="table" /> },
      ],
    },
  ]

  const initSubIndices = useCallback(() => Array(slides.length).fill(0), [])
  if (subIndices.length === 0 || subIndices.length !== slides.length) {
    setSubIndices(initSubIndices())
  }

  const activeSubIndex = subIndices[activeSlideIndex] ?? 0

  const setSubIndex = (slideIdx: number, subIdx: number) => {
    setSubIndices(prev => {
      const next = [...prev]
      next[slideIdx] = subIdx
      return next
    })
  }

  const goNext = () => {
    const sections = slides[activeSlideIndex].sections
    if (activeSubIndex < sections.length - 1) {
      setSubIndex(activeSlideIndex, activeSubIndex + 1)
    } else {
      swiperRef.current?.slideNext()
    }
  }

  const goPrev = () => {
    if (activeSubIndex > 0) {
      setSubIndex(activeSlideIndex, activeSubIndex - 1)
    } else {
      swiperRef.current?.slidePrev()
    }
  }

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'ArrowDown') {
        e.preventDefault()
        goNext()
      } else if (e.key === 'ArrowUp') {
        e.preventDefault()
        goPrev()
      }
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [activeSlideIndex, activeSubIndex])

  return (
    <Swiper
      modules={[Pagination, EffectFade, Keyboard]}
      effect="fade"
      fadeEffect={{ crossFade: true }}
      pagination={{ clickable: true }}
      keyboard={{ enabled: true }}
      onSlideChange={(swiper) => {
        setActiveSlideIndex(swiper.activeIndex)
      }}
      onSwiper={(swiper) => { swiperRef.current = swiper }}
      className="presentation-swiper"
    >
      {slides.map((slide, slideIdx) => (
        <SwiperSlide key={slideIdx}>
          <SlideCard
            sections={slide.sections}
            activeIndex={subIndices[slideIdx] ?? 0}
            onDotClick={(i) => setSubIndex(slideIdx, i)}
            slideTitle={slide.title}
          />
        </SwiperSlide>
      ))}
    </Swiper>
  )
}

export default Presentation
