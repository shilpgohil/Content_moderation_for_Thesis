import { motion } from 'framer-motion';
import { Scale, ThumbsUp, ThumbsDown, MessageSquare } from 'lucide-react';

export default function BiasGauge({ bias }) {
    if (!bias) {
        return null;
    }

    const { is_biased, bias_score, sentiment, counter_arguments_present, flags } = bias;

    return (
        <div className={`p-6 rounded-xl border ${is_biased
                ? 'border-yellow-500/30 bg-yellow-500/5'
                : 'border-green-500/30 bg-green-500/5'
            }`}>
            <div className="flex items-center gap-3 mb-6">
                <div className={`p-2 rounded-lg ${is_biased ? 'bg-yellow-500/20 text-yellow-400' : 'bg-green-500/20 text-green-400'
                    }`}>
                    <Scale className="w-5 h-5" />
                </div>
                <div>
                    <h3 className="font-medium">Bias Analysis</h3>
                    <p className={`text-sm ${is_biased ? 'text-yellow-400' : 'text-green-400'}`}>
                        {is_biased ? 'Potential Bias Detected' : 'Balanced Analysis'}
                    </p>
                </div>
            </div>

            <div className="grid sm:grid-cols-2 gap-6">
                {}
                <div>
                    <p className="text-sm text-gray-400 mb-3">Sentiment Distribution</p>
                    <div className="flex items-center gap-2 mb-2">
                        <ThumbsUp className="w-4 h-4 text-green-400" />
                        <div className="flex-1 h-3 bg-dark-border rounded-full overflow-hidden flex">
                            <motion.div
                                className="h-full bg-green-500"
                                initial={{ width: 0 }}
                                animate={{ width: `${sentiment.positive}%` }}
                                transition={{ duration: 0.5 }}
                            />
                            <motion.div
                                className="h-full bg-red-500"
                                initial={{ width: 0 }}
                                animate={{ width: `${sentiment.negative}%` }}
                                transition={{ duration: 0.5, delay: 0.2 }}
                            />
                        </div>
                        <ThumbsDown className="w-4 h-4 text-red-400" />
                    </div>
                    <div className="flex justify-between text-xs text-gray-500">
                        <span>{sentiment.positive.toFixed(0)}% Positive</span>
                        <span>{sentiment.negative.toFixed(0)}% Negative</span>
                    </div>
                </div>

                {}
                <div className="space-y-3">
                    <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-400">Bias Score</span>
                        <span className={`font-medium ${bias_score < 0.3 ? 'text-green-400' :
                                bias_score < 0.6 ? 'text-yellow-400' : 'text-red-400'
                            }`}>
                            {(bias_score * 100).toFixed(0)}%
                        </span>
                    </div>
                    <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-400">Counter-Arguments</span>
                        <span className={counter_arguments_present ? 'text-green-400' : 'text-red-400'}>
                            {counter_arguments_present ? 'Present' : 'Missing'}
                        </span>
                    </div>
                </div>
            </div>

            {}
            {flags && flags.length > 0 && (
                <div className="mt-6 pt-4 border-t border-dark-border">
                    <p className="text-sm text-gray-400 mb-2">Flags:</p>
                    <div className="flex flex-wrap gap-2">
                        {flags.map((flag, i) => (
                            <span
                                key={i}
                                className="px-3 py-1 rounded-full bg-yellow-500/10 text-yellow-400 text-xs"
                            >
                                {flag}
                            </span>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
