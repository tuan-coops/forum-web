document.addEventListener("DOMContentLoaded", async () => {
  const sidebarMenu = document.querySelector(".sidebar_section nav"); // chọn đúng nav trong sidebar_section

  try {
    const response = await fetch(`${API_BASE_URL}/tag/top`);
    const tags = await response.json();

    sidebarMenu.innerHTML = tags.map(tag => `
      <a 
        href="/Frontend/trending-tag/index.html?tag=${encodeURIComponent(tag.name)}" 
        class="tag_item"
      >
        #${tag.name} <span class="count">(${tag.count})</span>
      </a>
    `).join("");
  } catch (err) {
    console.error("❌ Lỗi tải tag nổi bật:", err);
    sidebarMenu.innerHTML = "<p>Không thể tải tag nổi bật</p>";
  }
});
