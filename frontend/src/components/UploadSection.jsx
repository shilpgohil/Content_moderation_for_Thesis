import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Upload, Wand2, AlertCircle } from 'lucide-react';

const SAMPLE_THESIS = `Investment Thesis: Long position in NVIDIA Corporation (NVDA) – Target Price $1500

Executive Summary:
We are initiating a long position in NVIDIA Corporation (NVDA) with a 12-month specific price target of $1,500. This represents roughly a 40% upside from current levels. The thesis is based on the company's dominant position in AI hardware, expanding software margins, and strong free cash flow generation.

Financial Evidence and Sourcing:
According to the FY2025 annual report, NVIDIA generated approximately $60.9 billion in revenue, representing a 126% increase year over year. Data from SEC filings confirms that data center revenue grew by about 409% to $47.5 billion. Based on statements in the most recent Q4 earnings call, management indicated that gross margins are expected to remain above 75% through 2026. This financial strength is supported by a reported net cash position of about $26 billion in the company's 10-K filing.

Logical Framework:
The core argument follows a clear causal chain. Global demand for accelerated computing is currently outpacing supply. Large cloud service providers (hyperscalers) have committed around $200 billion in capital expenditure for 2025, according to Bloomberg consensus estimates. NVIDIA is estimated to control close to 90% of the AI GPU market share according to IDC research. Therefore, NVIDIA is positioned to capture the majority of this spending, leading to earnings growth that could exceed current consensus expectations.

Market Position and Projections:
We project that FY2027 earnings per share will reach approximately $35.00, meaningfully above current street consensus of about $28.50. Using historical price-to-earnings multiples of around 40 times, this supports the $1,500 price target. The shift toward software-as-a-service through NVIDIA AI Enterprise is expected to support margins further. Unlike previous hardware cycles, this software component provides recurring revenue and may reduce earnings cyclicality.

Risk Assessment and Downside Scenarios:
A bear case is explicitly acknowledged. Geopolitical risk remains significant, as roughly 20 percent of revenue is exposed to China; a full export ban could affect about $10 billion in annual sales. Competitive pressures from AMD and Intel may increase. Valuation risk is present, as elevated expectations mean that any earnings disappointment may cause substantial volatility. However, the risk-reward profile remains favorable, with downside technical and valuation support estimated near $800 (approximately 25 times earnings per share).

Actionability and Trade Management:
Entry strategy involves accumulating shares in the $1,000 to $1,050 price range. Position sizing is limited to about 5 percent of the total investment portfolio given its high-conviction nature but elevated volatility. Exit criteria are defined: the entire position will be closed if gross margins fall below 70 percent for two consecutive quarters or if revenue growth declines to below 15 percent year over year. A hard stop loss is placed at $850 to limit downside risk. The monitoring plan includes tracking quarterly data center revenue, gross margins, and inventory levels reported in 10-Q filings.

Conclusion:
NVIDIA presents a compelling investment opportunity. The combination of high growth, dominant market share, strong financial metrics, and clearly defined entry, exit, and risk management parameters supports a strong buy thesis with a 12-month target price of $1,500.`;

export default function UploadSection({ onAnalyze, error, initialText = '' }) {
    const [text, setText] = useState(initialText);
    const [dragActive, setDragActive] = useState(false);

    // Update text when initialText changes (for Edit & Retry flow)
    useEffect(() => {
        if (initialText && initialText !== text) {
            setText(initialText);
        }
    }, [initialText]);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (text.trim().length >= 50) {
            onAnalyze(text);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setDragActive(false);

        const file = e.dataTransfer.files[0];
        if (file && file.type === 'text/plain') {
            const reader = new FileReader();
            reader.onload = (event) => {
                setText(event.target.result);
            };
            reader.readAsText(file);
        }
    };

    const loadSample = () => {
        setText(SAMPLE_THESIS);
    };

    return (
        <section className="max-w-4xl mx-auto px-4 pb-20">
            <motion.form
                onSubmit={handleSubmit}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
            >
                {/* Error display */}
                {error && (
                    <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20 flex items-start gap-3"
                    >
                        <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                        <p className="text-red-300">{error}</p>
                    </motion.div>
                )}

                {/* Textarea */}
                <div
                    className={`relative rounded-2xl border-2 transition-colors duration-200 ${dragActive
                        ? 'border-primary-500 bg-primary-500/5'
                        : 'border-dark-border hover:border-dark-border/80'
                        }`}
                    onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
                    onDragLeave={() => setDragActive(false)}
                    onDrop={handleDrop}
                >
                    <textarea
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                        placeholder="Paste your investment thesis here, or drag and drop a .txt file..."
                        className="w-full h-64 p-6 bg-transparent text-white placeholder-gray-500 rounded-2xl focus:outline-none focus:ring-0"
                    />

                    {/* Character count */}
                    <div className="absolute bottom-4 right-4 text-sm text-gray-500">
                        {text.length} characters
                    </div>

                    {/* Upload icon overlay when empty */}
                    {!text && (
                        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none opacity-30">
                            <Upload className="w-12 h-12 text-gray-500 mb-2" />
                            <span className="text-gray-500">Drop file here</span>
                        </div>
                    )}
                </div>

                {/* Action buttons */}
                <div className="flex flex-wrap gap-4 mt-6">
                    <motion.button
                        type="submit"
                        disabled={text.trim().length < 50}
                        className="flex-1 md:flex-none px-8 py-4 rounded-xl bg-gradient-to-r from-primary-600 to-primary-500 text-white font-semibold flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed glow-primary"
                        whileHover={{ scale: text.trim().length >= 50 ? 1.02 : 1 }}
                        whileTap={{ scale: text.trim().length >= 50 ? 0.98 : 1 }}
                    >
                        <Wand2 className="w-5 h-5" />
                        Analyze Thesis
                    </motion.button>

                    <motion.button
                        type="button"
                        onClick={loadSample}
                        className="px-6 py-4 rounded-xl border border-dark-border text-gray-300 font-medium hover:bg-dark-card transition-colors"
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                    >
                        Load Sample
                    </motion.button>
                </div>

                {/* Min length hint */}
                {text.length > 0 && text.length < 50 && (
                    <p className="mt-3 text-sm text-yellow-500">
                        Minimum 50 characters required ({50 - text.length} more needed)
                    </p>
                )}
            </motion.form>
        </section>
    );
}
