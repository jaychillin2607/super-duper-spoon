import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const apiClient = axios.create({
	baseURL: API_BASE_URL,
	headers: {
		"Content-Type": "application/json",
	},
});

/**
 * Enriches business data with TIB verification API
 */
export async function enrichBusinessData(
	businessName: string,
	zipCode: string,
	sessionId: string
) {
	try {
		const response = await apiClient.post("/enrichment", {
			business_name: businessName,
			zip_code: zipCode,
			session_id: sessionId,
		});
		return response.data;
	} catch (error) {
		console.error("Error enriching business data:", error);
		throw error;
	}
}

/**
 * Submit lead data from the form directly
 */
export async function submitLeadData(data: any) {
	try {
		const response = await apiClient.post("/leads", data);
		return response.data;
	} catch (error) {
		console.error("Error submitting lead data:", error);
		throw error;
	}
}

/**
 * Submit lead from session data
 */
export async function submitLeadFromSession(sessionId: string) {
	try {
		const response = await apiClient.post(`/leads/submit/${sessionId}`);
		return response.data;
	} catch (error) {
		console.error("Error submitting lead from session:", error);
		throw error;
	}
}

/**
 * Adds a health check function to verify backend connectivity
 */
export async function checkBackendHealth() {
	try {
		const response = await apiClient.get("/health");
		return response.data.status === "ok";
	} catch (error) {
		console.error("Backend health check failed:", error);
		return false;
	}
}
