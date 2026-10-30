# scripts/demo-crud.ps1 – gọi thử CRUD đủ cho 2 thực thể (kỹ thuật viên, lịch hẹn) qua API thật.
# Chạy (backend đang chạy ở cổng 3000):  powershell -ExecutionPolicy Bypass -File scripts\demo-crud.ps1
$ErrorActionPreference = 'Stop'
$Base = 'http://localhost:3000'
$H = @{ 'X-Employee-Id' = '3'; 'X-Role' = 'QUAN_LY'; 'X-Center-Id' = '2' }

function Call($Method, $Path, $Body) {
    $p = @{ Method = $Method; Uri = "$Base$Path"; Headers = $H; ContentType = 'application/json; charset=utf-8' }
    if ($Body) { $p.Body = [Text.Encoding]::UTF8.GetBytes(($Body | ConvertTo-Json -Compress)) }
    try {
        $r = Invoke-RestMethod @p
        Write-Host ("{0,-6} {1,-58} -> OK" -f $Method, $Path) -ForegroundColor Green
        return $r
    } catch {
        $code = [int]$_.Exception.Response.StatusCode
        Write-Host ("{0,-6} {1,-58} -> HTTP {2} {3}" -f $Method, $Path, $code, $_.ErrorDetails.Message) -ForegroundColor Yellow
        return $null
    }
}

Write-Host "`n=== THỰC THỂ 1: KỸ THUẬT VIÊN (E9 – E13) ===" -ForegroundColor Cyan
$t = Call POST '/api/technicians' @{ full_name = 'Trần Văn Mới'; level = 'SO_CAP' }
Write-Host ("       tạo: technician_id = {0}, {1}, {2}, trung tâm {3}" -f $t.technician_id, $t.full_name, $t.level, $t.center_id)
$g = Call GET "/api/technicians/$($t.technician_id)"
$u = Call PUT "/api/technicians/$($t.technician_id)" @{ full_name = 'Trần Văn Mới'; level = 'TRUNG_CAP'; is_active = $true }
Write-Host ("       sửa: bậc = {0}" -f $u.level)
$d = Call DELETE "/api/technicians/$($t.technician_id)"
Write-Host ("       xoá mềm: is_active = {0}" -f $d.is_active)
$all = Call GET '/api/technicians'
Write-Host ("       danh sách trung tâm 2: {0} kỹ thuật viên đang làm việc" -f $all.items.Count)
Write-Host "       -- dữ liệu sai:" -ForegroundColor DarkGray
$null = Call POST '/api/technicians' @{ full_name = 'A'; level = 'XYZ' }

Write-Host "`n=== THỰC THỂ 2: LỊCH HẸN (E5, E14 – E16) ===" -ForegroundColor Cyan
$list = Call GET '/api/tickets?status=MOI'
$ticket = $list.items[0]
$sg = Call GET "/api/tickets/$($ticket.ticket_id)/technician-suggestions"
$as = Call POST "/api/tickets/$($ticket.ticket_id)/assignment" @{ technician_id = $sg.suggestions[0].technician_id }
Write-Host ("       phân công phiếu {0} cho {1}" -f $as.ticket_code, $sg.suggestions[0].full_name)
$day = (Get-Date).AddDays(2); if ($day.DayOfWeek -eq 'Sunday') { $day = $day.AddDays(1) }
$ds = $day.ToString('yyyy-MM-dd')
$a = Call POST "/api/tickets/$($ticket.ticket_id)/appointments" @{ appointment_type = 'TRA_MAY'; start_at = "${ds}T09:00:00+07:00"; end_at = "${ds}T09:30:00+07:00" }
Write-Host ("       tạo: appointment_id = {0}, {1} → {2}, {3}" -f $a.appointment_id, $a.start_at, $a.end_at, $a.status)
$ga = Call GET "/api/appointments/$($a.appointment_id)"
$ua = Call PUT "/api/appointments/$($a.appointment_id)" @{ start_at = "${ds}T10:00:00+07:00"; end_at = "${ds}T10:45:00+07:00" }
Write-Host ("       sửa giờ: {0} → {1}" -f $ua.start_at, $ua.end_at)
$reason = [uri]::EscapeDataString('Khách báo bận, hẹn lại tuần sau')
$ca = Call DELETE "/api/appointments/$($a.appointment_id)?reason=$reason"
Write-Host ("       hủy: status = {0}" -f $ca.status)
Write-Host "       -- hủy lần hai (phải bị từ chối):" -ForegroundColor DarkGray
$null = Call DELETE "/api/appointments/$($a.appointment_id)?reason=$reason"
Write-Host "`nXong. Chạy lại script nhiều lần được (mỗi lần dùng một phiếu MOI khác)." -ForegroundColor Cyan
