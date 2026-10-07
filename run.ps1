Write-Host "`n Đang khởi động Multi-Provider AI Chatbot..." -ForegroundColor Cyan
docker compose up -d

Write-Host "`n========================================================" -ForegroundColor Green
Write-Host "Hệ thống đã khởi động thành công!" -ForegroundColor Green
Write-Host "========================================================`n" -ForegroundColor Green

Start-Process "http://localhost:5173"
