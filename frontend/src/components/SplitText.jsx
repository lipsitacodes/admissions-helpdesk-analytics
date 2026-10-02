import React, { useRef, useMemo } from 'react';
import { motion } from 'motion/react';

export default function SplitText({
  text = '',
  className = '',
  delay = 30,
  duration = 0.6,
  splitType = 'chars',
  from = { opacity: 0, y: 25 },
  to = { opacity: 1, y: 0 },
  textAlign = 'center',
  tag = 'span',
  style = {}
}) {
  const words = useMemo(() => {
    if (!text) return [];
    if (splitType === 'words') {
      return text.split(' ').map((w) => w + ' ');
    }
    return text.split(' ');
  }, [text, splitType]);

  const Tag = tag === 'p' ? motion.p : motion.span;

  let globalCharIndex = 0;

  return (
    <Tag
      className={`inline-block ${className}`}
      style={{
        textAlign,
        ...style
      }}
      initial="hidden"
      animate="visible"
      transition={{ staggerChildren: delay / 1000 }}
    >
      {splitType === 'words'
        ? words.map((word, wi) => (
            <motion.span
              key={wi}
              className="inline-block"
              variants={{
                hidden: from,
                visible: {
                  ...to,
                  transition: { duration, ease: [0.25, 0.1, 0.25, 1] }
                }
              }}
            >
              {word}&nbsp;
            </motion.span>
          ))
        : words.map((word, wi) => (
            <span key={wi} className="inline-block whitespace-nowrap">
              {word.split('').map((char, ci) => {
                const charIdx = globalCharIndex++;
                return (
                  <motion.span
                    key={ci}
                    className="inline-block"
                    variants={{
                      hidden: from,
                      visible: {
                        ...to,
                        transition: {
                          duration,
                          delay: (charIdx * delay) / 1000,
                          ease: [0.25, 0.1, 0.25, 1]
                        }
                      }
                    }}
                  >
                    {char}
                  </motion.span>
                );
              })}
              {wi < words.length - 1 && <span className="inline-block">&nbsp;</span>}
            </span>
          ))}
    </Tag>
  );
}
