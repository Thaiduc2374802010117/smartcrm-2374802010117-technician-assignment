// api/appointments.api.js – hàm gọi API lịch hẹn (E4, E5 trong docs/api-contract.md).
import { request } from './client.js';

/** E4 – lịch hẹn DA_HEN của kỹ thuật viên trong khoảng [from, to). */
export function listTechnicianAppointments(technicianId, from, to) {
  const q = new URLSearchParams({ from: from.toISOString(), to: to.toISOString() });
  return request(`/api/technicians/${technicianId}/appointments?${q}`);
}

/** E5 – tạo lịch hẹn giao máy / trả máy cho phiếu. */
export function createAppointment(ticketId, { appointmentType, startAt, endAt, note }) {
  return request(`/api/tickets/${ticketId}/appointments`, {
    method: 'POST',
    body: { appointment_type: appointmentType, start_at: startAt, end_at: endAt, note: note || null },
  });
}
