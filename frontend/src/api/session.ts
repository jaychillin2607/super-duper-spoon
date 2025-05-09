import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const apiClient = axios.create({
	baseURL: API_BASE_URL,
	headers: {
		"Content-Type": "application/json",
	},
});

/**
 * Create a new session on the backend
 */
export async function createSession() {
	try {
		const response = await apiClient.post("/sessions");
		return response.data;
	} catch (error) {
		console.error("Error creating session:", error);
		throw error;
	}
}

/**
 * Get session data from the backend
 */
export async function getSession(sessionId: string) {
	try {
		const response = await apiClient.get(`/sessions/${sessionId}`);
		return response.data;
	} catch (error) {
		if (axios.isAxiosError(error) && error.response?.status === 404) {
			return null;
		}
		console.error("Error retrieving session:", error);
		throw error;
	}
}

/**
 * Update session data on the backend
 */
export async function updateSession(sessionId: string, formData: any) {
	try {
		const payload = {
			form_data: formData,
		};

		const response = await apiClient.put(`/sessions/${sessionId}`, payload);
		return response.data;
	} catch (error) {
		console.error("Error updating session:", error);
		throw error;
	}
}

/**
 * Delete session from the backend
 */
export async function deleteSession(sessionId: string) {
	try {
		await apiClient.delete(`/sessions/${sessionId}`);
		return true;
	} catch (error) {
		console.error("Error deleting session:", error);
		return false;
	}
}

/**
 * Initialize session: either retrieve existing or create new
 * This is the main function that should be called when the app starts
 */
export async function initializeSession(): Promise<{
	sessionId: string;
	sessionData: any;
}> {
	const storedSessionId = localStorage.getItem("sessionId");
	let sessionId: string;
	let sessionData: any = null;

	if (storedSessionId) {
		try {
			sessionData = await getSession(storedSessionId);

			if (sessionData) {
				sessionId = storedSessionId;
				return { sessionId, sessionData };
			}
		} catch (error) {
			console.error("Failed to retrieve session, will create new", error);
		}
	}

	try {
		const newSession = await createSession();
		sessionId = newSession.session_id;
		sessionData = newSession;

		localStorage.setItem("sessionId", sessionId);

		return { sessionId, sessionData };
	} catch (error) {
		console.error("Failed to create session", error);
		throw error;
	}
}
