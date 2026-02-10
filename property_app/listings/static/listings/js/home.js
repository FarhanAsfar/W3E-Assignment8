const input = document.getElementById("locationInput");
const suggestionsBox = document.getElementById("suggestions");
const searchBtn = document.getElementById("searchBtn");
const resultsEl = document.getElementById("results");
const metaEl = document.getElementById("searchMeta");
const paginationEl = document.getElementById("pagination");

let selectedLocationName = "";
let currentPage = 1;

function escapeHtml(str) {
    return (str || "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function showSuggestions(items) {
    if (!items.length) {
        suggestionsBox.classList.add("hidden");
        suggestionsBox.innerHTML = "";
        return;
    }

    suggestionsBox.innerHTML = items
        .map((loc) => `<div class="suggestion" data-name="${escapeHtml(loc.name)}">${escapeHtml(loc.name)}</div>`)
        .join("");
    suggestionsBox.classList.remove("hidden");
}

async function fetchSuggestions(q) {
    const res = await fetch(`/api/locations/autocomplete/?q=${encodeURIComponent(q)}`);
    const data = await res.json();
    return data.results || [];
}

async function fetchProperties(locationName, page) {
    const url = `/api/properties/?location=${encodeURIComponent(locationName)}&page=${page}`;
    const res = await fetch(url);
    if (!res.ok) {
        const err = await res.json().catch(() => null);
        throw new Error(err?.error?.detail || "Failed to fetch properties");
    }
    return await res.json();
}

function renderProperties(items) {
    resultsEl.innerHTML = items.map((p) => {
        const img = p.primary_image_url
            ? `<img class="card-img" src="${p.primary_image_url}" alt="Primary image">`
            : `<div class="card-img"></div>`;

        return `
      <a class="card" href="/properties/${p.location_slug}/${p.slug}/">
        ${img}
        <div class="card-body">
          <p class="card-title">${escapeHtml(p.title)}</p>
          <p class="card-sub">${escapeHtml(p.address)}, ${escapeHtml(p.country)}</p>
          <p class="card-sub">Location: ${escapeHtml(p.location_name)}</p>
        </div>
      </a>
    `;
    }).join("");
}

function renderPagination(next, previous) {
    paginationEl.innerHTML = "";

    const prevBtn = document.createElement("button");
    prevBtn.className = "page-btn";
    prevBtn.textContent = "Previous";
    prevBtn.disabled = !previous;
    prevBtn.onclick = () => loadPage(currentPage - 1);

    const nextBtn = document.createElement("button");
    nextBtn.className = "page-btn";
    nextBtn.textContent = "Next";
    nextBtn.disabled = !next;
    nextBtn.onclick = () => loadPage(currentPage + 1);

    paginationEl.appendChild(prevBtn);
    paginationEl.appendChild(nextBtn);
}

async function loadPage(page) {
    if (!selectedLocationName) return;
    currentPage = page;
    metaEl.textContent = "Loading...";
    resultsEl.innerHTML = "";
    paginationEl.innerHTML = "";

    try {
        const data = await fetchProperties(selectedLocationName, page);
        metaEl.textContent = `Showing ${data.results.length} results (page ${currentPage}) for "${selectedLocationName}"`;
        renderProperties(data.results);
        renderPagination(data.next, data.previous);
    } catch (e) {
        metaEl.textContent = e.message;
    }
}

let debounceTimer = null;
input.addEventListener("input", () => {
    const q = input.value.trim();
    selectedLocationName = ""; // reset until user selects or searches

    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(async () => {
        if (q.length < 3) {
            showSuggestions([]);
            return;
        }
        try {
            const items = await fetchSuggestions(q);
            showSuggestions(items);
        } catch {
            showSuggestions([]);
        }
    }, 250);
});

input.addEventListener("keydown", (e) => {
    if (e.key !== "Enter") return;

    e.preventDefault();

    const first = suggestionsBox.querySelector(".suggestion");
    if (first) {
        const name = first.getAttribute("data-name");
        input.value = name;
        selectedLocationName = name;
    } else {
        selectedLocationName = q;
    }
    showSuggestions([]);
    loadPage(1);
});


suggestionsBox.addEventListener("click", (e) => {
    const el = e.target.closest(".suggestion");
    if (!el) return;
    const name = el.getAttribute("data-name");
    input.value = name;
    selectedLocationName = name;
    showSuggestions([]);
    loadPage(1);
});

document.addEventListener("click", (e) => {
    // Clicking outside suggestions closes it
    if (!suggestionsBox.contains(e.target) && e.target !== input) {
        showSuggestions([]);
    }
});

searchBtn.addEventListener("click", () => {
    const q = input.value.trim();
    if (q.length < 1) {
        metaEl.textContent = "Type a location name first.";
        return;
    }
    selectedLocationName = q;
    loadPage(1);
});
