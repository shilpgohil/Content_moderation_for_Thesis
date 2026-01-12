import { motion } from 'framer-motion';
import { FileText, Atom, BarChart3, Sparkles } from 'lucide-react';

export default function Hero() {
    return (
        <header className="relative py-16 px-4 overflow-hidden">
            {/* Animated background elements */}
            <div className="absolute inset-0 overflow-hidden">
                <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary-500/10 rounded-full blur-3xl" />
                <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl" />
            </div>

            <div className="relative max-w-4xl mx-auto text-center">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                >
                    {/* Badge */}
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-500/10 border border-primary-500/20 mb-8">
                        <Atom className="w-4 h-4 text-primary-400" />
                        <span className="text-sm text-primary-300">AI Powered Thesis Analyzer</span>
                    </div>

                    {/* Main title */}
                    <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-white via-primary-200 to-primary-400 bg-clip-text text-transparent">
                        Thesis Strength Analyzer
                    </h1>

                    <p className="text-xl text-gray-400 mb-12 max-w-2xl mx-auto">
                        Validate your investment thesis with AI powered analysis
                    </p>

                    {/* Feature cards */}
                    <div className="grid md:grid-cols-3 gap-6 mt-12">
                        <FeatureCard
                            icon={<FileText className="w-6 h-6" />}
                            title="Evidence Quality"
                            description="Verify claims with sources"
                        />
                        <FeatureCard
                            icon={<Sparkles className="w-6 h-6" />}
                            title="Logical Coherence"
                            description="Check argument flow"
                        />
                        <FeatureCard
                            icon={<BarChart3 className="w-6 h-6" />}
                            title="Risk Awareness"
                            description="Assess downside coverage"
                        />
                    </div>
                </motion.div>
            </div>
        </header>
    );
}

function FeatureCard({ icon, title, description }) {
    return (
        <motion.div
            className="p-6 rounded-2xl gradient-card border border-dark-border"
            whileHover={{ scale: 1.02, borderColor: 'rgba(14, 165, 233, 0.3)' }}
            transition={{ duration: 0.2 }}
        >
            <div className="w-12 h-12 rounded-xl bg-primary-500/20 flex items-center justify-center text-primary-400 mb-4">
                {icon}
            </div>
            <h3 className="font-semibold text-lg mb-2">{title}</h3>
            <p className="text-gray-400 text-sm">{description}</p>
        </motion.div>
    );
}
