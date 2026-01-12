import { AlertTriangle, Type, GitBranch, Database } from 'lucide-react';

export default function WeaknessReport({ report }) {
    if (!report) {
        return (
            <div className="p-8 text-center text-gray-500 bg-dark-card rounded-xl border border-dark-border">
                <p>No weakness report available</p>
            </div>
        );
    }

    const { language, logical, data } = report;

    return (
        <div className="grid md:grid-cols-3 gap-6">
            {/* Language Weaknesses */}
            <WeaknessCard
                icon={<Type className="w-5 h-5" />}
                title="Language Weaknesses"
                color="yellow"
            >
                {language?.vague_terms?.length > 0 && (
                    <WeaknessItem label="Vague terms" items={language.vague_terms} />
                )}
                {language?.weasel_words?.length > 0 && (
                    <WeaknessItem label="Weasel words" items={language.weasel_words} />
                )}
                {language?.unquantified_claims?.length > 0 && (
                    <WeaknessItem
                        label="Unquantified claims"
                        count={language.unquantified_claims.length}
                    />
                )}
                {!language?.vague_terms?.length &&
                    !language?.weasel_words?.length &&
                    !language?.unquantified_claims?.length && (
                        <p className="text-gray-500 text-sm">No language issues detected</p>
                    )}
            </WeaknessCard>

            {/* Logical Weaknesses */}
            <WeaknessCard
                icon={<GitBranch className="w-5 h-5" />}
                title="Logical Weaknesses"
                color="orange"
            >
                {logical?.missing_connections?.length > 0 && (
                    <WeaknessItem label="Missing connections" count={logical.missing_connections.length} />
                )}
                {logical?.circular_reasoning?.length > 0 && (
                    <WeaknessItem label="Circular reasoning" count={logical.circular_reasoning.length} />
                )}
                {logical?.unstated_assumptions?.length > 0 && (
                    <div className="mb-3">
                        <p className="text-gray-400 text-sm mb-2">Unstated assumptions:</p>
                        <ul className="space-y-1">
                            {logical.unstated_assumptions.slice(0, 5).map((item, i) => (
                                <li key={i} className="text-xs text-orange-400 flex items-start gap-2">
                                    <AlertTriangle className="w-3 h-3 flex-shrink-0 mt-0.5" />
                                    <span>{item}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
                {!logical?.missing_connections?.length &&
                    !logical?.circular_reasoning?.length &&
                    !logical?.unstated_assumptions?.length && (
                        <p className="text-gray-500 text-sm">No logical issues detected</p>
                    )}
            </WeaknessCard>

            {/* Data Weaknesses */}
            <WeaknessCard
                icon={<Database className="w-5 h-5" />}
                title="Data Weaknesses"
                color="red"
            >
                {data?.unsourced_statistics?.length > 0 && (
                    <WeaknessItem
                        label="Unsourced statistics"
                        count={data.unsourced_statistics.length}
                    />
                )}
                {data?.outdated_info?.length > 0 && (
                    <WeaknessItem label="Outdated info" count={data.outdated_info.length} />
                )}
                {data?.missing_context?.length > 0 && (
                    <div className="mb-3">
                        <p className="text-gray-400 text-sm mb-2">Missing context:</p>
                        <ul className="space-y-1">
                            {data.missing_context.slice(0, 5).map((item, i) => (
                                <li key={i} className="text-xs text-red-400 flex items-start gap-2">
                                    <AlertTriangle className="w-3 h-3 flex-shrink-0 mt-0.5" />
                                    <span>{item}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
                {!data?.unsourced_statistics?.length &&
                    !data?.outdated_info?.length &&
                    !data?.missing_context?.length && (
                        <p className="text-gray-500 text-sm">No data issues detected</p>
                    )}
            </WeaknessCard>
        </div>
    );
}

function WeaknessCard({ icon, title, color, children }) {
    const colors = {
        yellow: 'border-yellow-500/30 bg-yellow-500/5',
        orange: 'border-orange-500/30 bg-orange-500/5',
        red: 'border-red-500/30 bg-red-500/5',
    };

    const iconColors = {
        yellow: 'text-yellow-400 bg-yellow-500/20',
        orange: 'text-orange-400 bg-orange-500/20',
        red: 'text-red-400 bg-red-500/20',
    };

    return (
        <div className={`p-5 rounded-xl border ${colors[color]}`}>
            <div className="flex items-center gap-3 mb-4">
                <div className={`p-2 rounded-lg ${iconColors[color]}`}>
                    {icon}
                </div>
                <h3 className="font-medium">{title}</h3>
            </div>
            <div className="space-y-3">
                {children}
            </div>
        </div>
    );
}

function WeaknessItem({ label, items, count }) {
    return (
        <div className="mb-3">
            <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400">{label}</span>
                {count !== undefined && (
                    <span className="px-2 py-0.5 rounded bg-dark-border text-gray-300 text-xs">
                        {count}
                    </span>
                )}
            </div>
            {items && items.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                    {items.map((item, i) => (
                        <span key={i} className="px-2 py-0.5 rounded bg-dark-card text-gray-400 text-xs">
                            {item}
                        </span>
                    ))}
                </div>
            )}
        </div>
    );
}
