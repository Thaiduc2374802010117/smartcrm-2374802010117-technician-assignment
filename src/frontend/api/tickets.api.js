// api/tickets.api.js – hàm gọi API phiếu bảo hành (E1, E2, E3 trong docs/api-contract.md).
import { request } from './client.js';

/** E1 – danh sách phiếu chờ phân công, sắp theo hạn cam kết. */
export function listNewTickets({ categoryId, priority, page = 1, size = 20 } = {}) {
  const q = new URLSearchParams({ status: 'MOI', page, size });
  if (categoryId) q.set('category_id', categoryId);
  if (priority) q.set('priority', priority);
  return request(`/api/tickets?${q}`);
}

/** E2 – thông tin phiếu và tối đa 3 kỹ thuật viên gợi ý. */
export function getSuggestions(ticketId) {
  return request(`/api/tickets/${ticketId}/technician-suggestions`);
}

/** E3 – phân công phiếu cho một kỹ thuật viên. */
export function assignTechnician(ticketId, technicianId) {
  return request(`/api/tickets/${ticketId}/assignment`, { method: 'POST', body: { technician_id: technicianId } });
}
