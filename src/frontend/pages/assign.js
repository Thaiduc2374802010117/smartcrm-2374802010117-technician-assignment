// M2 – Phân công kỹ thuật viên (UC2 · US2, US3 · E2, E3). Mỗi luồng ngoại lệ có thông báo riêng.
import { assignTechnician, getSuggestions } from '../api/tickets.api.js';
import { withDataState } from '../components/data-state.js';
import { esc, fmt, notify, requireLogin } from '../components/layout.js';

requireLogin();
const ticketId = Number(new URLSearchParams(location.search).get('ticket'));
const content = document.getElementById('content');
const notice = document.getElementById('notice');

function render(data) {
  const t = data.ticket;
  const rows = data.suggestions.map((s, i) => `<tr><td><input type="radio" name="tech" value="${s.technician_id}" ${i === 0 ? 'checked' : ''}></td>
    <td>${esc(s.full_name)}</td><td>${esc(s.level)}</td><td>${s.proficiency}</td><td>${s.open_ticket_count}</td></tr>`).join('');
  content.innerHTML = `<div class="card"><b>Phiếu bảo hành ${esc(t.ticket_code)}</b><br>
      <span class="muted">Nhóm sự cố:</span> ${esc(t.category_name)} · <span class="muted">Mức ưu tiên:</span> ${esc(t.priority)} ·
      <span class="muted">Hạn cam kết:</span> ${fmt(t.due_date)} · <span class="muted">Trạng thái phiếu:</span> <span class="tag tag-status">${esc(t.status)}</span><br>
      <span class="muted">Mô tả lỗi:</span> ${esc(t.issue_desc)}</div>
    <h2>Gợi ý kỹ thuật viên (tối đa 3)</h2>
    ${data.suggestions.length ? `<table><thead><tr><th></th><th>Kỹ thuật viên</th><th>Bậc</th><th>Tay nghề (1–5)</th><th>Số phiếu đang mở</th></tr></thead>
      <tbody>${rows}</tbody></table>
      <p><button class="btn primary" id="assign" ${t.status !== 'MOI' ? 'disabled' : ''}>Phân công</button>
      <a class="btn" href="tickets.html">Hủy</a></p>`
      : `<div class="state state-empty">${esc(data.message || 'Không có kỹ thuật viên đủ tay nghề tại trung tâm')}</div>`}`;   // UC2 – 3a
  if (t.status !== 'MOI') notify(notice, 'error', `Phiếu đang ở trạng thái <b>${esc(t.status)}</b>, không phân công lại được.`);
  const btn = document.getElementById('assign');
  if (btn) btn.addEventListener('click', () => onAssign(btn, t));
}

async function onAssign(btn, ticket) {
  const chosen = content.querySelector('input[name=tech]:checked');
  if (!chosen) return;
  btn.disabled = true;
  try {
    const r = await assignTechnician(ticketId, Number(chosen.value));
    const name = chosen.closest('tr').children[1].textContent;
    content.querySelector('.tag-status').textContent = r.status;   // MOI → DA_PHAN_CONG
    notify(notice, 'ok', `Đã phân công phiếu <b>${esc(r.ticket_code)}</b> cho <b>${esc(name)}</b> lúc ${fmt(r.assigned_at)}.
      <a class="btn primary small" href="appointment.html?ticket=${ticketId}&technician=${r.technician_id}&code=${encodeURIComponent(r.ticket_code)}">Đặt lịch hẹn →</a>`);
  } catch (e) {
    btn.disabled = false;
    if (e.code === 'INVALID_STATE') notify(notice, 'error', `Phiếu đã được phân công, không ghi đè. ${esc(e.message)}`);            // 5a
    else if (e.code === 'TECHNICIAN_NOT_ELIGIBLE') {                                                                                 // 5b
      notify(notice, 'error', 'Kỹ thuật viên không còn đủ điều kiện – danh sách gợi ý đã được tải lại.');
      load();
    } else notify(notice, 'error', `Lưu không thành công, vui lòng thử lại. (${esc(e.message)})`);                                  // 6a
  }
}

function load() {
  return withDataState(content, () => getSuggestions(ticketId), render);
}
load();
