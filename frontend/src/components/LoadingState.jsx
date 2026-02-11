import { motion } from 'framer-motion';
import { Atom, Loader2 } from 'lucide-react';

const steps = [
    'ML Preprocessing',
    'Sentence Classification',
    'Quantitative Scoring',
    'LLM Deep Analysis',
    'Building Analysis',
    'Generating Report'
];

export default function LoadingState({ message = "Analyzing Your Thesis" }) {
    return (
        <div className="min-h-screen flex flex-col items-center justify-center px-4">
            <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.5 }}
                className="text-center"
            >
                {}
                <div className="relative w-32 h-32 mx-auto mb-8">
                    {}
                    <motion.div
                        className="absolute inset-0"
                        animate={{ rotate: 360 }}
                        transition={{ duration: 8, repeat: Infinity, ease: 'linear' }}
                    >
                        <div className="absolute inset-0 rounded-full border-2 border-dashed border-primary-500/30" />
                        {}
                        <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-primary-400 glow-primary" />
                    </motion.div>

                    {}
                    <motion.div
                        className="absolute inset-2"
                        animate={{ rotate: -360 }}
                        transition={{ duration: 6, repeat: Infinity, ease: 'linear' }}
                    >
                        <div className="absolute inset-0 rounded-full border-2 border-dashed border-cyan-500/30" />
                        {}
                        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2 w-3 h-3 rounded-full bg-cyan-400" />
                    </motion.div>

                    {}
                    <motion.div
                        className="absolute inset-4"
                        animate={{ rotate: 360 }}
                        transition={{ duration: 4, repeat: Infinity, ease: 'linear' }}
                    >
                        <div className="absolute inset-0 rounded-full border-2 border-dashed border-purple-500/30" />
                        {}
                        <div className="absolute right-0 top-1/2 translate-x-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-purple-400" />
                    </motion.div>

                    {}
                    <motion.div
                        className="absolute inset-0 flex items-center justify-center"
                        animate={{ scale: [1, 1.1, 1] }}
                        transition={{ duration: 2, repeat: Infinity }}
                    >
                        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary-400 to-cyan-500 flex items-center justify-center glow-primary">
                            <Atom className="w-6 h-6 text-white" />
                        </div>
                    </motion.div>
                </div>

                <h2 className="text-2xl font-bold mb-4">{message}</h2>
                <p className="text-gray-400 mb-8">
                    Deep learning models processing your content...
                </p>

                {}
                <div className="max-w-sm mx-auto">
                    {steps.map((step, i) => (
                        <motion.div
                            key={step}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: i * 0.3 }}
                            className="flex items-center gap-3 mb-3"
                        >
                            <motion.div
                                animate={{
                                    backgroundColor: ['#334155', '#0ea5e9', '#22c55e'],
                                }}
                                transition={{
                                    duration: 1.5,
                                    delay: i * 2,
                                    times: [0, 0.5, 1]
                                }}
                                className="w-3 h-3 rounded-full"
                            />
                            <span className="text-sm text-gray-400">{step}</span>
                        </motion.div>
                    ))}
                </div>

                <motion.div
                    className="mt-8 flex items-center gap-2 text-gray-500"
                    animate={{ opacity: [0.5, 1, 0.5] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                >
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span className="text-sm">This may take 15-30 seconds</span>
                </motion.div>
            </motion.div>
        </div>
    );
}
