# Test booking flow
$baseUrl = "http://localhost:8000"
$sessionId = "test-$(Get-Date -Format 'yyyyMMdd-HHmmss')"

Write-Host "Testing booking flow with session: $sessionId" -ForegroundColor Green

# 1. Start
Write-Host "`n1. Starting conversation..." -ForegroundColor Cyan
Invoke-RestMethod -Uri "$baseUrl/chat/message" -Method POST -ContentType "application/json" -Body "{`"session_id`": `"$sessionId`", `"message`": `"Hello, I need an appointment`"}"

Start-Sleep -Seconds 1

# 2. New patient
Write-Host "`n2. New patient..." -ForegroundColor Cyan
Invoke-RestMethod -Uri "$baseUrl/chat/message" -Method POST -ContentType "application/json" -Body "{`"session_id`": `"$sessionId`", `"message`": `"I am a new patient`"}"

Start-Sleep -Seconds 1

# Continue with rest...

# 3. Service
Write-Host "`n3. Service..." -ForegroundColor Cyan
Invoke-RestMethod -Uri "$baseUrl/chat/message" -Method POST -ContentType "application/json" -Body "{`"session_id`": `"$sessionId`", `"message`": `"I need a teeth cleaning`"}"

Start-Sleep -Seconds 1

# 4. Name
Write-Host "`n4. Name..." -ForegroundColor Cyan
Invoke-RestMethod -Uri "$baseUrl/chat/message" -Method POST -ContentType "application/json" -Body "{`"session_id`": `"$sessionId`", `"message`": `"My name is John Smith`"}"

Start-Sleep -Seconds 1

# 5. Phone
Write-Host "`n5. Phone..." -ForegroundColor Cyan
Invoke-RestMethod -Uri "$baseUrl/chat/message" -Method POST -ContentType "application/json" -Body "{`"session_id`": `"$sessionId`", `"message`": `"555-123-4567`"}"

Start-Sleep -Seconds 1

# 6. DOB
Write-Host "`n6. DOB..." -ForegroundColor Cyan
Invoke-RestMethod -Uri "$baseUrl/chat/message" -Method POST -ContentType "application/json" -Body "{`"session_id`": `"$sessionId`", `"message`": `"03/15/1990`"}"

Start-Sleep -Seconds 1

# 7. Insurance
Write-Host "`n7. Insurance..." -ForegroundColor Cyan
Invoke-RestMethod -Uri "$baseUrl/chat/message" -Method POST -ContentType "application/json" -Body "{`"session_id`": `"$sessionId`", `"message`": `"I have Blue Cross`"}"

Start-Sleep -Seconds 1

# 8. Preferred time
Write-Host "`n8. Preferred time..." -ForegroundColor Cyan
Invoke-RestMethod -Uri "$baseUrl/chat/message" -Method POST -ContentType "application/json" -Body "{`"session_id`": `"$sessionId`", `"message`": `"Wednesday morning`"}"

Start-Sleep -Seconds 1

# 9. Specific time
Write-Host "`n9. Specific time..." -ForegroundColor Cyan
Invoke-RestMethod -Uri "$baseUrl/chat/message" -Method POST -ContentType "application/json" -Body "{`"session_id`": `"$sessionId`", `"message`": `"Yes, Wednesday at 10 AM works perfectly`"}"

Start-Sleep -Seconds 1

# 10. Confirm
Write-Host "`n10. Confirm..." -ForegroundColor Cyan
Invoke-RestMethod -Uri "$baseUrl/chat/message" -Method POST -ContentType "application/json" -Body "{`"session_id`": `"$sessionId`", `"message`": `"Yes, that's all correct`"}"

Start-Sleep -Seconds 1

# 11. Final booking
Write-Host "`n11. Final booking..." -ForegroundColor Cyan
Invoke-RestMethod -Uri "$baseUrl/chat/message" -Method POST -ContentType "application/json" -Body "{`"session_id`": `"$sessionId`", `"message`": `"Yes, please book it`"}"

Write-Host "`n✅ Booking test complete!" -ForegroundColor Green
Write-Host "Check Google Sheets for the logged booking data." -ForegroundColor Yellow