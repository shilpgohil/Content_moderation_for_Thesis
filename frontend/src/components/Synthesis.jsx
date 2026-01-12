import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, AlertCircle, Lightbulb } from 'lucide-react';

export default function Synthesis({ synthesis }) {
    if (!synthesis) {
        return null;
    }

    return (
        <div className="grid md:grid-cols-2 gap-6">
            {/* Strengths */}
            <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="p-6 rounded-xl border border-green-500/30 bg-green-500/5"
            >
                <div className="flex items-center gap-3 mb-4">
                    <div className="p-2 rounded-lg bg-green-500/20 text-green-400">
                        <TrendingUp className="w-5 h-5" />
                    </div>
                    <h3 className="font-semibold text-green-400">Top Strengths</h3>
                </div>
                <ul className="space-y-3">
                    {synthesis.top_strengths?.map((item, i) => (
                        <li key={i} className="flex items-start gap-3 text-sm text-gray-300">
                            <span className="flex-shrink-0 w-6 h-6 rounded-full bg-green-500/20 text-green-400 flex items-center justify-center text-xs font-medium">
                                {i + 1}
                            </span>
                            <span>{item}</span>
                        </li>
                    ))}
                </ul>
            </motion.div>

            {/* Weaknesses */}
            <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="p-6 rounded-xl border border-red-500/30 bg-red-500/5"
            >
                <div className="flex items-center gap-3 mb-4">
                    <div className="p-2 rounded-lg bg-red-500/20 text-red-400">
                        <TrendingDown className="w-5 h-5" />
                    </div>
                    <h3 className="font-semibold text-red-400">Top Weaknesses</h3>
                </div>
                <ul className="space-y-3">
                    {synthesis.top_weaknesses?.map((item, i) => (
                        <li key={i} className="flex items-start gap-3 text-sm text-gray-300">
                            <span className="flex-shrink-0 w-6 h-6 rounded-full bg-red-500/20 text-red-400 flex items-center justify-center text-xs font-medium">
                                {i + 1}
                            </span>
                            <span>{item}</span>
                        </li>
                    ))}
                </ul>
            </motion.div>

            {/* Missing Elements */}
            {synthesis.missing_elements?.length > 0 && (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="p-6 rounded-xl border border-yellow-500/30 bg-yellow-500/5"
                >
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-2 rounded-lg bg-yellow-500/20 text-yellow-400">
                            <AlertCircle className="w-5 h-5" />
                        </div>
                        <h3 className="font-semibold text-yellow-400">Missing Elements</h3>
                    </div>
                    <ul className="space-y-2">
                        {synthesis.missing_elements.map((item, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                                <span className="text-yellow-400">•</span>
                                <span>{item}</span>
                            </li>
                        ))}
                    </ul>
                </motion.div>
            )}

            {/* Improvement Priorities */}
            {synthesis.improvement_priorities?.length > 0 && (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="p-6 rounded-xl border border-primary-500/30 bg-primary-500/5"
                >
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-2 rounded-lg bg-primary-500/20 text-primary-400">
                            <Lightbulb className="w-5 h-5" />
                        </div>
                        <h3 className="font-semibold text-primary-400">Improvement Priorities</h3>
                    </div>
                    <ul className="space-y-2">
                        {synthesis.improvement_priorities.map((item, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                                <span className="text-primary-400">{i + 1}.</span>
                                <span>{item}</span>
                            </li>
                        ))}
                    </ul>
                </motion.div>
            )}
        </div>
    );
}
