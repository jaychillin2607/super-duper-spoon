const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

export async function fetchLeads() {
  const response = await fetch(`${API_URL}/api/leads`);
  return response.json();
}

export async function saveSession(sessionId: string, data: any) {
  const response = await fetch(`${API_URL}/api/save-session/${sessionId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return response.json();
}
