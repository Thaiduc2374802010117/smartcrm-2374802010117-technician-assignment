# data/official – Dataset Smart CRM chính thức

Tải **Mekong Mobile – Dataset Smart CRM** trong mục "Case Study: Mekong Mobile & Đề Bài Tập" trên VLU E-learning,
giải nén để có các file sau ngay trong thư mục này:

- `technicians.csv` – kỹ thuật viên, bậc, trung tâm (khoảng 38 dòng)
- `technician_skills.csv` – tay nghề theo nhóm sự cố (khoảng 152 dòng)
- `tickets_history.csv` – phiếu bảo hành lịch sử (khoảng 7.800 dòng)

Sau đó chạy (từ thư mục gốc repo): `python -m src.backend.seed_dataset --data data/official --reopen 5`
