// M3 – Đặt lịch hẹn giao – nhận máy (UC4 · US5 · E4, E5). Ngoại lệ 1a, 4a, 5a hiển thị ở vùng thông báo.
import { createAppointment, listTechnicianAppointments } from '../api/appointments.api.js';
import { withDataState } from '../components/data-state.js';
import { esc, fmt, fmtTime, notify, requireLogin } from '../components/layout.js';

requireLogin();
const params = new URLSearchParams(location.search);
const ticketId = Number(params.get('ticket'));
const technicianId = Number(params.get('technician'));
document.getElementById('code').textContent = params.get('code') ? `· phiếu ${params.get('code')}` : '';
const schedule = document.getElementById('schedule');
const notice = document.getElementById('notice');
const form = document.getElementById('form');

const tomorrow = new Date(Date.now() + 86400000);
if (new Date(tomorrow.toLocaleString('en-US', { timeZone: 'Asia/Ho_Chi_Minh' })).getDay() === 0) tomorrow.setDate(tomorrow.getDate() + 1);   // bỏ qua Chủ nhật
form.date.value = tomorrow.toLocaleDateString('sv-SE', { timeZone: 'Asia/Ho_Chi_Minh' });   // YYYY-MM-DD theo giờ VN

const iso = (date, time) => `${date}T${time}:00+07:00`;                          // giờ Việt Nam, ISO 8601

function loadSchedule() {
  const from = new Date();
  const to = new Date(from.getTime() + 7 * 86400000);
  return withDataState(schedule, () => listTechnicianAppointments(technicianId, from, to), (d) => {
    document.getElementById('tname').textContent = d.full_name;
    schedule.innerHTML = `<table><thead><tr><th>Bắt đầu – Kết thúc</th><th>Loại lịch hẹn</th><th>Mã phiếu</th></tr></thead><tbody>
      ${d.items.map((a) => `<tr><td>${fmt(a.start_at)} – ${fmtTime(a.end_at)}</td><td>${esc(a.appointment_type)}</td><td>${esc(a.ticket_code)}</td></tr>`).join('')}</tbody></table>`;
  }, { isEmpty: (d) => { document.getElementById('tname').textContent = d.full_name; return d.items.length === 0; },
       emptyText: 'Kỹ thuật viên chưa có lịch hẹn nào trong 7 ngày tới.' });
}

form.addEventListener('submit', async (ev) => {
  ev.preventDefault();
  const btn = form.querySelector('button[type=submit]');
  btn.disabled = true;
  try {
    const a = await createAppointment(ticketId, {
      appointmentType: form.type.value, startAt: iso(form.date.value, form.start.value),
      endAt: iso(form.date.value, form.end.value), note: form.note.value,
    });
    notify(notice, 'ok', `Đã lưu lịch hẹn <b>${esc(a.appointment_type)}</b> ${fmt(a.start_at)} – ${fmtTime(a.end_at)} (trạng thái ${esc(a.status)}). Báo khách theo thông tin này.`);
    loadSchedule();
  } catch (e) {
    if (e.code === 'TICKET_NOT_ASSIGNED')                                                                           // 1a
      notify(notice, 'error', `Phiếu chưa được phân công. <a href="assign.html?ticket=${ticketId}">Đến màn hình Phân công</a>`);
    else if (e.code === 'APPOINTMENT_CONFLICT')                                                                     // 5a
      notify(notice, 'error', `Kỹ thuật viên đã có lịch hẹn ${fmt(e.fields.conflict_start_at)} – ${fmtTime(e.fields.conflict_end_at)}.
        Khung giờ trống gần nhất: <b>${fmtTime(e.fields.suggested_start_at)}</b>.`);
    else if (e.code === 'VALIDATION_FAILED')                                                                        // 4a
      notify(notice, 'error', `Khung giờ không hợp lệ: ${esc(Object.values(e.fields).join('; '))}`);
    else notify(notice, 'error', `Lưu không thành công: ${esc(e.message)}`);
  } finally {
    btn.disabled = false;
  }
});

loadSchedule();
