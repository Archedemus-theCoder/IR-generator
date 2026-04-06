import { useState, useEffect } from 'react'
import Sidebar from './components/Sidebar'
import Editor from './components/Editor'
import Preview from './components/Preview'
import './App.css'

const API = 'http://localhost:8000/api'

export default function App() {
  const [doc, setDoc] = useState(null)
  const [slideNames, setSlideNames] = useState({})
  const [selectedSlide, setSelectedSlide] = useState(null)
  const [saving, setSaving] = useState(false)
  const [exporting, setExporting] = useState(false)

  // Load data on mount
  useEffect(() => {
    fetch(`${API}/slides`)
      .then(r => r.json())
      .then(res => {
        setDoc(res.data)
        setSlideNames(res.slide_names)
        // Select first slide
        const first = res.data.slide_config
          .sort((a, b) => a.order - b.order)
          .find(s => s.enabled)
        if (first) setSelectedSlide(first.id)
      })
      .catch(e => console.error('Load failed:', e))
  }, [])

  // Save current document
  const handleSave = async () => {
    setSaving(true)
    try {
      await fetch(`${API}/slides`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(doc),
      })
    } catch (e) {
      console.error('Save failed:', e)
    }
    setSaving(false)
  }

  // Auto-save on doc change (debounced)
  useEffect(() => {
    if (!doc) return
    const timer = setTimeout(handleSave, 2000)
    return () => clearTimeout(timer)
  }, [doc])

  // Export PPT
  const handleExport = async () => {
    setExporting(true)
    try {
      // Save first
      await fetch(`${API}/slides`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(doc),
      })
      // Then export
      const res = await fetch(`${API}/export`, { method: 'POST' })
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'Rovothome_IR.pptx'
      a.click()
      URL.revokeObjectURL(url)
    } catch (e) {
      console.error('Export failed:', e)
    }
    setExporting(false)
  }

  // Update slide data
  const updateSlide = (slideId, field, value) => {
    setDoc(prev => {
      const updated = { ...prev }
      if (field.includes('.')) {
        // Nested field (e.g., "contact.name")
        const parts = field.split('.')
        const slideData = { ...updated[slideId] }
        let obj = slideData
        for (let i = 0; i < parts.length - 1; i++) {
          obj[parts[i]] = { ...obj[parts[i]] }
          obj = obj[parts[i]]
        }
        obj[parts[parts.length - 1]] = value
        updated[slideId] = slideData
      } else {
        updated[slideId] = { ...updated[slideId], [field]: value }
      }
      return updated
    })
  }

  // Update slide config (order/enabled)
  const updateConfig = (newConfig) => {
    setDoc(prev => ({ ...prev, slide_config: newConfig }))
  }

  // Toggle slide visibility
  const toggleSlide = (slideId) => {
    setDoc(prev => {
      const newConfig = prev.slide_config.map(sc =>
        sc.id === slideId ? { ...sc, enabled: !sc.enabled } : sc
      )
      return { ...prev, slide_config: newConfig }
    })
  }

  // Move slide up/down
  const moveSlide = (slideId, direction) => {
    setDoc(prev => {
      const config = [...prev.slide_config].sort((a, b) => a.order - b.order)
      const idx = config.findIndex(s => s.id === slideId)
      if (idx < 0) return prev
      const swapIdx = direction === 'up' ? idx - 1 : idx + 1
      if (swapIdx < 0 || swapIdx >= config.length) return prev
      // Swap orders
      const tmpOrder = config[idx].order
      config[idx] = { ...config[idx], order: config[swapIdx].order }
      config[swapIdx] = { ...config[swapIdx], order: tmpOrder }
      return { ...prev, slide_config: config }
    })
  }

  if (!doc) return <div className="loading">Loading...</div>

  return (
    <div className="app">
      <Sidebar
        config={doc.slide_config}
        slideNames={slideNames}
        selectedSlide={selectedSlide}
        onSelect={setSelectedSlide}
        onToggle={toggleSlide}
        onMove={moveSlide}
        onExport={handleExport}
        exporting={exporting}
        saving={saving}
      />
      <main className="main">
        {selectedSlide && doc[selectedSlide] && (
          <>
            <Editor
              slideId={selectedSlide}
              slideName={slideNames[selectedSlide] || selectedSlide}
              data={doc[selectedSlide]}
              onUpdate={(field, value) => updateSlide(selectedSlide, field, value)}
            />
            <Preview slideId={selectedSlide} doc={doc} />
          </>
        )}
      </main>
    </div>
  )
}
