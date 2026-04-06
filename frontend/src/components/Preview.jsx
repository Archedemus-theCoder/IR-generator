import { useState, useEffect } from 'react'

const API = 'http://localhost:8000/api'

/**
 * Live slide preview — fetches rendered preview from backend
 * and shows financial chart for P&L slide.
 */
export default function Preview({ slideId, doc }) {
  const [previewImg, setPreviewImg] = useState(null)
  const [chartImg, setChartImg] = useState(null)
  const [loading, setLoading] = useState(false)

  // Fetch preview when slide changes or data changes
  useEffect(() => {
    if (!slideId) return
    setLoading(true)

    // Save first, then get preview
    const timer = setTimeout(async () => {
      try {
        await fetch(`${API}/slides`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(doc),
        })
        const res = await fetch(`${API}/preview/${slideId}`)
        const data = await res.json()
        if (data.image) {
          setPreviewImg(`data:image/png;base64,${data.image}`)
        }
      } catch (e) {
        console.error('Preview failed:', e)
      }
      setLoading(false)
    }, 800) // Small debounce

    return () => clearTimeout(timer)
  }, [slideId, doc])

  // Fetch P&L chart for financial slides
  useEffect(() => {
    if (slideId !== 'pl' && slideId !== 'roadmap') {
      setChartImg(null)
      return
    }
    const fetchChart = async () => {
      try {
        await fetch(`${API}/slides`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(doc),
        })
        const res = await fetch(`${API}/chart/pl`, { method: 'POST' })
        const data = await res.json()
        if (data.image) {
          setChartImg(`data:image/png;base64,${data.image}`)
        }
      } catch (e) {
        console.error('Chart failed:', e)
      }
    }
    const timer = setTimeout(fetchChart, 1000)
    return () => clearTimeout(timer)
  }, [slideId, doc?.pl])

  return (
    <div className="preview-section">
      <div className="preview-header">
        <h3>미리보기</h3>
        {loading && <span className="preview-loading">업데이트 중...</span>}
      </div>

      {previewImg && (
        <div className="preview-image-container">
          <img src={previewImg} alt="Slide preview" className="preview-image" />
        </div>
      )}

      {chartImg && (
        <div className="chart-preview">
          <h4>📊 자동 생성 차트 (PPT에 포함됨)</h4>
          <img src={chartImg} alt="P&L Chart" className="chart-image" />
        </div>
      )}

      {/* Financial sync info */}
      {slideId === 'pl' && doc?.pl && (
        <div className="financial-sync">
          <h4>💰 재무 데이터 동기화</h4>
          <p className="sync-note">
            이 P&L 데이터는 PPT 내보내기 시 차트로 자동 변환됩니다.
            숫자를 수정하면 차트가 즉시 업데이트됩니다.
          </p>
          <div className="sync-summary">
            {doc.pl.rows?.map((row, i) => (
              <div key={i} className="sync-row">
                <span className="sync-label">{row.label}</span>
                <div className="sync-values">
                  {doc.pl.years?.map(yr => (
                    <span key={yr} className={`sync-value ${row.values?.[yr]?.startsWith('-') ? 'negative' : ''}`}>
                      {yr}: {row.values?.[yr] || '-'}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
