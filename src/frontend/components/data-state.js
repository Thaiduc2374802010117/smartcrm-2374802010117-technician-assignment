// components/data-state.js – bọc một vùng màn hình bằng ba trạng thái: đang tải · rỗng · lỗi.
// Cách dùng: await withDataState(container, loadFn, renderFn, { isEmpty, emptyText })
export function showLoading(container, text = 'Đang tải dữ liệu…') {
  container.innerHTML = `<div class="state state-loading" role="status"><span class="spinner"></span>${text}</div>`;
}

export function showEmpty(container, text) {
  container.innerHTML = `<div class="state state-empty">${text}</div>`;
}

export function showError(container, error, onRetry) {
  container.innerHTML = `<div class="state state-error" role="alert">
      <strong>Không tải được dữ liệu.</strong> <span class="msg"></span>
      ${onRetry ? '<button type="button" class="btn retry">Thử lại</button>' : ''}</div>`;
  container.querySelector('.msg').textContent = error.message;
  if (onRetry) container.querySelector('.retry').addEventListener('click', onRetry);
}

export async function withDataState(container, loadFn, renderFn, { isEmpty = () => false, emptyText = 'Không có dữ liệu' } = {}) {
  const run = async () => {
    showLoading(container);
    try {
      const data = await loadFn();
      if (isEmpty(data)) showEmpty(container, emptyText);
      else renderFn(data);
      return data;
    } catch (e) {
      showError(container, e, run);
      return null;
    }
  };
  return run();
}
