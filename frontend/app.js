/**
 * app.js — NimbusVault Frontend
 * --------------------------------
 * This file handles ALL frontend interactions:
 *   - File upload (with drag & drop)
 *   - File listing (calls /files API)
 *   - File download (calls /files/{id} API)
 *   - Backup & restore (calls backup API)
 *   - Filter by type
 *   - Modal popup with file details
 *
 * How it works:
 *   Browser → JavaScript (fetch) → FastAPI backend → Response → Update UI
 */

// ============================================================
// CONFIGURATION
// ============================================================

// The URL of your FastAPI backend
// If running locally: http://localhost:8000
// If on a VM: http://YOUR_VM_IP:8000
const API_BASE = "http://localhost:8000";

// Keep track of all files and current filter
let allFiles = [];
let currentFilter = "all";


// ============================================================
// INITIALIZATION — Runs when the page loads
// ============================================================

document.addEventListener("DOMContentLoaded", () => {
  console.log("☁️ NimbusVault loading...");
  setupDropZone();
  setupFileInput();
  refreshFiles();
});


// ============================================================
// FILE LISTING
// ============================================================

/**
 * Fetch all files from the backend and render them.
 * Called on page load and after upload/delete.
 */
async function refreshFiles() {
  console.log("[UI] Refreshing file list...");

  try {
    const response = await fetch(`${API_BASE}/files`);

    if (!response.ok) {
      throw new Error(`Server returned ${response.status}`);
    }

    const data = await response.json();
    allFiles = data.files || [];

    updateStats(allFiles);
    renderFiles(allFiles, currentFilter);
    updateFileCountTag(allFiles, currentFilter);

    console.log(`[UI] Loaded ${allFiles.length} files`);

  } catch (err) {
    console.error("[UI] Failed to load files:", err);
    showGrid(`
      <div class="empty-state">
        <div class="empty-state-icon">⚠️</div>
        <p>Cannot connect to backend.<br>Make sure FastAPI is running on port 8000.</p>
        <p style="margin-top:8px; font-size:12px; opacity:0.5">
          Run: <code>uvicorn backend.main:app --reload</code>
        </p>
      </div>
    `);
  }
}


/**
 * Update the stats bar at the top.
 */
function updateStats(files) {
  const totalFiles   = files.length;
  const backedUp     = files.filter(f => f.is_backed_up).length;
  const totalSize    = formatBytes(files.reduce((s, f) => s + f.size_bytes, 0));
  const totalAccess  = files.reduce((s, f) => s + f.access_count, 0);

  animateNumber("totalFiles",   totalFiles);
  animateNumber("totalBackedUp", backedUp);
  document.getElementById("totalSize").textContent    = totalSize;
  animateNumber("totalAccess",  totalAccess);
}


/**
 * Animate a number counting up.
 */
function animateNumber(id, target) {
  const el = document.getElementById(id);
  const current = parseInt(el.textContent) || 0;
  const diff = target - current;
  const steps = 20;
  let step = 0;

  const interval = setInterval(() => {
    step++;
    el.textContent = Math.round(current + (diff * (step / steps)));
    if (step >= steps) {
      el.textContent = target;
      clearInterval(interval);
    }
  }, 20);
}


// ============================================================
// RENDERING FILES
// ============================================================

/**
 * Render file cards in the grid.
 * Applies filter if provided.
 */
