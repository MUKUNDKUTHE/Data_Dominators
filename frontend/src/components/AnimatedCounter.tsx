import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

interface AnimatedCounterProps {
  value: number;
  prefix?: string;
  duration?: number;
  className?: string;
}

const AnimatedCounter = ({ value, prefix = '₹', duration = 1.5, className = '' }: AnimatedCounterProps) => {
  const [display, setDisplay] = useState(0);

  useEffect(() => {
    const start = 0;
    const increment = value / (duration * 60);
    let current = start;
    const timer = setInterval(() => {
      current += increment;
      if (current >= value) {
        setDisplay(value);
        clearInterval(timer);
      } else {
        setDisplay(Math.floor(current));
      }
    }, 1000 / 60);
    return () => clearInterval(timer);
  }, [value, duration]);

  return (
    <motion.span
      className={className}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      {prefix}{display.toLocaleString('en-IN')}
    </motion.span>
  );
};

export default AnimatedCounter;
