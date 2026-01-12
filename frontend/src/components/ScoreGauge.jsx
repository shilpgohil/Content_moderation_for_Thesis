import { motion } from 'framer-motion';

function getGradeColor(grade) {
    const colors = {
        'A+': '#22c55e', 'A': '#22c55e',
        'B+': '#84cc16', 'B': '#84cc16',
        'C+': '#eab308', 'C': '#eab308',
        'D+': '#f97316', 'D': '#f97316',
        'F': '#ef4444'
    };
    return colors[grade] || '#64748b';
}

function getScoreColor(score) {
    if (score >= 80) return '#22c55e';
    if (score >= 60) return '#84cc16';
    if (score >= 40) return '#eab308';
    if (score >= 20) return '#f97316';
    return '#ef4444';
}

export default function ScoreGauge({ score, grade }) {
    const radius = 70;
    const circumference = 2 * Math.PI * radius;
    const percentage = score / 100;
    const strokeDashoffset = circumference * (1 - percentage);
    const color = getScoreColor(score);

    return (
        <div className="flex flex-col items-center">
            {/* Gauge container */}
            <div className="relative w-[180px] h-[180px]">
                <svg width="180" height="180" className="transform -rotate-90">
                    {/* Background circle */}
                    <circle
                        cx="90"
                        cy="90"
                        r={radius}
                        strokeWidth="12"
                        stroke="#334155"
                        fill="none"
                    />

                    {/* Animated progress circle */}
                    <motion.circle
                        cx="90"
                        cy="90"
                        r={radius}
                        strokeWidth="12"
                        stroke={color}
                        fill="none"
                        strokeLinecap="round"
                        initial={{ strokeDashoffset: circumference }}
                        animate={{ strokeDashoffset }}
                        transition={{ duration: 1.5, ease: 'easeOut' }}
                        style={{
                            strokeDasharray: circumference,
                        }}
                    />
                </svg>

                {/* Center content - positioned inside the circle */}
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <motion.span
                        className="text-4xl font-bold leading-none"
                        initial={{ opacity: 0, scale: 0.5 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 0.5 }}
                        style={{ color }}
                    >
                        {score.toFixed(1)}
                    </motion.span>
                    <span className="text-sm text-gray-400 mt-1">out of 100</span>
                </div>
            </div>

            {/* Grade badge - separated below the gauge */}
            <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8 }}
                className="mt-6 px-6 py-2 rounded-full border-2"
                style={{
                    borderColor: getGradeColor(grade),
                    color: getGradeColor(grade),
                    backgroundColor: `${getGradeColor(grade)}10`
                }}
            >
                <span className="font-bold text-xl">Grade: {grade}</span>
            </motion.div>
        </div>
    );
}
