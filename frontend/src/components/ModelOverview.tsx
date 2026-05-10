function ModelOverview({ section = 'all' }: { section?: 'all' | 'description' | 'specs' }) {
  const showAll = section === 'all'
  return (
    <section className="section">
      <div className="overview-grid">
        {(showAll || section === 'description') && (
          <div className="overview-text">
            <p>
              <strong>Whisper</strong> is OpenAI's encoder-decoder Transformer trained on{' '}
              <strong>680,000 hours</strong> of multilingual supervised speech data. It handles
              transcription, translation, and language identification across 99+ languages.
            </p>

            <h4>Architecture</h4>
            <ul>
              <li><strong>Encoder:</strong> Converts raw audio → 80-channel log-Mel spectrogram → hidden state representations</li>
              <li><strong>Decoder:</strong> Autoregressively generates text tokens conditioned on encoder states + previous tokens</li>
              <li><strong>Loss:</strong> Cross-entropy (Seq2Seq), not CTC</li>
            </ul>

            <h4>Why whisper-small?</h4>
            <p>
              With <strong>244M parameters</strong> and ~950 MB, it offers the best accuracy/VRAM
              tradeoff for single-GPU fine-tuning. Larger variants (medium: 769M, large-v3: 1.55B)
              would require more VRAM and training time.
            </p>

            <h4>What fine-tuning changed</h4>
            <ul>
              <li>Removed forced language/task decoder tokens — Whisper auto-detects Tagalog/Cebuano</li>
              <li>Trained on Filipino Speech Corpus (Tagalog, ~50h) + FLEURS (Tagalog + Cebuano, ~20h)</li>
              <li>Seq2Seq training with WER as the early-stopping metric</li>
              <li>All checkpoints preserved (every 500 steps), best model selected by validation WER</li>
            </ul>
          </div>
        )}
        {(showAll || section === 'specs') && (
          <div className="overview-table-wrap">
            <table className="overview-table">
              <tbody>
                <tr><th>Pretrained model</th><td>openai/whisper-small</td></tr>
                <tr><th>Parameters</th><td>244M</td></tr>
                <tr><th>Disk size</th><td>~950 MB</td></tr>
                <tr><th>Architecture</th><td>Encoder-Decoder Transformer</td></tr>
                <tr><th>Pre-training data</th><td>680k hours, 99+ languages</td></tr>
                <tr><th>Loss function</th><td>Cross-entropy (Seq2Seq)</td></tr>
                <tr><th>Output</th><td>BPE tokens with language tags</td></tr>
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  )
}

export default ModelOverview
