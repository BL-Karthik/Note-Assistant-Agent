const API_URL = import.meta.env.PROD
  ? "/api"
  : "http://127.0.0.1:8000";

export async function sendMessageToBackend(message) {
  try {
    const response = await fetch(`${API_URL}/classify`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        messege: message,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.detail || "Something went wrong with the backend"
      );
    }

    return data;
  } catch (error) {
    console.error("Chat API Error:", error);
    throw error;
  }
}