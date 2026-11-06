"""Hồi quy BUG-09: header định danh ngoài phạm vi cột CSDL phải bị từ chối 401 ở lớp trình bày, không để CSDL báo lỗi (500)."""
import pytest

from src.backend.api.auth import current_user
from src.backend.api.errors import Unauthenticated


@pytest.mark.parametrize("emp, center", [("99999999999999999999", "2"), ("3", "99999999999"), ("0", "2"), ("-5", "2")])
def test_bug09_header_ngoai_pham_vi_bi_tu_choi(emp, center):
    with pytest.raises(Unauthenticated):
        current_user(emp, "QUAN_LY", center)


def test_bug09_gia_tri_bien_hop_le_van_qua():                                          # biên trên của BIGINT / INT
    u = current_user(str(2**63 - 1), "QUAN_LY", str(2**31 - 1))
    assert u.employee_id == 2**63 - 1 and u.center_id == 2**31 - 1
