import { useRef } from 'react'

interface Props {
  model: string
  onResult: (result: any) => void
  loading: boolean
  setLoading: (v: boolean) => void
}

function Transcriber({ model, onResult, loading, setLoading }: Props) {
  const fileRef = useRef<HTMLInputElement>(null)
  const refRef = useRef<HTMLTextAreaElement>(null)

  const handleUpload = async () => {
    const file = fileRef.current?.files?.[0]
    if (!file) return

    setLoading(true)
    const formData = new FormData()
    formData.append('file', file)

    const reference = refRef.current?.value || ''
    if (reference) formData.append('reference', reference)

    try {
      const res = await fetch(`/api/transcribe?model=${model}`, {
        method: 'POST',
        body: formData,
      })
      const data = await res.json()
      onResult(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="transcriber">
      <div className="upload-area">
        <input
          type="file"
          ref={fileRef}
          accept="audio/*"
          onChange={handleUpload}
          disabled={loading}
        />
        <button onClick={handleUpload} disabled={loading || !fileRef.current?.files?.length}>
          {loading ? 'Transcribing...' : 'Transcribe'}
        </button>
      </div>
      <div className="ref-area">
        <textarea
          ref={refRef}
          placeholder="Enter reference text (optional) for WER/CER calculation..."
          rows={2}
        />
      </div>
    </div>
  )
}

export default Transcriber
