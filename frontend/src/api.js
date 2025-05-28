const BASE_URL = "http://localhost:8000";

// Chatbot user
export async function chat(question) {
  const res = await fetch(`${BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  return res.json(); // res.answer
}

// Admin login
export async function adminLogin(username, password) {
  const formData = new URLSearchParams();
  formData.append("username", username);
  formData.append("password", password);

  const res = await fetch(`${BASE_URL}/admin/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: formData,
  });
  return res.json();
}

// Upload PDF (admin)
export async function uploadPdf(file, token, onProgress) {
  const formData = new FormData();
  formData.append("file", file);

  // Gunakan XMLHttpRequest untuk progress upload
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", `${BASE_URL}/admin/upload`);
    xhr.setRequestHeader("Authorization", `Bearer ${token}`);
    xhr.onload = () => {
      try {
        resolve(JSON.parse(xhr.responseText));
      } catch (e) {
        reject(e);
      }
    };
    xhr.onerror = () => reject(new Error("Upload failed"));
    if (xhr.upload && onProgress) {
      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable) {
          onProgress(Math.round((e.loaded / e.total) * 100));
        }
      };
    }
    xhr.send(formData);
  });
}

// Delete PDF (admin)
export async function deletePdf(filename, token) {
  const res = await fetch(`${BASE_URL}/admin/delete/${filename}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.json();
}

// List PDF (admin)
export async function listPdfs(token) {
  const res = await fetch(`${BASE_URL}/admin/list`, {
    method: "GET",
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.json(); // [ "file1.pdf", ... ]
}

// Trigger embedding ulang (admin)
export async function reEmbed(token) {
  const res = await fetch(`${BASE_URL}/admin/embed`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.json();
}