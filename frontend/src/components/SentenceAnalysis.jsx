import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';

const typeColors = {
    FACT: { bg: 'bg-blue-500/20', text: 'text-blue-400', border: 'border-blue-500/30' },
    OPINION: { bg: 'bg-purple-500/20', text: 'text-purple-400', border: 'border-purple-500/30' },
    ASSUMPTION: { bg: 'bg-yellow-500/20', text: 'text-yellow-400', border: 'border-yellow-500/30' },
    PROJECTION: { bg: 'bg-cyan-500/20', text: 'text-cyan-400', border: 'border-cyan-500/30' },
    CONTEXT: { bg: 'bg-gray-500/20', text: 'text-gray-400', border: 'border-gray-500/30' },
};

const supportIcons = {
    SUPPORTED: { icon: CheckCircle, color: 'text-green-400' },
    PARTIAL: { icon: AlertTriangle, color: 'text-yellow-400' },
    UNSUPPORTED: { icon: XCircle, color: 'text-red-400' },
};

export default function SentenceAnalysis({ sentences, quickStats }) {
    const [filter, setFilter] = useState('ALL');
    const [expanded, setExpanded] = useState(new Set());

    const filteredSentences = filter === 'ALL'
        ? sentences
        : sentences.filter(s => s.type === filter);

    const toggleExpanded = (index) => {
        const newExpanded = new Set(expanded);
        if (newExpanded.has(index)) {
            newExpanded.delete(index);
        } else {
            newExpanded.add(index);
        }
        setExpanded(newExpanded);
    };

    return (
        <div>
            {}
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-4 mb-8">
                <StatBadge label="Total" value={quickStats.total_sentences} />
                <StatBadge label="Facts" value={quickStats.facts} color="blue" />
                <StatBadge label="Assumptions" value={quickStats.assumptions} color="yellow" />
                <StatBadge label="Opinions" value={quickStats.opinions} color="purple" />
                <StatBadge label="Projections" value={quickStats.projections} color="cyan" />
            </div>

            {}
            <div className="flex flex-wrap gap-2 mb-6">
                {['ALL', 'FACT', 'OPINION', 'ASSUMPTION', 'PROJECTION', 'CONTEXT'].map((type) => (
                    <button
                        key={type}
                        onClick={() => setFilter(type)}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${filter === type
                                ? 'bg-primary-500 text-white'
                                : 'bg-dark-card border border-dark-border text-gray-400 hover:border-primary-500/30'
                            }`}
                    >
                        {type}
                    </button>
                ))}
            </div>

            {}
            <div className="space-y-3">
                {filteredSentences.map((sentence, i) => {
                    const colors = typeColors[sentence.type] || typeColors.CONTEXT;
                    const support = supportIcons[sentence.support] || supportIcons.PARTIAL;
                    const SupportIcon = support.icon;
                    const isExpanded = expanded.has(sentence.index);

                    return (
                        <motion.div
                            key={sentence.index}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: i * 0.02 }}
                            className={`rounded-xl border ${colors.border} overflow-hidden`}
                        >
                            <button
                                onClick={() => toggleExpanded(sentence.index)}
                                className="w-full p-4 flex items-start gap-4 text-left hover:bg-dark-card/50 transition-colors"
                            >
                                {}
                                <span className="flex-shrink-0 w-8 h-8 rounded-lg bg-dark-border flex items-center justify-center text-sm font-medium">
                                    {sentence.index}
                                </span>

                                {}
                                <div className="flex-1 min-w-0">
                                    <p className="text-gray-200 line-clamp-2">{sentence.text}</p>
                                </div>

                                {}
                                <div className="flex items-center gap-2 flex-shrink-0">
                                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${colors.bg} ${colors.text}`}>
                                        {sentence.type}
                                    </span>
                                    <SupportIcon className={`w-5 h-5 ${support.color}`} />
                                    <ChevronDown
                                        className={`w-5 h-5 text-gray-500 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                                    />
                                </div>
                            </button>

                            {}
                            <AnimatePresence>
                                {isExpanded && (
                                    <motion.div
                                        initial={{ height: 0, opacity: 0 }}
                                        animate={{ height: 'auto', opacity: 1 }}
                                        exit={{ height: 0, opacity: 0 }}
                                        className="px-4 pb-4 border-t border-dark-border"
                                    >
                                        <div className="pt-4 grid sm:grid-cols-2 gap-4 text-sm">
                                            <div>
                                                <span className="text-gray-500">Support Level:</span>
                                                <span className={`ml-2 ${support.color}`}>{sentence.support}</span>
                                            </div>
                                            <div>
                                                <span className="text-gray-500">Role:</span>
                                                <span className="ml-2 text-gray-300">{sentence.role}</span>
                                            </div>
                                            <div>
                                                <span className="text-gray-500">Confidence:</span>
                                                <span className="ml-2 text-gray-300">{(sentence.confidence * 100).toFixed(0)}%</span>
                                            </div>
                                            {sentence.issues && sentence.issues.length > 0 && (
                                                <div className="sm:col-span-2">
                                                    <span className="text-gray-500">Issues:</span>
                                                    <ul className="mt-2 space-y-1">
                                                        {sentence.issues.map((issue, idx) => (
                                                            <li key={idx} className="flex items-start gap-2 text-orange-400">
                                                                <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                                                                <span>{issue}</span>
                                                            </li>
                                                        ))}
                                                    </ul>
                                                </div>
                                            )}
                                        </div>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </motion.div>
                    );
                })}
            </div>
        </div>
    );
}

function StatBadge({ label, value, color = 'gray' }) {
    const colors = {
        gray: 'bg-gray-500/20 text-gray-400',
        blue: 'bg-blue-500/20 text-blue-400',
        yellow: 'bg-yellow-500/20 text-yellow-400',
        purple: 'bg-purple-500/20 text-purple-400',
        cyan: 'bg-cyan-500/20 text-cyan-400',
    };

    return (
        <div className={`p-4 rounded-xl ${colors[color]} text-center`}>
            <div className="text-2xl font-bold">{value}</div>
            <div className="text-sm opacity-80">{label}</div>
        </div>
    );
}
