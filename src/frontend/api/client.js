// api/client.js – NƠI DUY NHẤT gọi fetch() trong giao diện.
// Gắn thông tin người dùng giả lập (W8) vào header, đổi lỗi HTTP thành ApiError theo cấu trúc API contract:
// { "error": { "code", "message", "fields" } }. Nhận 401 thì xoá người dùng và về trang đăng nhập.
import { API_BASE } from './config.js';

const USER_KEY = 'smartcrm_user';
const LOGIN_PAGE = new URL('../index.html', import.meta.url).href;   // trang đăng nhập ở thư mục gốc giao diện

export class ApiError extends Error {
  constructor(status, code, message, fields = {}) {
    super(message);
    this.status = status;   // 0 = không kết nối được máy chủ
    this.code = code;
    this.fields = fields;
  }
}

export function getUser() {
  try { return JSON.parse(localStorage.getItem(USER_KEY)); } catch { return null; }
}

export function saveUser(user) {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function logout() {
  localStorage.removeItem(USER_KEY);
  window.location.href = LOGIN_PAGE;
}

export async function request(path, { method = 'GET', body } = {}) {
  const user = getUser();
  if (!user) { logout(); throw new ApiError(401, 'UNAUTHENTICATED', 'Chưa đăng nhập'); }
  let response;
  try {
    response = await fetch(API_BASE + path, {
      method,
      headers: {
        'Content-Type': 'application/json',
        'X-Employee-Id': String(user.employee_id),
        'X-Role': user.role,
        'X-Center-Id': String(user.center_id),
      },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new ApiError(0, 'NETWORK', 'Không kết nối được máy chủ. Kiểm tra backend đã chạy chưa rồi bấm Thử lại.');
  }
  const data = await response.json().catch(() => null);
  if (response.status === 401) { logout(); throw new ApiError(401, 'UNAUTHENTICATED', 'Phiên đăng nhập không hợp lệ'); }
  if (!response.ok) {
    const e = (data && data.error) || {};
    throw new ApiError(response.status, e.code || `HTTP_${response.status}`, e.message || 'Máy chủ gặp lỗi', e.fields || {});
  }
  return data;
}
