import FieldGroup from './FieldGroup'

/**
 * Slide editor — auto-generates form fields based on slide data structure.
 * Knows how to render different field types:
 * - string → text input or textarea (if multiline)
 * - array of objects → repeatable card list
 * - nested object → sub-group
 */

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

export default function Editor({ slideId, slideName, data, onUpdate }) {
  return (
    <div className="editor">
      <div className="editor-header">
        <h2>{slideName}</h2>
        <span className="slide-id">{slideId}</span>
      </div>

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
