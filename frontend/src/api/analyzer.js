import axios from 'axios';

// Auto-detect environment based on browser URL
const API_BASE = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? 'http://localhost:8000/api'
    : 'https://thesis-content-guard.onrender.com/api';

/**
 * Step 1: Content Moderation Check
 * Returns: { decision, risk_score, is_finance_related, issues, explanation, can_proceed }
 */
export const moderateContent = async (text) => {
    const response = await axios.post(`${API_BASE}/moderate`, { text });
    return response.data;
};

/**
 * Step 2: Thesis Strength Analysis
 * Only called after moderation returns can_proceed = true
 */
export const analyzeThesis = async (thesisText) => {
    // Backend expects a file upload (UploadFile), so we convert text to a Blob
    const formData = new FormData();
    const blob = new Blob([thesisText], { type: 'text/plain' });
    formData.append('file', blob, 'thesis.txt');

    const response = await axios.post(`${API_BASE}/analyze`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

/**
 * Submit content for manual review
 */
export const submitManualReview = async (text, reason, userEmail) => {
    const response = await axios.post(`${API_BASE}/manual-review`, {
        text,
        reason,
        user_email: userEmail
    });
    return response.data;
};

/**
 * Health check
 */
export const healthCheck = async () => {
    const response = await axios.get(API_BASE.replace('/api', ''));
    return response.data;
};
