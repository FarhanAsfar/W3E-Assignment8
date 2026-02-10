const detailEl = document.getElementById("detail");

function escapeHtml(str) {
  return (str || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

async function fetchDetail(id) {
  const res = await fetch(`/api/properties/${id}/`);
  if (!res.ok) {
    const err = await res.json().catch(() => null);
    throw new Error(err?.error?.detail || "Failed to fetch property details");
  }
  return await res.json();
}

function renderGallery(images) {
  if (!images || !images.length) return "<p class='meta'>No images available.</p>";

  const primary = images.find(i => i.is_primary) || images[0];
  const others = images.filter(i => i !== primary);

  const primaryHtml = primary.image_url
    ? `<img class="card-img" style="height:340px;border-radius:12px;" src="${primary.image_url}" alt="${escapeHtml(primary.alt_text)}">`
    : "";

  const thumbs = others.map(img => {
    if (!img.image_url) return "";
    return `<img class="card-img" style="height:120px;border-radius:12px;" src="${img.image_url}" alt="${escapeHtml(img.alt_text)}">`;
  }).join("");

  return `
    <div style="display:grid; gap:12px;">
      ${primaryHtml}
      <div class="grid">${thumbs}</div>
    </div>
  `;
}

async function init() {
  detailEl.innerHTML = "<p class='meta'>Loading...</p>";
  try {
    const p = await fetchDetail(PROPERTY_ID);

    detailEl.innerHTML = `
      <div class="card" style="padding:14px;">
        <h1 style="margin:0 0 8px;">${escapeHtml(p.title)}</h1>
        <p class="meta" style="margin:0 0 12px;">
          ${escapeHtml(p.address)}, ${escapeHtml(p.country)} •
          Location: ${escapeHtml(p.location?.name || "")}
        </p>

        ${renderGallery(p.images)}

        <h3 style="margin:16px 0 6px;">Description</h3>
        <p style="margin:0; color: var(--muted);">${escapeHtml(p.description || "No description")}</p>
      </div>
    `;
  } catch (e) {
    detailEl.innerHTML = `<p class="meta">${escapeHtml(e.message)}</p>`;
  }
}

init();
