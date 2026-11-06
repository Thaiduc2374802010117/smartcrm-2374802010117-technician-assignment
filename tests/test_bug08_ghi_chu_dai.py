"""Hồi quy BUG-08: sửa giờ lịch hẹn với ghi chú > 255 ký tự phải trả lỗi kiểm tra dữ liệu, không để CSDL báo lỗi (500)."""
import pytest

from src.backend.services.appointment_service import AppointmentService
from src.backend.services.errors import ValidationFailed
from tests.test_appointment_service import NOW, SAT, FakeUowAppt, User, at


def test_bug08_ghi_chu_300_ky_tu_bi_tu_choi_truoc_khi_ghi():
    with pytest.raises(ValidationFailed) as e:
        AppointmentService(FakeUowAppt()).reschedule(7, at(SAT, 14), at(SAT, 14, 30), "x" * 300, User(), now=NOW)
    assert "note" in e.value.fields


def test_bug08_ghi_chu_dung_255_ky_tu_van_hop_le():                                     # biên
    r = AppointmentService(FakeUowAppt()).reschedule(7, at(SAT, 14), at(SAT, 14, 30), "x" * 255, User(), now=NOW)
    assert r["start_at"] == at(SAT, 14)
