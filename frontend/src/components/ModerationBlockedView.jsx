import { useState } from 'react';
import { motion } from 'framer-motion';
import { ShieldX, AlertTriangle, Edit3, Send, X, ChevronDown } from 'lucide-react';

export default function ModerationBlockedView({ moderationResult, originalText, onEdit, onRetry }) {
    const [showReviewModal, setShowReviewModal] = useState(false);
    const [reviewEmail, setReviewEmail] = useState('');
    const [reviewReason, setReviewReason] = useState('');
    const [reviewSubmitted, setReviewSubmitted] = useState(false);
    const [expandedIssues, setExpandedIssues] = useState({});

    const { decision, risk_score, issues, explanation, is_finance_related } = moderationResult;

    const isBlocked = decision === 'BLOCK';
    const isFlagged = decision === 'FLAG';

    const toggleIssue = (index) => {
        setExpandedIssues(prev => ({ ...prev, [index]: !prev[index] }));
    };

    const handleSubmitReview = async () => {
        if (!reviewEmail || !reviewEmail.includes('@')) {
            alert('Please enter a valid email address');
            return;
        }

        try {
            const API_BASE = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
                ? 'http://localhost:8000/api'
                : 'https://thesis-content-guard.onrender.com/api';

            const response = await fetch(`${API_BASE}/manual-review`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: originalText,
                    reason: reviewReason,
                    user_email: reviewEmail
                })
            });

            if (response.ok) {
                setReviewSubmitted(true);
            } else {
                alert('Failed to submit review request. Please try again.');
            }
        } catch (error) {
            console.error('Review submission error:', error);
            alert('Failed to submit review request. Please try again.');
        }
    };

    return (
        <div className="min-h-screen gradient-bg py-12 px-4">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="max-w-2xl mx-auto"
            >
                {}
                <div className="text-center mb-8">
                    <div className={`inline-flex items-center justify-center w-20 h-20 rounded-full mb-6 ${isBlocked ? 'bg-red-500/20' : 'bg-yellow-500/20'
                        }`}>
                        {isBlocked ? (
                            <ShieldX className="w-10 h-10 text-red-400" />
                        ) : (
                            <AlertTriangle className="w-10 h-10 text-yellow-400" />
                        )}
                    </div>

                    <h1 className={`text-3xl font-bold mb-3 ${isBlocked ? 'text-red-400' : 'text-yellow-400'
                        }`}>
                        {isBlocked ? 'Content Could Not Be Analyzed' : 'Content Requires Attention'}
                    </h1>

                    <p className="text-gray-400 max-w-md mx-auto">
                        {isBlocked
                            ? 'Your thesis contains content that needs to be revised before analysis.'
                            : 'We found potential issues that should be addressed before proceeding.'
                        }
                    </p>
                </div>

                {}
                <div className="flex justify-center mb-8">
                    <div className={`px-6 py-3 rounded-full border ${isBlocked
                        ? 'border-red-500/30 bg-red-500/10'
                        : 'border-yellow-500/30 bg-yellow-500/10'
                        }`}>
                        <span className="text-gray-400 mr-2">Risk Score:</span>
                        <span className={`font-bold ${isBlocked ? 'text-red-400' : 'text-yellow-400'
                            }`}>
                            {(risk_score * 100).toFixed(0)}%
                        </span>
                    </div>
                </div>

                {}
                <div className="space-y-3 mb-8">
                    <h2 className="text-lg font-semibold text-white mb-4">Issues Found</h2>

                    {issues && issues.length > 0 ? (
                        (() => {
                            // Check if any issue is expanded
                            const hasExpandedIssue = Object.values(expandedIssues).some(v => v);

                            return issues.map((issue, index) => {
                                const isExpanded = expandedIssues[index];
                                const shouldDim = hasExpandedIssue && !isExpanded;

                                return (
                                    <motion.div
                                        key={index}
                                        initial={{ opacity: 0, x: -20 }}
                                        animate={{
                                            opacity: shouldDim ? 0.4 : 1,
                                            x: 0,
                                            scale: shouldDim ? 0.98 : 1
                                        }}
                                        transition={{
                                            delay: index * 0.05,
                                            opacity: { duration: 0.2 },
                                            scale: { duration: 0.2 }
                                        }}
                                        className={`rounded-xl border overflow-hidden transition-colors duration-200 ${isExpanded
                                            ? 'border-primary-500/50 bg-dark-card shadow-lg shadow-primary-500/10'
                                            : 'border-dark-border bg-dark-card'
                                            }`}
                                    >
                                        <button
                                            onClick={() => toggleIssue(index)}
                                            className="w-full p-4 flex items-center justify-between text-left hover:bg-white/5 transition-colors"
                                        >
                                            <div className="flex items-center gap-3">
                                                <div className={`w-2 h-2 rounded-full ${issue.type.toLowerCase().includes('severe') ? 'bg-red-500' :
                                                    issue.type.toLowerCase().includes('profanity') || issue.type.toLowerCase().includes('toxic') ? 'bg-orange-500' :
                                                        issue.type.toLowerCase().includes('scam') ? 'bg-red-500' :
                                                            issue.type.toLowerCase().includes('off') ? 'bg-yellow-500' :
                                                                'bg-gray-500'
                                                    }`} />
                                                <span className="font-medium text-white capitalize">
                                                    {issue.type.replace('_', ' ')}
                                                </span>
                                                <span className="text-xs text-gray-500 font-mono ml-2">
                                                    "{issue.found}"
                                                </span>
                                            </div>
                                            <motion.div
                                                animate={{ rotate: isExpanded ? 180 : 0 }}
                                                transition={{ duration: 0.2 }}
                                            >
                                                <ChevronDown className="w-5 h-5 text-gray-400" />
                                            </motion.div>
                                        </button>

                                        <motion.div
                                            initial={false}
                                            animate={{
                                                height: isExpanded ? 'auto' : 0,
                                                opacity: isExpanded ? 1 : 0
                                            }}
                                            transition={{ duration: 0.25, ease: 'easeInOut' }}
                                            style={{ overflow: 'hidden' }}
                                        >
                                            <div className="px-4 pb-4 border-t border-dark-border">
                                                <div className="mt-3 p-3 bg-dark-bg rounded-lg">
                                                    <p className="text-sm text-gray-400 mb-1">Found:</p>
                                                    <p className="text-white font-mono text-sm bg-red-500/10 px-2 py-1 rounded inline-block">"{issue.found}"</p>
                                                </div>
                                                <div className="mt-3 flex items-start gap-2">
                                                    <span className="text-2xl">💡</span>
                                                    <p className="text-sm text-primary-300">{issue.suggestion}</p>
                                                </div>
                                            </div>
                                        </motion.div>
                                    </motion.div>
                                );
                            });
                        })()
                    ) : (
                        <div className="p-4 rounded-xl border border-dark-border bg-dark-card">
                            <p className="text-gray-400">{explanation || 'Content did not pass moderation checks.'}</p>
                        </div>
                    )}
                </div>

                {}
                <div className="flex flex-col sm:flex-row gap-4">
                    <motion.button
                        onClick={onEdit}
                        className="flex-1 px-6 py-4 rounded-xl bg-gradient-to-r from-primary-600 to-primary-500 text-white font-semibold flex items-center justify-center gap-2"
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                    >
                        <Edit3 className="w-5 h-5" />
                        Edit & Retry
                    </motion.button>

                    <motion.button
                        onClick={() => setShowReviewModal(true)}
                        className="flex-1 px-6 py-4 rounded-xl border border-dark-border text-gray-300 font-medium flex items-center justify-center gap-2 hover:bg-dark-card transition-colors"
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                    >
                        <Send className="w-5 h-5" />
                        Request Manual Review
                    </motion.button>
                </div>

                {}
                {showReviewModal && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4"
                        onClick={() => setShowReviewModal(false)}
                    >
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            className="bg-dark-card border border-dark-border rounded-2xl p-6 max-w-md w-full"
                            onClick={(e) => e.stopPropagation()}
                        >
                            {reviewSubmitted ? (
                                <div className="text-center py-4">
                                    <div className="w-16 h-16 rounded-full bg-green-500/20 flex items-center justify-center mx-auto mb-4">
                                        <span className="text-3xl">✓</span>
                                    </div>
                                    <h3 className="text-xl font-semibold text-white mb-2">Request Submitted</h3>
                                    <p className="text-gray-400 mb-4">We'll review your content within 24 hours.</p>
                                    <button
                                        onClick={() => {
                                            setShowReviewModal(false);
                                            setReviewSubmitted(false);
                                        }}
                                        className="px-6 py-2 rounded-lg bg-primary-600 text-white"
                                    >
                                        Close
                                    </button>
                                </div>
                            ) : (
                                <>
                                    <div className="flex justify-between items-center mb-4">
                                        <h3 className="text-xl font-semibold text-white">Request Manual Review</h3>
                                        <button onClick={() => setShowReviewModal(false)} className="text-gray-400 hover:text-white">
                                            <X className="w-5 h-5" />
                                        </button>
                                    </div>

                                    <p className="text-gray-400 text-sm mb-4">
                                        If you believe your content was incorrectly flagged, submit a review request.
                                    </p>

                                    <div className="space-y-4">
                                        <div>
                                            <label className="block text-sm text-gray-400 mb-1">Email Address *</label>
                                            <input
                                                type="email"
                                                value={reviewEmail}
                                                onChange={(e) => setReviewEmail(e.target.value)}
                                                placeholder="your@email.com"
                                                className="w-full px-4 py-3 rounded-lg bg-dark-bg border border-dark-border text-white placeholder-gray-500 focus:outline-none focus:border-primary-500"
                                            />
                                        </div>

                                        <div>
                                            <label className="block text-sm text-gray-400 mb-1">Reason (Optional)</label>
                                            <textarea
                                                value={reviewReason}
                                                onChange={(e) => setReviewReason(e.target.value)}
                                                placeholder="Explain why you think this content should be allowed..."
                                                rows={3}
                                                className="w-full px-4 py-3 rounded-lg bg-dark-bg border border-dark-border text-white placeholder-gray-500 focus:outline-none focus:border-primary-500 resize-none"
                                            />
                                        </div>

                                        <button
                                            onClick={handleSubmitReview}
                                            className="w-full px-6 py-3 rounded-lg bg-primary-600 text-white font-medium hover:bg-primary-500 transition-colors"
                                        >
                                            Submit Review Request
                                        </button>
                                    </div>
                                </>
                            )}
                        </motion.div>
                    </motion.div>
                )}
            </motion.div>
        </div>
    );
}
