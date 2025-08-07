const API_BASE_URL =
    window._env_?.REACT_APP_API_ENDPOINT ||
    window.location.origin.replace(":3000", ":8000");

export default API_BASE_URL;