function renderFiles(files, filter = "all") {
  const grid = document.getElementById("filesGrid");
  grid.innerHTML = "";

  // Filter files based on type
  const filtered = filter === "all"
    ? files
    : files.filter(f => f.file_type === filter);

  updateFileCountTag(files, filter);

  if (filtered.length === 0) {
    grid.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">📭</div>
        <p>${filter === "all" ? "No files uploaded yet. Drop a file above to get started!" : `No ${filter} files found.`}</p>
      </div>
    `;
    return;
  }

  // Render each file as a card
  filtered.forEach((file, index) => {
    const card = createFileCard(file, index);
    grid.appendChild(card);
  });
}


/**
 * Create a file card DOM element.
 */
function createFileCard(file, index) {
  const card = document.createElement("div");
  card.className = "file-card";
  card.style.animationDelay = `${index * 0.05}s`;

  const icon       = getFileIcon(file.file_type);
  const badgeClass = `badge-${file.file_type}`;
  const sizeStr    = formatBytes(file.size_bytes);
  const dateStr    = formatDate(file.upload_time);
  const priority   = getPriority(file.file_type, file.access_count);

  card.innerHTML = `
    ${file.is_backed_up ? '<div class="backed-up-dot" title="Backed up"></div>' : ''}
    <div class="card-top">
      <span class="card-icon">${icon}</span>
      <span class="card-badge ${badgeClass}">${file.file_type}</span>
    </div>
    <div class="card-name" title="${escapeHtml(file.filename)}">${escapeHtml(file.filename)}</div>
    <div class="card-meta">
      <span>📦 ${sizeStr}</span>
      <span>🕐 ${dateStr}</span>
    </div>
    <div class="card-footer">
      <div class="card-access">
        Downloads: <strong>${file.access_count}</strong>
        &nbsp;·&nbsp;
        <span class="priority-${priority}">${priority}</span>
      </div>
      <div class="card-actions">
        <button class="card-btn" onclick="downloadFile('${file.file_id}', event)">↓ Get</button>
        <button class="card-btn" onclick="openModal('${file.file_id}', event)">•••</button>
      </div>
    </div>
  `;

  return card;
}


function showGrid(html) {
  document.getElementById("filesGrid").innerHTML = html;
}

function updateFileCountTag(files, filter) {
  const filtered = filter === "all" ? files : files.filter(f => f.file_type === filter);
  document.getElementById("fileCountTag").textContent =
    `${filtered.length} file${filtered.length !== 1 ? "s" : ""}`;
}


// ============================================================
// FILTER
// ============================================================

function filterFiles(type, btn) {
  currentFilter = type;

  // Update active button
  document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");

  renderFiles(allFiles, type);
}


// ============================================================
// FILE UPLOAD
// ============================================================

/**
 * Set up drag-and-drop on the drop zone.
 */
function setupDropZone() {
  const zone = document.getElementById("dropZone");

  zone.addEventListener("dragover", (e) => {
    e.preventDefault();
    zone.classList.add("dragover");
  });

  zone.addEventListener("dragleave", () => {
    zone.classList.remove("dragover");
  });

  zone.addEventListener("drop", (e) => {
    e.preventDefault();
    zone.classList.remove("dragover");
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) uploadFiles(files);
  });
}


/**
 * Set up the hidden file input.
 */
function setupFileInput() {
  const input = document.getElementById("fileInput");
  input.addEventListener("change", (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) uploadFiles(files);
    input.value = ""; // Reset so same file can be re-uploaded
  });
}


/**
 * Upload an array of files one by one.
 */
async function uploadFiles(files) {
  console.log(`[Upload] Uploading ${files.length} file(s)`);

  for (const file of files) {
    await uploadSingleFile(file);
  }

  // Refresh the file list after all uploads
  setTimeout(refreshFiles, 500);
}


/**
 * Upload a single file with progress tracking.
 */
async function uploadSingleFile(file) {
  const progressList = document.getElementById("uploadProgressList");

  // Create a progress item
  const itemId = `upload-${Date.now()}`;
  const item = document.createElement("div");
  item.className = "upload-item";
  item.id = itemId;
  item.innerHTML = `
    <span class="upload-item-icon">📤</span>
    <span class="upload-item-name">${escapeHtml(file.name)}</span>
    <div class="upload-item-bar">
      <div class="upload-item-fill" id="${itemId}-fill" style="width:0%"></div>
    </div>
    <span class="upload-item-status" id="${itemId}-status">0%</span>
  `;
  progressList.appendChild(item);

  // Animate progress bar to ~80% (fake progress during upload)
  let progress = 0;
  const fakeProgress = setInterval(() => {
    progress = Math.min(progress + Math.random() * 15, 80);
    document.getElementById(`${itemId}-fill`).style.width = `${progress}%`;
    document.getElementById(`${itemId}-status`).textContent = `${Math.round(progress)}%`;
  }, 100);

  try {
    // Create FormData with the file
    const formData = new FormData();
    formData.append("file", file);

    // POST to the /upload endpoint
    const response = await fetch(`${API_BASE}/upload`, {
      method: "POST",
      body: formData
    });

    clearInterval(fakeProgress);

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || "Upload failed");
    }

    const result = await response.json();

    // Complete the progress bar
    document.getElementById(`${itemId}-fill`).style.width = "100%";
    document.getElementById(`${itemId}-status`).textContent = "Done ✓";
    item.querySelector(".upload-item-icon").textContent = getFileIcon(result.file_type);

    showToast(`✓ ${file.name} uploaded as ${result.file_type}`, "success");
    console.log(`[Upload] ✅ ${file.name} → ${result.file_type}`);

  } catch (err) {
    clearInterval(fakeProgress);
    document.getElementById(`${itemId}-fill`).style.width = "100%";
    document.getElementById(`${itemId}-fill`).style.background = "var(--red)";
    document.getElementById(`${itemId}-status`).textContent = "Failed";
    showToast(`✗ Upload failed: ${err.message}`, "error");
    console.error("[Upload] Failed:", err);
  }

  // Remove progress item after 3 seconds
  setTimeout(() => item.remove(), 3000);
}


// ============================================================
// FILE DOWNLOAD
// ============================================================

async function downloadFile(fileId, event) {
  if (event) event.stopPropagation();
  console.log(`[Download] Downloading: ${fileId}`);

  try {
    // This triggers the browser to download the file
    const url = `${API_BASE}/files/${encodeURIComponent(fileId)}`;
    const link = document.createElement("a");
    link.href = url;
    link.download = fileId;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    showToast("⬇️ Download started", "success");

    // Refresh to update access count display
    setTimeout(refreshFiles, 1000);

  } catch (err) {
    showToast(`Download failed: ${err.message}`, "error");
  }
}


// ============================================================
// BACKUP & RESTORE
// ============================================================

async function backupFile(fileId) {
  console.log(`[Backup] Backing up: ${fileId}`);
  closeModal();

  try {
    const response = await fetch(`${API_BASE}/backup/${encodeURIComponent(fileId)}`, {
      method: "POST"
    });
    const result = await response.json();

    if (result.success) {
      showToast("✓ File backed up successfully", "success");
    } else {
      showToast(`Backup note: ${result.message}`, "error");
    }
    refreshFiles();
  } catch (err) {
    showToast(`Backup failed: ${err.message}`, "error");
  }
}


async function restoreFile(fileId) {
  console.log(`[Restore] Restoring: ${fileId}`);
  closeModal();

  try {
    const response = await fetch(`${API_BASE}/restore/${encodeURIComponent(fileId)}`, {
      method: "POST"
    });
    const result = await response.json();

    if (result.success) {
      showToast("✓ File restored from backup VM", "success");
    } else {
      showToast(`Restore: ${result.message}`, "error");
    }
  } catch (err) {
    showToast(`Restore failed: ${err.message}`, "error");
  }
}


async function deleteFile(fileId) {
  if (!confirm("Are you sure you want to delete this file?")) return;
  closeModal();

  try {
    const response = await fetch(`${API_BASE}/files/${encodeURIComponent(fileId)}`, {
      method: "DELETE"
    });
    const result = await response.json();
    showToast(`✓ ${result.message}`, "success");
    refreshFiles();
  } catch (err) {
    showToast(`Delete failed: ${err.message}`, "error");
  }
}


async function backupAll() {
    console.log("[Backup] Running smart backup all...");
    showToast("⚡ Running smart backup...", "info");

    try {
        const response = await fetch(`${API_BASE}/backup/all`, { 
            method: "POST" 
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || "Backup failed");
        }
        
        const result = await response.json();
        console.log("[Backup] Smart backup result:", result);
        
        // IMPORTANT: Frontend expects result.results.backed_up
        // The backend returns { success: true, message: "...", results: {...} }
        if (result.results) {
            const backedUp = result.results.backed_up || 0;
            const skipped = result.results.skipped || 0;
            const failed = result.results.failed || 0;
            
            showToast(
                `📦 Backup complete: ${backedUp} backed up, ${skipped} skipped, ${failed} failed`, 
                "success"
            );
        } else {
            showToast("Backup completed", "success");
        }
        
        refreshFiles();
        
    } catch (err) {
        console.error("[Backup] Smart backup error:", err);
        showToast(`❌ Smart backup failed: ${err.message}`, "error");
    }
}


// ============================================================
// MODAL (File Details)
// ============================================================

async function openModal(fileId, event) {
  if (event) event.stopPropagation();

  const file = allFiles.find(f => f.file_id === fileId);
  if (!file) return;

  const priority = getPriority(file.file_type, file.access_count);

  document.getElementById("modalContent").innerHTML = `
    <div class="modal-file-icon">${getFileIcon(file.file_type)}</div>
    <div class="modal-file-name">${escapeHtml(file.filename)}</div>
    <div style="font-size:12px;color:var(--text-2);margin-bottom:16px">ID: ${file.file_id}</div>

    <div class="modal-detail-grid">
      <div class="modal-detail">
        <div class="modal-detail-label">File Type</div>
        <div class="modal-detail-value">${file.file_type}</div>
      </div>
      <div class="modal-detail">
        <div class="modal-detail-label">Size</div>
        <div class="modal-detail-value">${formatBytes(file.size_bytes)}</div>
      </div>
      <div class="modal-detail">
        <div class="modal-detail-label">Uploaded</div>
        <div class="modal-detail-value">${formatDate(file.upload_time)}</div>
      </div>
      <div class="modal-detail">
        <div class="modal-detail-label">Access Count</div>
        <div class="modal-detail-value">${file.access_count}</div>
      </div>
      <div class="modal-detail">
        <div class="modal-detail-label">Backup Status</div>
        <div class="modal-detail-value">${file.is_backed_up ? "✅ Backed Up" : "⏳ Not yet"}</div>
      </div>
      <div class="modal-detail">
        <div class="modal-detail-label">Backup Priority</div>
        <div class="modal-detail-value priority-${priority}">${priority.toUpperCase()}</div>
      </div>
    </div>

    <div class="modal-actions">
      <button class="modal-btn primary" onclick="downloadFile('${fileId}')">⬇ Download</button>
      <button class="modal-btn" onclick="backupFile('${fileId}')">☁ Backup Now</button>
      ${file.is_backed_up ? `<button class="modal-btn" onclick="restoreFile('${fileId}')">↩ Restore</button>` : ""}
      <button class="modal-btn danger" onclick="deleteFile('${fileId}')">🗑 Delete</button>
    </div>
  `;

  document.getElementById("modalOverlay").classList.add("open");
}


function closeModal() {
  document.getElementById("modalOverlay").classList.remove("open");
}


// ============================================================
// TOAST NOTIFICATIONS
// ============================================================

let toastTimeout;

function showToast(message, type = "info") {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.className = `toast ${type} show`;

  clearTimeout(toastTimeout);
  toastTimeout = setTimeout(() => {
    toast.classList.remove("show");
  }, 3500);
}


// ============================================================
// HELPER FUNCTIONS
// ============================================================

/**
 * Convert bytes to human-readable string.
 * 1024 → "1.0 KB", 1048576 → "1.0 MB"
 */
function formatBytes(bytes) {
  if (bytes === 0) return "0 B";
  const sizes = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return (bytes / Math.pow(1024, i)).toFixed(1) + " " + sizes[i];
}


/**
 * Format an ISO date string to readable format.
 */
function formatDate(isoStr) {
  if (!isoStr) return "Unknown";
  try {
    const d = new Date(isoStr);
    return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
  } catch {
    return isoStr.split("T")[0];
  }
}


/**
 * Get emoji icon for a file type.
 */
function getFileIcon(type) {
  const icons = {
    image: "🖼️", code: "💻", document: "📄",
    video: "🎬", audio: "🎵", archive: "📦", other: "📎"
  };
  return icons[type] || "📎";
}


/**
 * Determine backup priority (mirrors backend logic).
 */
function getPriority(fileType, accessCount) {
  if (accessCount > 10) return "high";
  if (fileType === "code" || fileType === "document") return "high";
  if (fileType === "image" && accessCount > 2) return "medium";
  if (fileType === "video" || fileType === "audio") return "medium";
  return "low";
}


/**
 * Escape HTML special characters to prevent XSS.
 */
function escapeHtml(str) {
  const div = document.createElement("div");
  div.appendChild(document.createTextNode(str));
  return div.innerHTML;
}