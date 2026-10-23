// M1 – Danh sách phiếu chờ phân công (UC1, US1, E1). Không gọi fetch trực tiếp – dùng tickets.api.js.
import { listNewTickets } from '../api/tickets.api.js';
import { withDataState } from '../components/data-state.js';
import { CATEGORIES, esc, fmt, requireLogin } from '../components/layout.js';

requireLogin();
const list = document.getElementById('list');
const pager = document.getElementById('pager');
const categorySel = document.getElementById('category');
Object.entries(CATEGORIES).forEach(([id, name]) => categorySel.add(new Option(name, id)));
let page = 1;

function warn(t) {
  if (t.is_overdue) return '<span class="tag tag-over">Quá hạn</span>';
  if (t.is_due_soon) return '<span class="tag tag-soon">Sắp quá hạn</span>';
  return '';
}

function render(data) {
  list.innerHTML = `<table><thead><tr><th>Mã phiếu</th><th>Nhóm sự cố</th><th>Mức ưu tiên</th><th>Thời điểm tiếp nhận</th>
    <th>Hạn cam kết ▲</th><th>Cảnh báo</th><th></th></tr></thead><tbody>${data.items.map((t) => `<tr>
    <td>${esc(t.ticket_code)}</td><td>${esc(t.category_name)}</td><td>${esc(t.priority)}</td><td>${fmt(t.received_at)}</td>
    <td>${fmt(t.due_date)}</td><td>${warn(t)}</td>
    <td><a class="btn primary small" href="assign.html?ticket=${t.ticket_id}">Phân công</a></td></tr>`).join('')}</tbody></table>`;
  const pages = Math.max(1, Math.ceil(data.total / data.size));
  pager.innerHTML = `<span class="muted">Tổng ${data.total} phiếu · Trang ${data.page} / ${pages}</span>
    <button class="btn small" id="prev" ${data.page <= 1 ? 'disabled' : ''}>‹ Trước</button>
    <button class="btn small" id="next" ${data.page >= pages ? 'disabled' : ''}>Sau ›</button>`;
  pager.querySelector('#prev').onclick = () => { page -= 1; load(); };
  pager.querySelector('#next').onclick = () => { page += 1; load(); };
}

function load() {
  pager.innerHTML = '';
  return withDataState(list,
    () => listNewTickets({ categoryId: categorySel.value, priority: document.getElementById('priority').value, page }),
    render,
    { isEmpty: (d) => d.items.length === 0, emptyText: 'Không có phiếu chờ phân công.' });
}

document.getElementById('filter').addEventListener('click', () => { page = 1; load(); });
load();
