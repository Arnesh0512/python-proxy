$ports = @(54312,9000)

foreach ($port in $ports) {

    $pids = netstat -ano | Select-String ":$port\s"

    $pids = $pids | ForEach-Object {
        ($_ -split "\s+")[-1]
    } | Select-Object -Unique

    foreach ($procId in $pids) {
        if ($procId -match "^\d+$" -and $procId -ne 0) {
            taskkill /PID $procId /F
        }
    }
}

Start-Sleep -Seconds 5



# Run mitmdump using venv
Start-Process powershell -ArgumentList "-NoExit", "-Command",
"C:\blocker\Mitmenv\Scripts\mitmdump.exe -p 54312 -s C:\blocker\blocker.py --set http2=false --set ssl_insecure=true --set connection_strategy=lazy --set tls_version_server_min=TLS1_2 --set upstream_cert=false"

# Run FastAPI using same venv
Start-Process powershell -ArgumentList "-NoExit", "-Command",
"C:\blocker\Mitmenv\Scripts\uvicorn.exe main:app --app-dir C:\blocker\dashboard --host 127.0.0.1 --port 9000 --reload"