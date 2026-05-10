interface SubSectionNavProps {
  total: number
  active: number
  onDotClick: (index: number) => void
}

function SubSectionNav({ total, active, onDotClick }: SubSectionNavProps) {
  if (total <= 1) return null

  return (
    <div className="sub-section-nav">
      {Array.from({ length: total }).map((_, i) => (
        <button
          key={i}
          className={`sub-section-dot ${i === active ? 'active' : ''}`}
          onClick={() => onDotClick(i)}
          aria-label={`Section ${i + 1} of ${total}`}
        />
      ))}
    </div>
  )
}

export default SubSectionNav
