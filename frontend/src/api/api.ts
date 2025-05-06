import axios from "axios";

const API_BASE_URL = "http://localhost:8000"; // Change this to your FastAPI server URL

export async function enrichBusinessData(
  businessName: string,
  zipCode: string
) {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/enrich`, null, {
      params: {
        business_name: businessName,
        zip_code: zipCode,
      },
    });
    return response.data;
  } catch (error) {
    console.error("Error enriching business data:", error);
    throw error;
  }
}

export async function saveSessionData(sessionId: string, data: any) {
  try {
    await axios.post(`${API_BASE_URL}/api/save-session/${sessionId}`, data);
  } catch (error) {
    console.error("Error saving session data:", error);
    // Continue even if saving to backend fails - we still have localStorage
  }
}

export async function getSessionData(sessionId: string) {
  try {
    const response = await axios.get(
      `${API_BASE_URL}/api/get-session/${sessionId}`
    );
    return response.data;
  } catch (error) {
    console.error("Error getting session data:", error);
    return null;
  }
}

export async function submitLeadData(data: any) {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/leads`, data);
    return response.data;
  } catch (error) {
    console.error("Error submitting lead data:", error);
    throw error;
  }
}
