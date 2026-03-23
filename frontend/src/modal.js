// ─── Modal System ─────────────────────────────────────────────

export function showModal({
  type = "info",
  title = "",
  message = "",
  confirmText = "OK",
  cancelText = null,
}) {
  return new Promise((resolve) => {
    const overlay = document.createElement("div");
    overlay.className = "modal-overlay";

    const iconMap = {
      success: "✓",
      danger: "!",
      warning: "!",
      info: "i",
    };

    overlay.innerHTML = `
      <div class="modal-card modal-card--${type}">
        <div class="modal-header">
          <div class="modal-icon modal-icon--${type}">
            ${iconMap[type] || "i"}
          </div>
          <div class="modal-title">${title}</div>
        </div>

        <div class="modal-body">${message}</div>

        <div class="modal-actions">
          ${
            cancelText
              ? `<button class="secondary modal-cancel">${cancelText}</button>`
              : ""
          }
          <button class="${type === "danger" ? "danger" : ""} modal-confirm">
            ${confirmText}
          </button>
        </div>
      </div>
    `;

    document.body.appendChild(overlay);

    const confirmBtn = overlay.querySelector(".modal-confirm");
    const cancelBtn = overlay.querySelector(".modal-cancel");

    function close(result) {
      overlay.remove();
      resolve(result);
    }

    confirmBtn.onclick = () => close(true);
    cancelBtn && (cancelBtn.onclick = () => close(false));

    // click outside to close (optional)
    overlay.onclick = (e) => {
      if (e.target === overlay) close(false);
    };
  });
}