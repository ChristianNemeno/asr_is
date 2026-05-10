import { AnimatePresence, motion } from 'motion/react'
import SubSectionNav from './SubSectionNav'

export interface SubSection {
  id: string
  title: string
  content: React.ReactNode
}

interface SlideCardProps {
  sections: SubSection[]
  activeIndex: number
  onDotClick: (index: number) => void
  slideTitle: string
}

function SlideCard({ sections, activeIndex, onDotClick, slideTitle }: SlideCardProps) {
  const section = sections[activeIndex]
  if (!section) return null

  return (
    <div className="slide-card glow-border">
      <div className="slide-card-header">
        <h2 className="section-title">{slideTitle}</h2>
        {sections.length > 1 && (
          <span className="sub-section-counter">
            {activeIndex + 1} / {sections.length}
          </span>
        )}
      </div>
      <div className="slide-card-body">
        <div className="slide-card-inner">
          <AnimatePresence mode="wait">
            <motion.div
              key={section.id}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: 0.25, ease: 'easeOut' }}
            >
              <div className="sub-section-title">{section.title}</div>
              {section.content}
            </motion.div>
          </AnimatePresence>
        </div>
        <SubSectionNav
          total={sections.length}
          active={activeIndex}
          onDotClick={onDotClick}
        />
      </div>
    </div>
  )
}

export default SlideCard
