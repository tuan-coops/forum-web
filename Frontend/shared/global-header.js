document.addEventListener('DOMContentLoaded', async () => {
    const avatarEl = document.querySelector(".profile_placeholder");
    const userId = localStorage.getItem("user_id");
    const token = localStorage.getItem("token");

    if (!avatarEl) return;

    // ✅ Nếu chưa đăng nhập
    if (!userId || !token || userId === "undefined" || token === "undefined") {
        avatarEl.style.backgroundImage = "url('/Frontend/profile-page/placeholder_avatar.png')";
        avatarEl.style.backgroundSize = "cover";
        avatarEl.style.borderRadius = "50%";
        return;
    }

    try {
        const res = await fetch(`${API_BASE_URL}/profile/${userId}`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        if (!res.ok) throw new Error("Không tải được avatar");

        const data = await res.json();
        let avatarUrl = data.avatar;
        if (avatarUrl && !avatarUrl.startsWith("http")) {
            avatarUrl = `${API_BASE_URL}/static/uploads/${avatarUrl}`;
        }

        const placeholder = "/Frontend/profile-page/placeholder_avatar.png";
        avatarEl.style.backgroundImage = `url('${avatarUrl || placeholder}')`;
        avatarEl.style.backgroundSize = "cover";
        avatarEl.style.backgroundPosition = "center";
        avatarEl.style.borderRadius = "50%";
        avatarEl.style.width = "36px";
        avatarEl.style.height = "36px";
        avatarEl.style.border = "2px solid #8e44ad";
        avatarEl.style.boxShadow = "0 2px 6px rgba(0,0,0,0.15)";
        avatarEl.style.cursor = "pointer";

    } catch (err) {
        console.error("🚨 Lỗi khi tải avatar:", err);
    }
});
window.addEventListener("scroll", () => {
  if (window.scrollY > 10) document.body.classList.add("scrolled");
  else document.body.classList.remove("scrolled");
});
