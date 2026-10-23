// components/layout.js – thanh trên cùng (trung tâm, người dùng, đăng xuất) và tiện ích định dạng.
import { getUser, logout } from '../api/client.js';

export const CATEGORIES = { 1: 'MAN_HINH', 2: 'PIN', 3: 'SAC', 4: 'PHAN_MEM', 5: 'NUOC_VAO', 6: 'KHAC' };

export function requireLogin() {
  const user = getUser();
  if (!user) { logout(); return null; }
  const bar = document.querySelector('.topbar');
  if (bar) {
    bar.innerHTML = `<span>Smart CRM · Trung tâm bảo hành mã <b>${user.center_id}</b></span>
      <span>Quản lý trung tâm: <b class="uname"></b> <button type="button" class="btn small" id="logout">Đăng xuất</button></span>`;
    bar.querySelector('.uname').textContent = user.full_name || `Mã NV ${user.employee_id}`;
    bar.querySelector('#logout').addEventListener('click', logout);
  }
  return user;
}

const TZ = 'Asia/Ho_Chi_Minh';   // luôn hiển thị giờ Việt Nam, không phụ thuộc múi giờ của máy

/** Ngày giờ dạng 24/10/2026 09:00 */
export function fmt(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return `${d.toLocaleDateString('vi-VN', { timeZone: TZ, day: '2-digit', month: '2-digit', year: 'numeric' })} ${fmtTime(iso)}`;
}

/** Chỉ giờ dạng 09:00 */
export function fmtTime(iso) {
  if (!iso) return '';
  return new Date(iso).toLocaleTimeString('vi-VN', { timeZone: TZ, hour: '2-digit', minute: '2-digit', hour12: false });
}

export function esc(text) {
  const d = document.createElement('div');
  d.textContent = text == null ? '' : String(text);
  return d.innerHTML;
}

/** Vùng thông báo: type = 'ok' | 'error' */
export function notify(box, type, html) {
  box.className = `notice notice-${type}`;
  box.innerHTML = html;
  box.hidden = false;
}
