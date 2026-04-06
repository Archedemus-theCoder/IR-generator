/**
 * Recursive field renderer — handles:
 * - string/number → input or textarea
 * - object → nested FieldGroup
 * - array of objects → list of editable cards
 * - array of strings → comma-separated input
 */

export default function FieldGroup({ data, path, onUpdate, getLabel, isMultiline }) {
  if (!data || typeof data !== 'object') return null

  const entries = Object.entries(data)

  return (
    <div className="field-group">
      {entries.map(([key, value]) => {
        const fieldPath = path ? `${path}.${key}` : key

        // Skip internal fields
        if (key.startsWith('_')) return null

        // String field
        if (typeof value === 'string') {
          if (isMultiline(key, value)) {
            return (
              <div className="field" key={fieldPath}>
                <label>{getLabel(key)}</label>
                <textarea
                  value={value}
                  onChange={e => onUpdate(fieldPath, e.target.value)}
                  rows={Math.max(3, value.split('\n').length + 1)}
                />
              </div>
            )
          }
          return (
            <div className="field" key={fieldPath}>
              <label>{getLabel(key)}</label>
              <input
                type="text"
                value={value}
                onChange={e => onUpdate(fieldPath, e.target.value)}
              />
            </div>
          )
        }

        // Number field
        if (typeof value === 'number') {
          return (
            <div className="field" key={fieldPath}>
              <label>{getLabel(key)}</label>
              <input
                type="number"
                value={value}
                onChange={e => onUpdate(fieldPath, Number(e.target.value))}
              />
            </div>
          )
        }

        // Array of objects → editable card list
        if (Array.isArray(value) && value.length > 0 && typeof value[0] === 'object') {
          return (
            <div className="field-array" key={fieldPath}>
              <label className="array-label">{getLabel(key)}</label>
              {value.map((item, idx) => (
                <div className="array-card" key={idx}>
                  <div className="array-card-header">
                    <span>#{idx + 1}</span>
                    <button
                      className="remove-btn"
                      onClick={() => {
                        const newArr = value.filter((_, i) => i !== idx)
                        onUpdate(fieldPath, newArr)
                      }}
                    >×</button>
                  </div>
                  {Object.entries(item).map(([subKey, subVal]) => {
                    if (typeof subVal === 'string') {
                      return (
                        <div className="field" key={`${fieldPath}.${idx}.${subKey}`}>
                          <label>{getLabel(subKey)}</label>
                          {isMultiline(subKey, subVal) ? (
                            <textarea
                              value={subVal}
                              rows={Math.max(2, subVal.split('\n').length + 1)}
                              onChange={e => {
                                const newArr = [...value]
                                newArr[idx] = { ...newArr[idx], [subKey]: e.target.value }
                                onUpdate(fieldPath, newArr)
                              }}
                            />
                          ) : (
                            <input
                              type="text"
                              value={subVal}
                              onChange={e => {
                                const newArr = [...value]
                                newArr[idx] = { ...newArr[idx], [subKey]: e.target.value }
                                onUpdate(fieldPath, newArr)
                              }}
                            />
                          )}
                        </div>
                      )
                    }
                    // dict[str, str] (like PLRow.values)
                    if (typeof subVal === 'object' && !Array.isArray(subVal)) {
                      return (
                        <div className="field-inline-group" key={`${fieldPath}.${idx}.${subKey}`}>
                          <label>{getLabel(subKey)}</label>
                          <div className="inline-fields">
                            {Object.entries(subVal).map(([k, v]) => (
                              <div className="inline-field" key={k}>
                                <span className="inline-label">{k}</span>
                                <input
                                  type="text"
                                  value={v}
                                  onChange={e => {
                                    const newArr = [...value]
                                    newArr[idx] = {
                                      ...newArr[idx],
                                      [subKey]: { ...newArr[idx][subKey], [k]: e.target.value }
                                    }
                                    onUpdate(fieldPath, newArr)
                                  }}
                                />
                              </div>
                            ))}
                          </div>
                        </div>
                      )
                    }
                    return null
                  })}
                </div>
              ))}
              <button
                className="add-btn"
                onClick={() => {
                  // Clone first item as template with empty values
                  const template = {}
                  if (value.length > 0) {
                    for (const [k, v] of Object.entries(value[0])) {
                      if (typeof v === 'string') template[k] = ''
                      else if (typeof v === 'object' && !Array.isArray(v)) {
                        template[k] = Object.fromEntries(Object.keys(v).map(kk => [kk, '']))
                      } else template[k] = v
                    }
                  }
                  onUpdate(fieldPath, [...value, template])
                }}
              >+ 항목 추가</button>
            </div>
          )
        }

        // Array of strings
        if (Array.isArray(value) && (value.length === 0 || typeof value[0] === 'string')) {
          return (
            <div className="field" key={fieldPath}>
              <label>{getLabel(key)}</label>
              <input
                type="text"
                value={value.join(', ')}
                onChange={e => onUpdate(fieldPath, e.target.value.split(',').map(s => s.trim()).filter(Boolean))}
              />
              <span className="field-hint">쉼표로 구분</span>
            </div>
          )
        }

        // Nested object (not array)
        if (typeof value === 'object' && !Array.isArray(value)) {
          return (
            <div className="field-nested" key={fieldPath}>
              <label className="nested-label">{getLabel(key)}</label>
              <div className="nested-content">
                <FieldGroup
                  data={value}
                  path={fieldPath}
                  onUpdate={onUpdate}
                  getLabel={getLabel}
                  isMultiline={isMultiline}
                />
              </div>
            </div>
          )
        }

        return null
      })}
    </div>
  )
}
