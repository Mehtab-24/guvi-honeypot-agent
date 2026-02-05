import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002'; // Configurable for Production

export interface Interaction {
    timestamp: string;
    client_id: string;
    message: string;
    reply: string;
    extracted_intelligence: {
        upi_id: string | null;
        bank_details: string | null;
        phishing_links: string[];
    };
    scam_detected: boolean;
    suspicion_level: string;
    reasoning: string;
    turns_count: number;
}

export interface StatsResponse {
    interactions: Interaction[];
    turn_counts: Record<string, number>;
}

export const fetchDashboardData = async (): Promise<StatsResponse> => {
    try {
        const response = await axios.get(`${API_BASE_URL}/stats`);
        return response.data;
    } catch (error) {
        console.error("Error fetching SOC stats:", error);
        return { interactions: [], turn_counts: {} };
    }
};

export interface IntelItem {
    type: string;
    value: string;
    source: string;
}

export const fetchIntel = async (): Promise<IntelItem[]> => {
    try {
        const response = await axios.get(`${API_BASE_URL}/api/intel`);
        return response.data;
    } catch (error) {
        console.error("Error fetching intel:", error);
        return [];
    }
};

export const reportScam = async (): Promise<{ status: string, message: string }> => {
    try {
        const response = await axios.post(`${API_BASE_URL}/api/report`);
        return response.data;
    } catch (error) {
        console.error("Error reporting scam:", error);
        return { status: "error", message: "Failed to connect to NPCI." };
    }
};
