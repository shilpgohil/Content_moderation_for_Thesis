import axios from 'axios';

// Auto-detect environment based on browser URL
const API_BASE = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? 'http://localhost:8000/api'
    : 'https://content-moderation-for-thesis.onrender.com/api';

console.log('Active API Base:', API_BASE);

export const moderateContent = async (text) => {
    const response = await axios.post(`${API_BASE}/moderate`, { text });
    return response.data;
};

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

export const submitManualReview = async (text, reason, userEmail) => {
    const response = await axios.post(`${API_BASE}/manual-review`, {
        text,
        reason,
        user_email: userEmail
    });
    return response.data;
};

export const healthCheck = async () => {
    const response = await axios.get(API_BASE.replace('/api', ''));
    return response.data;
};
