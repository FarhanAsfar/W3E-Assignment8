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
  if (!images || !images.length) {
    return "<p class='meta'>No images available.</p>";
  }

  const primary = images.find(i => i.is_primary) || images[0];
  const others = images.filter(i => i !== primary);

  const mainImage = primary.image_url
    ? `<img id="mainImage" class="main-image" src="${primary.image_url}" alt="${escapeHtml(primary.alt_text)}">`
    : "";

  const thumbs = images.map(img => {
    if (!img.image_url) return "";
    return `
      <img 
        class="thumb-image ${img === primary ? "active" : ""}" 
        src="${img.image_url}" 
        alt="${escapeHtml(img.alt_text)}"
        data-src="${img.image_url}"
      >
    `;
  }).join("");

  return `
    <div class="gallery">
      <div class="main-image-wrapper">
        ${mainImage}
      </div>

      <div class="thumbs-wrapper">
        ${thumbs}
      </div>
    </div>
  `;
}

function attachGalleryEvents() {
  const gallery = document.querySelector(".gallery");
  const mainImage = document.getElementById("mainImage");
  if (!gallery || !mainImage) return;

  // One listener handles all thumbnail clicks, even if DOM changes later.
  gallery.addEventListener("click", (e) => {
    const thumb = e.target.closest(".thumb-image");
    if (!thumb) return;

    const newSrc = thumb.getAttribute("data-src");
    if (!newSrc) return;

    mainImage.src = newSrc;

    gallery.querySelectorAll(".thumb-image").forEach(t => t.classList.remove("active"));
    thumb.classList.add("active");
  });
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
    attachGalleryEvents();
  } catch (e) {
    detailEl.innerHTML = `<p class="meta">${escapeHtml(e.message)}</p>`;
  }
}

init();
