// api/config.js – địa chỉ backend.
// Chạy cục bộ / docker compose: giao diện ở cổng 5500, backend ở cổng 3000 (TD-11).
// Bản deploy (Render): backend phục vụ luôn giao diện ở /app → gọi API cùng địa chỉ (TD-20).
export const API_BASE = location.pathname.startsWith('/app/') ? location.origin : 'http://localhost:3000';
