const API_BASE = "http://127.0.0.1:8000";

export function saveAuthTokens({ access_token, refresh_token, id, username }) {
  if (access_token) {
    localStorage.setItem("token", access_token);
  }
  if (refresh_token) {
    localStorage.setItem("refresh_token", refresh_token);
  }
  if (id !== undefined && id !== null) {
    localStorage.setItem("id", id);
  }
  if (username) {
    localStorage.setItem("username", username);
  }
}

export function clearAuthTokens() {
  localStorage.removeItem("token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("id");
  localStorage.removeItem("username");
}

export async function refreshAccessToken() {
  const refresh_token = localStorage.getItem("refresh_token");
  if (!refresh_token) {
    return null;
  }

  const response = await fetch(`${API_BASE}/refresh`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ refresh_token }),
  });

  if (!response.ok) {
    clearAuthTokens();
    return null;
  }

  const data = await response.json().catch(() => null);
  if (!data?.access_token) {
    clearAuthTokens();
    return null;
  }

  saveAuthTokens({
    access_token: data.access_token,
    refresh_token: data.refresh_token,
  });

  return data.access_token;
}

export async function fetchWithAuth(url, options = {}) {
  const token = localStorage.getItem("token");
  const headers = {
    ...(options.headers || {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };

  let response = await fetch(url, { ...options, headers });
  if (response.status !== 401) {
    return response;
  }

  const newToken = await refreshAccessToken();
  if (!newToken) {
    return response;
  }

  const retryHeaders = {
    ...(options.headers || {}),
    Authorization: `Bearer ${newToken}`,
  };
  response = await fetch(url, { ...options, headers: retryHeaders });

  if (response.status === 401) {
    clearAuthTokens();
  }

  return response;
}
