$baseUrl = "http://localhost:8080"

Write-Host "`n=== Testing /tools endpoint ===" -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/tools" -Method Get
    Write-Host "Success! Available tools:" -ForegroundColor Green
    $response.tools | ForEach-Object { Write-Host "- $_" }
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}

Write-Host "`n=== Testing /call_tool endpoint ===" -ForegroundColor Cyan
try {
    $body = @{
        name = "add"
        args = @(2, 3)
        kwargs = @{}
    } | ConvertTo-Json
    $response = Invoke-RestMethod -Uri "$baseUrl/call_tool" -Method Post -Body $body -ContentType "application/json"
    Write-Host "Success! Result of add(2, 3): $($response.result)" -ForegroundColor Green
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}

Write-Host "`n=== Testing /chat endpoint with Ollama ===" -ForegroundColor Cyan
try {
    $body = @{
        provider = "ollama"
        messages = @(
            @{
                role = "user"
                content = "Hello, please give a very brief response."
            }
        )
        profile = "concise"
    } | ConvertTo-Json
    $response = Invoke-RestMethod -Uri "$baseUrl/chat" -Method Post -Body $body -ContentType "application/json"
    Write-Host "Success! Response from Ollama:" -ForegroundColor Green
    if ($response.choices) {
        Write-Host $response.choices[0].message.content
    } else {
        Write-Host ($response | ConvertTo-Json -Depth 3)
    }
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}

# Optional: Test with OpenAI if API key is available
$env:OPENAI_API_KEY = (Get-Content -Path ".env" -ErrorAction SilentlyContinue | Where-Object { $_ -match "OPENAI_API_KEY" } | ForEach-Object { $_.Split("=")[1] })
if ($env:OPENAI_API_KEY) {
    Write-Host "`n=== Testing /chat endpoint with OpenAI ===" -ForegroundColor Cyan
    try {
        $body = @{
            provider = "openai"
            messages = @(
                @{
                    role = "user"
                    content = "Hello, please give a very brief response."
                }
            )
        } | ConvertTo-Json
        $response = Invoke-RestMethod -Uri "$baseUrl/chat" -Method Post -Body $body -ContentType "application/json"
        Write-Host "Success! Response from OpenAI:" -ForegroundColor Green
        Write-Host $response.choices[0].message.content
    } catch {
        Write-Host "Error: $_" -ForegroundColor Red
    }
}

Write-Host "`nTests completed!" -ForegroundColor Cyan