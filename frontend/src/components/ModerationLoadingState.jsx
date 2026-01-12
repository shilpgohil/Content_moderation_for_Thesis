import { motion } from 'framer-motion';
import { Shield, CheckCircle, Loader2 } from 'lucide-react';

/**
 * ModerationLoadingState - Shows while content moderation is running.
 * Distinct visual design from thesis analysis loading to avoid confusion.
 */

const moderationSteps = [
    { id: 1, label: 'Scanning for spam patterns' },
    { id: 2, label: 'Checking content toxicity' },
    { id: 3, label: 'Validating finance relevance' },
    { id: 4, label: 'Verifying content safety' },
];

export default function ModerationLoadingState() {
    return (
        <div className="min-h-screen flex flex-col items-center justify-center px-4">
            <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.5 }}
                className="text-center"
            >
                {/* Security Shield Animation */}
                <div className="relative w-32 h-32 mx-auto mb-8">
                    {/* Outer pulsing ring */}
                    <motion.div
                        className="absolute inset-0"
                        animate={{ scale: [1, 1.2, 1], opacity: [0.3, 0.1, 0.3] }}
                        transition={{ duration: 2, repeat: Infinity }}
                    >
                        <div className="absolute inset-0 rounded-full bg-green-500/20" />
                    </motion.div>

                    {/* Scanning ring */}
                    <motion.div
                        className="absolute inset-2"
                        animate={{ rotate: 360 }}
                        transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
                    >
                        <div className="absolute inset-0 rounded-full border-2 border-dashed border-green-500/40" />
                        <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 w-2 h-2 rounded-full bg-green-400" />
                    </motion.div>

                    {/* Inner shield */}
                    <motion.div
                        className="absolute inset-0 flex items-center justify-center"
                        animate={{ scale: [1, 1.05, 1] }}
                        transition={{ duration: 1.5, repeat: Infinity }}
                    >
                        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center shadow-lg shadow-green-500/30">
                            <Shield className="w-8 h-8 text-white" />
                        </div>
                    </motion.div>
                </div>

                <h2 className="text-2xl font-bold mb-4 text-white">Checking Content Safety</h2>
                <p className="text-gray-400 mb-8">
                    Verifying your content meets our guidelines...
                </p>

                {/* Moderation Steps */}
                <div className="max-w-sm mx-auto">
                    {moderationSteps.map((step, i) => (
                        <motion.div
                            key={step.id}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: i * 0.4 }}
                            className="flex items-center gap-3 mb-3"
                        >
                            <motion.div
                                animate={{
                                    backgroundColor: ['#334155', '#22c55e', '#22c55e'],
                                }}
                                transition={{
                                    duration: 1,
                                    delay: i * 0.5,
                                    times: [0, 0.8, 1]
                                }}
                                className="w-3 h-3 rounded-full flex items-center justify-center"
                            >
                                <motion.div
                                    initial={{ scale: 0 }}
                                    animate={{ scale: 1 }}
                                    transition={{ delay: i * 0.5 + 0.8 }}
                                >
                                    <CheckCircle className="w-3 h-3 text-white" />
                                </motion.div>
                            </motion.div>
                            <span className="text-sm text-gray-400">{step.label}</span>
                        </motion.div>
                    ))}
                </div>

                <motion.div
                    className="mt-8 flex items-center gap-2 text-gray-500"
                    animate={{ opacity: [0.5, 1, 0.5] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                >
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span className="text-sm">This usually takes 2-5 seconds</span>
                </motion.div>
            </motion.div>
        </div>
    );
}
