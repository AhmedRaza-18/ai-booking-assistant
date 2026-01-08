# Test SMS booking confirmation
# This test will send a real SMS to the provided phone number
$baseUrl = "http://localhost:8000"

# Generate unique session ID with timestamp
$sessionId = "sms-test-$(Get-Date -Format 'yyyyMMddHHmmss')"

Write-Host "🔔 TESTING SMS BOOKING CONFIRMATION" -ForegroundColor Magenta
Write-Host "⚠️  This will send a real SMS to the phone number provided!" -ForegroundColor Yellow
Write-Host "Session ID: $sessionId" -ForegroundColor Yellow
Write-Host "=" * 60 -ForegroundColor Magenta

# 1. Start
Write-Host "`n1. Starting conversation..." -ForegroundColor Cyan
Invoke-RestMethod -Uri "$baseUrl/chat/message" -Method POST -ContentType "application/json" -Body "{`"session_id`": `"$sessionId`", `"message`": `"Hi I need an appointment`"}"

Start-Sleep -Seconds 2

# 2. New patient
Write-Host "`n2. New patient..." -ForegroundColor Cyan
Invoke-RestMethod -Uri "$baseUrl/chat/message" -Method POST -ContentType "application/json" -Body "{`"session_id`": `"$sessionId`", `"message`": `"I am a new patient`"}"

Start-Sleep -Seconds 2

# 3. Service
Write-Host "`n3. Service..." -ForegroundColor Cyan
Invoke-RestMethod -Uri "$baseUrl/chat/message" -Method POST -ContentType "application/json" -Body "{`"session_id`": `"$sessionId`", `"message`": `"I need a cleaning`"}"

Start-Sleep -Seconds 2

# 4. Timing
Write-Host "`n4. Timing..." -ForegroundColor Cyan
Invoke-RestMethod -Uri "$baseUrl/chat/message" -Method POST -ContentType "application/json" -Body "{`"session_id`": `"$sessionId`", `"message`": `"Next week`"}"

Start-Sleep -Seconds 2

# 5. Name
Write-Host "`n5. Name..." -ForegroundColor Cyan
Invoke-RestMethod -Uri "$baseUrl/chat/message" -Method POST -ContentType "application/json" -Body "{`"session_id`": `"$sessionId`", `"message`": `"Ahmed Khan`"}"

Start-Sleep -Seconds 2

# 6. Phone - USE YOUR REAL NUMBER IN INTERNATIONAL FORMAT
Write-Host "`n6. Phone (SMS will be sent here)..." -ForegroundColor Cyan
Invoke-RestMethod -Uri "$baseUrl/chat/message" -Method POST -ContentType "application/json" -Body "{`"session_id`": `"$sessionId`", `"message`": `"+923124660742`"}"

Start-Sleep -Seconds 2

# 7. DOB
Write-Host "`n7. DOB..." -ForegroundColor Cyan
Invoke-RestMethod -Uri "$baseUrl/chat/message" -Method POST -ContentType "application/json" -Body "{`"session_id`": `"$sessionId`", `"message`": `"05/20/1995`"}"

Start-Sleep -Seconds 2

# 8. Insurance
Write-Host "`n8. Insurance..." -ForegroundColor Cyan
Invoke-RestMethod -Uri "$baseUrl/chat/message" -Method POST -ContentType "application/json" -Body "{`"session_id`": `"$sessionId`", `"message`": `"Cash`"}"

Start-Sleep -Seconds 2

# 9. Confirm
Write-Host "`n9. Confirm details..." -ForegroundColor Cyan
Invoke-RestMethod -Uri "$baseUrl/chat/message" -Method POST -ContentType "application/json" -Body "{`"session_id`": `"$sessionId`", `"message`": `"Yes correct`"}"

Start-Sleep -Seconds 2

# 10. Time
Write-Host "`n10. Preferred time..." -ForegroundColor Cyan
Invoke-RestMethod -Uri "$baseUrl/chat/message" -Method POST -ContentType "application/json" -Body "{`"session_id`": `"$sessionId`", `"message`": `"Monday morning`"}"

Start-Sleep -Seconds 2

# 11. Book it (SMS will be sent!)
Write-Host "`n11. Book it (SMS will be sent!)..." -ForegroundColor Green
$finalResponse = Invoke-RestMethod -Uri "$baseUrl/chat/message" -Method POST -ContentType "application/json" -Body "{`"session_id`": `"$sessionId`", `"message`": `"Yes book it`"}"

Write-Host "`n" + "=" * 60 -ForegroundColor Magenta
Write-Host "✅ SMS TEST COMPLETE" -ForegroundColor Green
Write-Host "📱 Check your phone for the confirmation SMS!" -ForegroundColor Green
Write-Host "📊 Also check Google Sheets for the booking record" -ForegroundColor Green
Write-Host "Final State: $($finalResponse.state)" -ForegroundColor Yellow
Write-Host "=" * 60 -ForegroundColor Magenta