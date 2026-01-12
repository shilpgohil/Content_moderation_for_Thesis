import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { analyzeThesis, moderateContent } from './api/analyzer';
import Hero from './components/Hero';
import UploadSection from './components/UploadSection';
import Dashboard from './components/Dashboard';
import LoadingState from './components/LoadingState';
import ModerationLoadingState from './components/ModerationLoadingState';
import ModerationBlockedView from './components/ModerationBlockedView';

function App() {
    // States: upload | moderating | moderation_blocked | loading | dashboard
    const [view, setView] = useState('upload');
    const [analysisResult, setAnalysisResult] = useState(null);
    const [moderationResult, setModerationResult] = useState(null);
    const [currentText, setCurrentText] = useState('');
    const [error, setError] = useState(null);

    const handleAnalyze = async (thesisText) => {
        setCurrentText(thesisText);
        setView('moderating');
        setError(null);

        try {
            // Step 1: Content moderation check
            console.log('Starting moderation check...');
            const modResult = await moderateContent(thesisText);
            console.log('Moderation result:', modResult);

            // Check if content can proceed
            if (!modResult.can_proceed) {
                // Content blocked or flagged - show blocked view
                setModerationResult(modResult);
                setView('moderation_blocked');
                return;
            }

            // Step 2: Proceed to thesis analysis
            setView('loading');
            const result = await analyzeThesis(thesisText);
            setAnalysisResult(result);
            setView('dashboard');

        } catch (err) {
            console.error('Analysis failed:', err);

            let errorMessage = 'Analysis failed. Please try again.';
            if (err.response?.data?.detail) {
                const detail = err.response.data.detail;
                if (typeof detail === 'string') {
                    errorMessage = detail;
                } else if (Array.isArray(detail)) {
                    errorMessage = detail.map(e => e.msg).join(', ');
                } else if (typeof detail === 'object') {
                    errorMessage = JSON.stringify(detail);
                }
            } else if (err.message) {
                errorMessage = err.message;
            }

            setError(errorMessage);
            setView('upload');
        }
    };

    const handleReset = () => {
        setAnalysisResult(null);
        setModerationResult(null);
        setCurrentText('');
        setError(null);
        setView('upload');
    };

    const handleEditFromBlocked = () => {
        // Return to upload view with text preserved
        setModerationResult(null);
        setView('upload');
        // Note: currentText is preserved, UploadSection will need to accept initialText prop
    };

    return (
        <div className="min-h-screen gradient-bg">
            <AnimatePresence mode="wait">
                {view === 'upload' && (
                    <motion.div
                        key="upload"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.3 }}
                    >
                        <Hero />
                        <UploadSection
                            onAnalyze={handleAnalyze}
                            error={error}
                            initialText={currentText}
                        />
                    </motion.div>
                )}

                {view === 'moderating' && (
                    <motion.div
                        key="moderating"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.3 }}
                    >
                        <ModerationLoadingState />
                    </motion.div>
                )}

                {view === 'moderation_blocked' && moderationResult && (
                    <motion.div
                        key="moderation_blocked"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.4 }}
                    >
                        <ModerationBlockedView
                            moderationResult={moderationResult}
                            originalText={currentText}
                            onEdit={handleEditFromBlocked}
                        />
                    </motion.div>
                )}

                {view === 'loading' && (
                    <motion.div
                        key="loading"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.3 }}
                    >
                        <LoadingState message="Analyzing thesis strength..." />
                    </motion.div>
                )}

                {view === 'dashboard' && analysisResult && (
                    <motion.div
                        key="dashboard"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.4 }}
                    >
                        <Dashboard result={analysisResult} onReset={handleReset} />
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}

export default App;
