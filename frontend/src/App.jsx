import { useEffect, useMemo, useRef, useState } from 'react'
import './App.css'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

const emptyMetrics = {
  scene: {
    mode: '--',
    exposure: '--',
    brightness: 0,
    contrast: 0,
    glarePercent: 0,
    darkPercent: 0,
  },
  detections: {
    vehicles: 0,
    persons: 0,
    trafficLights: 0,
    objects: [],
  },
  warning: 'WAITING',
  processingMs: 0,
  detectorAvailable: false,
  images: {},
}

function metricLabel(value, suffix = '') {
  if (value === undefined || value === null || Number.isNaN(Number(value))) return '--'
  return Number(value).toFixed(value % 1 === 0 ? 0 : 1) + suffix
}

function App() {
  const [health, setHealth] = useState(null)
  const [samples, setSamples] = useState([])
  const [selectedSample, setSelectedSample] = useState('night')
  const [analysis, setAnalysis] = useState(emptyMetrics)
  const [busy, setBusy] = useState(false)
  const [processingVideo, setProcessingVideo] = useState(false)
  const [error, setError] = useState('')
  const [outputs, setOutputs] = useState({})
  const fileInput = useRef(null)

  const totals = useMemo(() => {
    const detections = analysis.detections || emptyMetrics.detections
    return [
      { label: 'Vehicles', value: detections.vehicles },
      { label: 'Persons', value: detections.persons },
      { label: 'Signals', value: detections.trafficLights },
      { label: 'Latency', value: metricLabel(analysis.processingMs, ' ms') },
    ]
  }, [analysis])

  async function loadStatus() {
    try {
      const [healthResponse, samplesResponse] = await Promise.all([
        fetch(API_BASE + '/api/health'),
        fetch(API_BASE + '/api/samples'),
      ])

      if (!healthResponse.ok || !samplesResponse.ok) {
        throw new Error('AVES API is not responding yet.')
      }

      const healthData = await healthResponse.json()
      const samplesData = await samplesResponse.json()

      setHealth(healthData)
      setSamples(samplesData.samples || [])
      setOutputs(samplesData.outputs || {})
      setError('')
    } catch (err) {
      setHealth(null)
      setError(err.message)
    }
  }

  async function analyzeSample(sample = selectedSample) {
    setBusy(true)
    setError('')
    try {
      const response = await fetch(API_BASE + '/api/analyze-sample', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sample }),
      })

      if (!response.ok)
        throw new Error((await response.json()).detail || 'Analysis failed.')

      setAnalysis(await response.json())
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  async function analyzeUpload(event) {
    const file = event.target.files?.[0]
    if (!file) return

    setBusy(true)
    setError('')

    try {
      const form = new FormData()
      form.append('file', file)

      const response = await fetch(API_BASE + '/api/analyze-upload', {
        method: 'POST',
        body: form,
      })

      if (!response.ok)
        throw new Error((await response.json()).detail || 'Upload analysis failed.')

      setAnalysis(await response.json())
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
      event.target.value = ''
    }
  }

  async function processVideo() {
    setProcessingVideo(true)
    setError('')

    try {
      const response = await fetch(API_BASE + '/api/process-video', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sample: selectedSample }),
      })

      if (!response.ok)
        throw new Error((await response.json()).detail || 'Video processing failed.')

      const data = await response.json()
      setOutputs(data.outputs || {})
    } catch (err) {
      setError(err.message)
    } finally {
      setProcessingVideo(false)
    }
  }

  useEffect(() => {
    loadStatus()
  }, [])

  useEffect(() => {
    if (health) {
      analyzeSample(selectedSample)
    }
  }, [health])

  const scene = analysis.scene || emptyMetrics.scene
  const detections = analysis.detections || emptyMetrics.detections
  const statusText = health ? 'API online' : 'API offline'

  return (
    <main className="dashboard-shell">
      <section className="hero-panel">
        <div className="hero-copy">
          <p className="eyebrow">Adaptive Vision Enhancement System</p>
          <h1>AVES Judge Dashboard</h1>
          <p className="hero-text">
            Real-time driving video enhancement with glare control, low-light recovery,
            object detection, and collision warnings in one demo-ready interface.
          </p>
        </div>

        <div className="status-strip">
          <span className={health ? 'status-dot online' : 'status-dot'}></span>
          <div>
            <strong>{statusText}</strong>
            <span>
              {health?.detectorAvailable
                ? 'YOLO detector loaded'
                : 'Enhancement engine ready'}
            </span>
          </div>
        </div>
      </section>

      {error && <div className="alert">{error}</div>}

      <section className="control-band">
        <div className="sample-switcher">
          {samples.map((sample) => (
            <button
              key={sample.id}
              className={selectedSample === sample.id ? 'active' : ''}
              disabled={!sample.available || busy || processingVideo}
              onClick={() => {
                setSelectedSample(sample.id)
                analyzeSample(sample.id)
              }}
            >
              <span>{sample.label}</span>
              <small>{sample.available ? 'Ready' : 'Missing'}</small>
            </button>
          ))}
        </div>

        <div className="actions">
          <button onClick={() => analyzeSample()} disabled={busy || !health}>
            {busy ? 'Analyzing...' : 'Analyze Frame'}
          </button>

          <button onClick={() => fileInput.current?.click()} disabled={busy || !health}>
            Upload Media
          </button>

          <button onClick={processVideo} disabled={processingVideo || !health}>
            {processingVideo ? 'Processing...' : 'Process Video'}
          </button>

          <input
            ref={fileInput}
            type="file"
            accept="image/*,video/*"
            onChange={analyzeUpload}
          />
        </div>
      </section>

      <section className="visual-grid">
        <div className="video-stage comparison-stage">
          <div className="stage-header">
            <span>Before / After</span>
            <strong>
              {scene.mode} | {scene.exposure}
            </strong>
          </div>

          {analysis.images?.comparison ? (
            <img
              src={analysis.images.comparison}
              alt="AVES comparison"
            />
          ) : (
            <div className="empty-preview">
              Start the API to preview AVES output
            </div>
          )}
        </div>

        <aside className="insight-panel">
          <div className={analysis.warning === 'CLEAR' ? 'warning clear' : 'warning'}>
            <span>Warning</span>
            <strong>{analysis.warning}</strong>
          </div>

          <div className="metric-list">
            <div><span>Brightness</span><strong>{metricLabel(scene.brightness)}</strong></div>
            <div><span>Contrast</span><strong>{metricLabel(scene.contrast)}</strong></div>
            <div><span>Glare</span><strong>{metricLabel(scene.glarePercent, '%')}</strong></div>
            <div><span>Dark Area</span><strong>{metricLabel(scene.darkPercent, '%')}</strong></div>
          </div>
        </aside>
      </section>

      <section className="stat-row">
        {totals.map((item) => (
          <div className="stat-card" key={item.label}>
            <span>{item.label}</span>
            <strong>{item.value}</strong>
          </div>
        ))}
      </section>

      <section className="lower-grid">
        <div className="objects-panel">
          <div className="section-title">
            <span>Detected Road Users</span>
            <strong>{detections.objects.length}</strong>
          </div>

          <div className="object-list">
            {detections.objects.length ? (
              detections.objects.slice(0, 5).map((object, index) => (
                <div className="object-row" key={object.label + '-' + index}>
                  <span>{object.label}</span>
                  <strong>{object.distance} m</strong>
                  <small>{Math.round(object.confidence * 100)}%</small>
                </div>
              ))
            ) : (
              <p>No high-confidence road users in this frame.</p>
            )}
          </div>
        </div>

        <div className="output-panel">
          <div className="section-title">
            <span>Generated Demo Videos</span>
            <strong>MP4</strong>
          </div>

          <div className="download-grid">
            {outputs.comparison && (
              <div style={{ marginBottom: '20px' }}>
                <h4>Comparison Output</h4>
                <video width="100%" controls>
                  <source
                    src={`${API_BASE}${outputs.comparison}?t=${Date.now()}`}
                    type="video/mp4"
                  />
                  Your browser does not support the video tag.
                </video>
              </div>
            )}

            {outputs.enhanced && (
              <div>
                <h4>Enhanced Output</h4>
                <video width="100%" controls>
                  <source
                    src={`${API_BASE}${outputs.enhanced}?t=${Date.now()}`}
                    type="video/mp4"
                  />
                  Your browser does not support the video tag.
                </video>
              </div>
            )}

            {!outputs.comparison && !outputs.enhanced && (
              <p>No processed videos available yet.</p>
            )}
          </div>
        </div>
      </section>
    </main>
  )
}

export default App