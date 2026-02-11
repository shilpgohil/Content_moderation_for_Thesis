import { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, FileDown } from 'lucide-react';
import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';
import ScoreGauge from './ScoreGauge';
import ComponentCards from './ComponentCards';
import SentenceAnalysis from './SentenceAnalysis';
import AuditTable from './AuditTable';
import WeaknessReport from './WeaknessReport';
import BiasGauge from './BiasGauge';
import Synthesis from './Synthesis';

const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'sentences', label: 'Sentences' },
    { id: 'audit', label: 'Audit' },
    { id: 'weaknesses', label: 'Weaknesses' },
];

export default function Dashboard({ result, onReset }) {
    const [activeTab, setActiveTab] = useState('overview');

    const handleExportPDF = () => {
        const doc = new jsPDF();
        const pageWidth = doc.internal.pageSize.getWidth();
        const pageHeight = doc.internal.pageSize.getHeight();
        let y = 25;
        const lineHeight = 6;
        const margin = 20;
        const contentWidth = pageWidth - 2 * margin;

        const themeColor = [128, 0, 0]; // Maroon / Deep Red
        const subTitleColor = [60, 60, 60]; // Dark Gray for subtitles
        const lightBoxColor = [250, 245, 245]; // Very light warm background
        const dividerColor = [160, 60, 60];

        const addBackground = () => {
            doc.setFillColor(252, 251, 248); // Off-white / cream color
            doc.rect(0, 0, pageWidth, pageHeight, 'F');
        };

        addBackground();

        const checkNewPage = (neededSpace = 20) => {
            if (y > pageHeight - neededSpace) {
                doc.addPage();
                addBackground();
                y = 25;
            }
        };

        const addTitle = (text, size = 18) => {
            checkNewPage(20);
            doc.setFontSize(size);
            doc.setFont('times', 'bold');
            doc.setTextColor(33, 37, 41); // Dark gray
            doc.text(text, pageWidth / 2, y, { align: 'center' });
            y += lineHeight + 6;
        };

        const addSubtitle = (text, size = 14) => {
            checkNewPage(20);
            doc.setFontSize(size);
            doc.setFont('times', 'bold');
            doc.setTextColor(subTitleColor[0], subTitleColor[1], subTitleColor[2]); // Dark Gray for subtitles
            doc.text(text, margin, y);
            y += lineHeight + 3;
        };

        const addText = (text, size = 11) => {
            checkNewPage();
            doc.setFontSize(size);
            doc.setFont('times', 'normal');
            doc.setTextColor(73, 80, 87);
            const lines = doc.splitTextToSize(text, contentWidth);
            lines.forEach(line => {
                checkNewPage();
                doc.text(line, margin, y);
                y += lineHeight;
            });
        };

        const addBullet = (text, size = 11) => {
            checkNewPage();
            doc.setFontSize(size);
            doc.setFont('times', 'normal');
            doc.setTextColor(73, 80, 87);
            const bulletX = margin;
            const textX = margin + 8;
            const lines = doc.splitTextToSize(text, contentWidth - 8);
            lines.forEach((line, i) => {
                checkNewPage();
                if (i === 0) doc.text('•', bulletX, y);
                doc.text(line, i === 0 ? textX : margin, y);
                y += lineHeight;
            });
            if (lines.length === 0) y += lineHeight;
        };

        const addDivider = () => {
            y += 3;
            doc.setDrawColor(200, 200, 200);
            doc.setLineWidth(0.3);
            doc.line(margin, y, pageWidth - margin, y);
            y += 8;
        };

        const addSection = (title) => {
            y += 5;
            // distinct check to ensure header + at least 2-3 lines of content fit
            checkNewPage(45);
            addSubtitle(title);
            doc.setDrawColor(dividerColor[0], dividerColor[1], dividerColor[2]);
            doc.setLineWidth(0.5);
            doc.line(margin, y - 2, margin + 40, y - 2);
            y += 4;
        };
        doc.setFillColor(themeColor[0], themeColor[1], themeColor[2]);
        doc.rect(0, 0, pageWidth, 12, 'F');

        y = 30;
        addTitle('THESIS STRENGTH ANALYSIS', 20);
        addTitle('COMPREHENSIVE REPORT', 14);
        y += 5;
        doc.setFillColor(lightBoxColor[0], lightBoxColor[1], lightBoxColor[2]);
        doc.setDrawColor(themeColor[0], themeColor[1], themeColor[2]);
        // roundedRect with very thin border
        doc.setLineWidth(0.1);
        doc.roundedRect(margin - 5, y - 5, contentWidth + 10, 35, 3, 3, 'FD');

        y += 5;
        doc.setFontSize(24);
        doc.setFont('times', 'bold');
        doc.setTextColor(33, 37, 41);
        doc.text(`Score: ${result.overall_score.toFixed(1)}/100`, pageWidth / 2, y, { align: 'center' });
        y += 12;
        doc.setFontSize(16);
        doc.text(`Grade: ${result.grade}`, pageWidth / 2, y, { align: 'center' });
        y += 20;

        addDivider();
        addSection('COMPONENT SCORES');

        const scoreData = Object.entries(result.component_scores || {}).map(([key, comp]) => [
            comp.name,
            `${comp.score.toFixed(1)} / ${comp.max}`,
            `${comp.percentage.toFixed(0)}%`
        ]);

        autoTable(doc, {
            startY: y,
            head: [['Component', 'Score', 'Percentage']],
            body: scoreData,
            theme: 'striped',
            headStyles: { fillColor: themeColor },
            styles: { font: 'times', fontSize: 10 },
            margin: { left: margin, right: margin }
        });

        y = doc.lastAutoTable.finalY + 10;

        addDivider();
        addSection('ANALYSIS STATISTICS');
        const stats = result.quick_stats;
        if (stats) {
            addText(`Total Sentences Analyzed: ${stats.total_sentences}`);
            y += 2;
            addBullet(`Facts: ${stats.facts}`);
            addBullet(`Assumptions: ${stats.assumptions}`);
            addBullet(`Opinions: ${stats.opinions}`);
            addBullet(`Projections: ${stats.projections}`);
            y += 2;
            addText(`Supported Claims: ${stats.supported_percentage?.toFixed(1) || 0}%`);
        }

        addDivider();
        addSection('KEY STRENGTHS');
        (result.synthesis?.top_strengths || []).forEach((s, i) => {
            addBullet(`${s}`);
        });

        y += 5;
        addSection('KEY WEAKNESSES');
        (result.synthesis?.top_weaknesses || []).forEach((w, i) => {
            addBullet(`${w}`);
        });

        if (result.synthesis?.missing_elements?.length > 0) {
            y += 5;
            addSection('MISSING ELEMENTS');
            result.synthesis.missing_elements.forEach((m) => {
                addBullet(m);
            });
        }

        if (result.synthesis?.improvement_priorities?.length > 0) {
            y += 5;
            addSection('IMPROVEMENT PRIORITIES');
            result.synthesis.improvement_priorities.forEach((p, i) => {
                addBullet(`${i + 1}. ${p}`);
            });
        }

        addDivider();
        addSection('BIAS ANALYSIS');
        const bias = result.bias_analysis;
        if (bias) {
            addText(`Status: ${bias.is_biased ? 'Potential Bias Detected' : 'Balanced Analysis'}`);
            addText(`Sentiment Distribution: ${bias.sentiment?.positive?.toFixed(0) || 0}% Positive / ${bias.sentiment?.negative?.toFixed(0) || 0}% Negative`);
            addText(`Counter-arguments: ${bias.counter_arguments_present ? 'Present in thesis' : 'Not found'}`);
            if (bias.flags?.length > 0) {
                y += 3;
                addText('Flags:');
                bias.flags.forEach(f => addBullet(f));
            }
        }
        if (result.audit_table?.length > 0) {
            addDivider();
            addSection('FACT VS ASSUMPTION AUDIT');
            addText('Statements that may be presented differently than they should be:');
            y += 5;

            const auditData = result.audit_table.map(entry => [
                entry.sentence_index,
                entry.statement,
                entry.classified_as,
                entry.should_be,
                entry.issue
            ]);

            autoTable(doc, {
                startY: y,
                head: [['ID', 'Statement', 'Classified As', 'Should Be', 'Issue']],
                body: auditData,
                theme: 'striped',
                headStyles: { fillColor: themeColor },
                styles: { font: 'times', fontSize: 9, overflow: 'linebreak' },
                columnStyles: {
                    0: { cellWidth: 10 },
                    1: { cellWidth: 60 },
                    2: { cellWidth: 25 },
                    3: { cellWidth: 25 },
                    4: { cellWidth: 'auto' }
                },
                margin: { left: margin, right: margin }
            });

            y = doc.lastAutoTable.finalY + 10;
        }
        const totalPages = doc.internal.getNumberOfPages();
        for (let i = 1; i <= totalPages; i++) {
            doc.setPage(i);
            // Footer bar
            doc.setFillColor(themeColor[0], themeColor[1], themeColor[2]);
            doc.rect(0, pageHeight - 10, pageWidth, 10, 'F');
            // Footer text
            doc.setFontSize(8);
            doc.setFont('times', 'italic');
            doc.setTextColor(255, 255, 255);
            const date = new Date().toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
            doc.text(`Generated by Thesis Strength Analyzer | ${date}`, pageWidth / 2, pageHeight - 4, { align: 'center' });
            doc.text(`Page ${i} of ${totalPages}`, pageWidth - margin, pageHeight - 4, { align: 'right' });
        }

        // Save using Blob method for better browser compatibility
        const pdfOutput = doc.output('blob');
        const url = URL.createObjectURL(pdfOutput);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'Thesis_Analysis_Report.pdf';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    };

    return (
        <div className="min-h-screen">
            {}
            <header className="sticky top-0 z-50 bg-dark-bg/80 backdrop-blur-lg border-b border-dark-border">
                <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
                    <button
                        onClick={onReset}
                        className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
                    >
                        <ArrowLeft className="w-5 h-5" />
                        <span>New Analysis</span>
                    </button>

                    <div className="flex items-center gap-4">
                        <button
                            onClick={handleExportPDF}
                            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-primary-600 to-primary-500 text-white font-medium hover:from-primary-500 hover:to-primary-400 transition-all"
                        >
                            <FileDown className="w-4 h-4" />
                            <span className="hidden sm:inline">Export PDF</span>
                        </button>
                    </div>
                </div>
            </header>

            {}
            <main className="max-w-7xl mx-auto px-4 py-8">
                {}
                <div className="grid lg:grid-cols-3 gap-8 mb-12">
                    <div className="lg:col-span-1 flex justify-center">
                        <ScoreGauge
                            score={result.overall_score}
                            grade={result.grade}
                        />
                    </div>
                    <div className="lg:col-span-2">
                        <ComponentCards scores={result.component_scores} />
                    </div>
                </div>

                {}
                <div className="border-b border-dark-border mb-8">
                    <nav className="flex gap-8">
                        {tabs.map((tab) => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`pb-4 px-1 font-medium transition-colors ${activeTab === tab.id ? 'tab-active' : 'tab-inactive'
                                    }`}
                            >
                                {tab.label}
                            </button>
                        ))}
                    </nav>
                </div>

                {}
                <motion.div
                    key={activeTab}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.2 }}
                >
                    {activeTab === 'overview' && (
                        <div className="space-y-8">
                            <Synthesis synthesis={result.synthesis} />
                            <BiasGauge bias={result.bias_analysis} />
                        </div>
                    )}

                    {activeTab === 'sentences' && (
                        <SentenceAnalysis
                            sentences={result.sentence_analyses}
                            quickStats={result.quick_stats}
                        />
                    )}

                    {activeTab === 'audit' && (
                        <AuditTable
                            auditTable={result.audit_table}
                            logicChain={result.logic_chain}
                        />
                    )}

                    {activeTab === 'weaknesses' && (
                        <WeaknessReport report={result.weakness_report} />
                    )}
                </motion.div>
            </main>
        </div>
    );
}
