import { motion } from 'framer-motion';

interface SpoilageGaugeProps {
  score: number; // 0-100
  size?: number;
}

const SpoilageGauge = ({ score, size = 180 }: SpoilageGaugeProps) => {
  const radius = (size - 20) / 2;
  const cx = size / 2;
  const cy = size / 2;
  const startAngle = 135;
  const endAngle = 405;
  const totalAngle = endAngle - startAngle;
  const scoreAngle = startAngle + (totalAngle * Math.min(score, 100)) / 100;

  const polarToCartesian = (angle: number) => {
    const rad = ((angle - 90) * Math.PI) / 180;
    return { x: cx + radius * Math.cos(rad), y: cy + radius * Math.sin(rad) };
  };

  const arcPath = (start: number, end: number) => {
    const s = polarToCartesian(start);
    const e = polarToCartesian(end);
    const largeArc = end - start > 180 ? 1 : 0;
    return `M ${s.x} ${s.y} A ${radius} ${radius} 0 ${largeArc} 1 ${e.x} ${e.y}`;
  };

  const needleEnd = polarToCartesian(scoreAngle);
  const color = score < 35 ? 'hsl(153 43% 30%)' : score < 65 ? 'hsl(29 89% 67%)' : 'hsl(0 84% 60%)';
  const label = score < 35 ? 'Safe' : score < 65 ? 'Caution' : 'Danger';

  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size * 0.75} viewBox={`0 0 ${size} ${size * 0.85}`}>
        {/* Background arc */}
        <path d={arcPath(startAngle, endAngle)} fill="none" stroke="hsl(var(--muted))" strokeWidth="12" strokeLinecap="round" />
        {/* Green zone */}
        <path d={arcPath(135, 225)} fill="none" stroke="hsl(153 43% 30% / 0.3)" strokeWidth="12" strokeLinecap="round" />
        {/* Yellow zone */}
        <path d={arcPath(225, 315)} fill="none" stroke="hsl(29 89% 67% / 0.3)" strokeWidth="12" strokeLinecap="round" />
        {/* Red zone */}
        <path d={arcPath(315, 405)} fill="none" stroke="hsl(0 84% 60% / 0.3)" strokeWidth="12" strokeLinecap="round" />
        {/* Score arc */}
        <motion.path
          d={arcPath(startAngle, scoreAngle)}
          fill="none"
          stroke={color}
          strokeWidth="12"
          strokeLinecap="round"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 1.2, ease: 'easeOut' }}
        />
        {/* Needle */}
        <motion.line
          x1={cx}
          y1={cy}
          x2={needleEnd.x}
          y2={needleEnd.y}
          stroke={color}
          strokeWidth="3"
          strokeLinecap="round"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
        />
        <circle cx={cx} cy={cy} r="5" fill={color} />
        {/* Score text */}
        <text x={cx} y={cy + 25} textAnchor="middle" className="text-2xl font-bold" fill={color}>
          {score}
        </text>
      </svg>
      <span className="text-lg font-bold mt-1" style={{ color }}>{label}</span>
    </div>
  );
};

export default SpoilageGauge;
