import { motion } from 'framer-motion';
import { FileCheck, Brain, Eye, Shield, Target } from 'lucide-react';

const icons = {
    'Evidence Quality': FileCheck,
    'Logical Coherence': Brain,
    'Clarity & Specificity': Eye,
    'Risk Awareness': Shield,
    'Actionability': Target,
};

function getScoreColor(percentage) {
    if (percentage >= 80) return { bg: 'bg-green-500/20', text: 'text-green-400', bar: 'bg-green-500' };
    if (percentage >= 60) return { bg: 'bg-lime-500/20', text: 'text-lime-400', bar: 'bg-lime-500' };
    if (percentage >= 40) return { bg: 'bg-yellow-500/20', text: 'text-yellow-400', bar: 'bg-yellow-500' };
    if (percentage >= 20) return { bg: 'bg-orange-500/20', text: 'text-orange-400', bar: 'bg-orange-500' };
    return { bg: 'bg-red-500/20', text: 'text-red-400', bar: 'bg-red-500' };
}

export default function ComponentCards({ scores }) {
    const scoreEntries = Object.entries(scores || {});

    return (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {scoreEntries.map(([key, data], index) => {
                const Icon = icons[data.name] || FileCheck;
                const colors = getScoreColor(data.percentage);

                return (
                    <motion.div
                        key={key}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="p-5 rounded-xl gradient-card border border-dark-border hover:border-primary-500/30 transition-colors"
                    >
                        {}
                        <div className="flex items-start justify-between mb-4">
                            <div className={`w-10 h-10 rounded-lg ${colors.bg} flex items-center justify-center`}>
                                <Icon className={`w-5 h-5 ${colors.text}`} />
                            </div>
                            <span className={`text-2xl font-bold ${colors.text}`}>
                                {data.score}/{data.max}
                            </span>
                        </div>

                        {}
                        <h3 className="font-medium text-white mb-3">{data.name}</h3>

                        {}
                        <div className="h-2 bg-dark-border rounded-full overflow-hidden">
                            <motion.div
                                className={`h-full ${colors.bar} rounded-full`}
                                initial={{ width: 0 }}
                                animate={{ width: `${data.percentage}%` }}
                                transition={{ duration: 1, delay: 0.3 + index * 0.1 }}
                            />
                        </div>

                        {}
                        {data.breakdown && (
                            <div className="mt-4 space-y-1">
                                {Object.entries(data.breakdown).map(([bKey, bValue]) => (
                                    <div key={bKey} className="flex justify-between text-xs">
                                        <span className="text-gray-500 capitalize">
                                            {bKey.replace(/_/g, ' ')}
                                        </span>
                                        <span className="text-gray-400">{bValue}</span>
                                    </div>
                                ))}
                            </div>
                        )}
                    </motion.div>
                );
            })}
        </div>
    );
}
