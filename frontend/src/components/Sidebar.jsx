export default function Sidebar({
  config, slideNames, selectedSlide,
  onSelect, onToggle, onMove, onExport, exporting, saving,
}) {
  const sorted = [...config].sort((a, b) => a.order - b.order)

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="logo">
          <span className="logo-mark">R</span>
          <span className="logo-text">Rovothome IR</span>
        </div>
        <div className="save-status">
          {saving ? '저장 중...' : '자동 저장됨'}
        </div>
      </div>

      <div className="slide-list">
        {sorted.map((sc, idx) => (
          <div
            key={sc.id}
            className={`slide-item ${selectedSlide === sc.id ? 'active' : ''} ${!sc.enabled ? 'disabled' : ''}`}
            onClick={() => onSelect(sc.id)}
          >
            <div className="slide-item-left">
              <button
                className="toggle-btn"
                onClick={e => { e.stopPropagation(); onToggle(sc.id) }}
                title={sc.enabled ? '비활성화' : '활성화'}
              >
                {sc.enabled ? '✓' : '○'}
              </button>
              <span className="slide-name">
                {slideNames[sc.id] || sc.id}
              </span>
            </div>
            <div className="slide-item-right">
              <button
                className="move-btn"
                onClick={e => { e.stopPropagation(); onMove(sc.id, 'up') }}
                disabled={idx === 0}
              >↑</button>
              <button
                className="move-btn"
                onClick={e => { e.stopPropagation(); onMove(sc.id, 'down') }}
                disabled={idx === sorted.length - 1}
              >↓</button>
            </div>
          </div>
        ))}
      </div>

      <div className="sidebar-footer">
        <button
          className="export-btn"
          onClick={onExport}
          disabled={exporting}
        >
          {exporting ? '생성 중...' : '⬇ PPT 내보내기'}
        </button>
      </div>
    </aside>
  )
}
