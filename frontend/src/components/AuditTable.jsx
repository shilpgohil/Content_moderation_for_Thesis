import { AlertCircle, CheckCircle, ArrowRight, Link2 } from 'lucide-react';

export default function AuditTable({ auditTable, logicChain }) {
    // Handle both array and object formats
    const auditData = Array.isArray(auditTable) ? auditTable : [];
    const chainData = Array.isArray(logicChain) ? logicChain : [];

    return (
        <div className="space-y-10">
            {}
            <div>
                <div className="flex items-center gap-3 mb-6">
                    <AlertCircle className="w-6 h-6 text-yellow-400" />
                    <h3 className="text-xl font-semibold">Fact vs Assumption Audit</h3>
                </div>

                <p className="text-gray-400 text-sm mb-6">
                    Identifies statements that may be presented differently than they should be.
                    For example, assumptions stated as certainties or projections presented as facts.
                </p>

                {auditData.length > 0 ? (
                    <div className="space-y-4">
                        {auditData.map((entry, i) => (
                            <div
                                key={i}
                                className="p-5 rounded-xl bg-dark-card border border-dark-border hover:border-yellow-500/30 transition-colors"
                            >
                                {}
                                <div className="flex items-center gap-4 mb-3">
                                    <span className="text-gray-500 font-mono text-sm">
                                        #{entry.sentence_index}
                                    </span>
                                    <div className="flex items-center gap-2">
                                        <span className="px-3 py-1 rounded-full bg-red-500/20 text-red-400 text-xs font-medium">
                                            {entry.classified_as}
                                        </span>
                                        <ArrowRight className="w-4 h-4 text-gray-500" />
                                        <span className="px-3 py-1 rounded-full bg-green-500/20 text-green-400 text-xs font-medium">
                                            {entry.should_be}
                                        </span>
                                    </div>
                                </div>

                                {}
                                <p className="text-gray-300 mb-3 leading-relaxed">
                                    "{entry.statement}"
                                </p>

                                {}
                                <div className="flex items-start gap-2 p-3 rounded-lg bg-yellow-500/5 border border-yellow-500/20">
                                    <AlertCircle className="w-4 h-4 text-yellow-400 flex-shrink-0 mt-0.5" />
                                    <span className="text-yellow-300 text-sm">{entry.issue}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="p-8 text-center bg-dark-card rounded-xl border border-dark-border">
                        <CheckCircle className="w-12 h-12 mx-auto mb-4 text-green-500" />
                        <p className="text-green-400 font-medium">All statements properly classified!</p>
                        <p className="text-gray-500 text-sm mt-2">
                            No cases of assumptions presented as facts or vice versa detected.
                        </p>
                    </div>
                )}
            </div>

            {}
            <div>
                <div className="flex items-center gap-3 mb-6">
                    <Link2 className="w-6 h-6 text-primary-400" />
                    <h3 className="text-xl font-semibold">Logic Chain</h3>
                </div>

                <p className="text-gray-400 text-sm mb-6">
                    Maps the argument flow from main claims to supporting evidence.
                </p>

                {chainData.length > 0 ? (
                    <div className="space-y-3">
                        {chainData.slice(0, 10).map((node, i) => (
                            <div
                                key={i}
                                className={`p-4 rounded-xl border ${node.claim_type === 'main_claim' || node.type === 'main_claim'
                                        ? 'border-primary-500/30 bg-primary-500/5'
                                        : 'border-dark-border bg-dark-card'
                                    }`}
                            >
                                <div className="flex items-start gap-3">
                                    <div className={`flex-shrink-0 mt-1 ${node.has_evidence ? 'text-green-400' : 'text-yellow-400'
                                        }`}>
                                        {node.has_evidence ? (
                                            <CheckCircle className="w-5 h-5" />
                                        ) : (
                                            <AlertCircle className="w-5 h-5" />
                                        )}
                                    </div>
                                    <div className="flex-1">
                                        <div className="flex items-center gap-2 mb-2">
                                            <span className="px-2 py-0.5 rounded text-xs bg-dark-border capitalize">
                                                {((node.claim_type || node.type || 'claim').replace(/_/g, ' '))}
                                            </span>
                                            <span className="text-xs text-gray-500">
                                                Confidence: {((node.confidence || 0.5) * 100).toFixed(0)}%
                                            </span>
                                        </div>
                                        <p className="text-gray-300 text-sm line-clamp-2">
                                            {node.claim || node.text}
                                        </p>
                                        {(node.evidence_refs || node.evidence_sentences)?.length > 0 && (
                                            <p className="mt-2 text-xs text-gray-500">
                                                Evidence refs: #{(node.evidence_refs || node.evidence_sentences).join(', #')}
                                            </p>
                                        )}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="p-8 text-center bg-dark-card rounded-xl border border-dark-border">
                        <Link2 className="w-12 h-12 mx-auto mb-4 text-primary-400" />
                        <p className="text-gray-400 font-medium">Logic chain processing complete</p>
                        <p className="text-gray-500 text-sm mt-2">
                            View other tabs for detailed sentence-level analysis.
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}
