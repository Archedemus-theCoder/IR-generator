import { useState, useRef } from 'react'
import FieldGroup from './FieldGroup'

const API = 'http://localhost:8000/api'

const FIELD_LABELS = {
  company_name: '회사명', tagline: '태그라인', kpis: 'KPI 카드',
  section_label: '섹션 라벨', headline: '헤드라인', body: '본문',
  data_cards: '데이터 카드', contact: '연락처',
  name: '이름', phone: '전화번호', email: '이메일',
  label: '라벨', value: '값', sub: '설명',
  left_title: '왼쪽 제목', left_desc: '왼쪽 설명',
  right_title: '오른쪽 제목', right_desc: '오른쪽 설명',
  points: '포인트', tam: 'TAM', sam: 'SAM', som: 'SOM',
  growth_note: '성장 전망', model_types: '비즈니스 모델 유형',
  items: '항목', moats: '기술 장벽', phases: 'Phase 목록',
  phase: 'Phase', period: '기간', description: '설명',
  years: '연도', rows: 'P&L 항목', values: '값',
  amount: '금액', valuation: '밸류에이션',
  use_of_funds: '자금 사용처', members: '팀원',
  title: '직함', bio: '소개',
}

function getLabel(key) {
  return FIELD_LABELS[key] || key
}

function isMultiline(key, value) {
  return typeof value === 'string' && (
    value.includes('\n') ||
    ['headline', 'body', 'description', 'bio', 'left_desc', 'right_desc'].includes(key)
  )
}

export default function Editor({ slideId, slideName, data, onUpdate, onReload }) {
  const [importing, setImporting] = useState(false)
  const [importMsg, setImportMsg] = useState(null)
  const fileRef = useRef(null)

  const handleFileImport = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    setImporting(true)
    setImportMsg(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch(`${API}/import/financial`, {
        method: 'POST',
        body: formData,
      })
      const result = await res.json()
      if (result.ok) {
        setImportMsg({ type: 'success', text: result.message })
        // Reload data from server
        if (onReload) onReload()
      } else {
        setImportMsg({ type: 'error', text: result.error })
      }
    } catch (err) {
      setImportMsg({ type: 'error', text: `업로드 실패: ${err.message}` })
    }
    setImporting(false)
    // Reset file input
    if (fileRef.current) fileRef.current.value = ''
  }

  return (
    <div className="editor">
      <div className="editor-header">
        <h2>{slideName}</h2>
        <span className="slide-id">{slideId}</span>
      </div>

      {/* Financial import for P&L slide */}
      {slideId === 'pl' && (
        <div className="import-section">
          <div className="import-header">
            <span className="import-icon">📊</span>
            <div>
              <strong>재무 프로젝션 파일 가져오기</strong>
              <p className="import-hint">Excel(.xlsx) 또는 CSV 파일을 업로드하세요. 첫 행=연도, 첫 열=항목명</p>
            </div>
          </div>
          <div className="import-actions">
            <input
              ref={fileRef}
              type="file"
              accept=".xlsx,.xls,.csv"
              onChange={handleFileImport}
              style={{ display: 'none' }}
            />
            <button
              className="import-btn"
              onClick={() => fileRef.current?.click()}
              disabled={importing}
            >
              {importing ? '가져오는 중...' : '📂 파일 선택'}
            </button>
            <button
              className="import-template-btn"
              onClick={() => {
                // Download template
                const csv = '항목,2026,2027,2028,2029\n매출,15억,89억,280억,520억\n영업이익,-18억,-5억,42억,105억\n영업이익률,-120%,-6%,15%,20%'
                const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8' })
                const url = URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url; a.download = 'pl_template.csv'; a.click()
                URL.revokeObjectURL(url)
              }}
            >
              📥 템플릿 다운로드
            </button>
          </div>
          {importMsg && (
            <div className={`import-msg ${importMsg.type}`}>
              {importMsg.text}
            </div>
          )}
        </div>
      )}

      <div className="editor-body">
        <FieldGroup
          data={data}
          path=""
          onUpdate={onUpdate}
          getLabel={getLabel}
          isMultiline={isMultiline}
        />
      </div>
    </div>
  )
}
