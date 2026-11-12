// Auto-dismiss alerts after 4 seconds
document.addEventListener("DOMContentLoaded", () => {
  setTimeout(() => {
    document.querySelectorAll(".alert").forEach(el => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
      bsAlert.close();
    });
  }, 4000);
});

// ── Sidebar toggle ───────────────────────────────────────────
function openSidebar() {
  document.getElementById('sidebar').classList.add('open');
  document.getElementById('sidebarOverlay').classList.add('active');
  document.body.style.overflow = 'hidden';
}
function closeSidebar() {
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('sidebarOverlay').classList.remove('active');
  document.body.style.overflow = '';
}

// Close sidebar on ESC key
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeSidebar();
});

// Set active topbar title from the active sidebar link
document.addEventListener('DOMContentLoaded', () => {
  const titleEl = document.getElementById('topbar-page-title');
  if (!titleEl) return;
  const active = document.querySelector('.sidebar-link.active span');
  if (active) titleEl.textContent = active.textContent.trim();
});
