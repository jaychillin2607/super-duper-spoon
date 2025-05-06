import {
  getSessionData as getSessionDataFromApi,
  saveSessionData as saveSessionDataToApi,
} from "./api";

// Generate a random session ID
export function generateSessionId(): string {
  return (
    Math.random().toString(36).substring(2, 15) +
    Math.random().toString(36).substring(2, 15)
  );
}

// Save session data to localStorage and backend
export async function saveSessionData(
  sessionId: string,
  data: any
): Promise<void> {
  // Save to localStorage
  localStorage.setItem(`form_data_${sessionId}`, JSON.stringify(data));

  // Save to backend
  try {
    await saveSessionDataToApi(sessionId, data);
  } catch (error) {
    console.error(
      "Failed to save session to backend, but saved to localStorage",
      error
    );
  }
}

// Get session data from localStorage or backend
export async function getSessionData(sessionId: string): Promise<any> {
  // Try to get from localStorage first
  const localData = localStorage.getItem(`form_data_${sessionId}`);

  if (localData) {
    return JSON.parse(localData);
  }

  // If not in localStorage, try to get from backend
  try {
    return await getSessionDataFromApi(sessionId);
  } catch (error) {
    console.error("Failed to get session data", error);
    return null;
  }
}
