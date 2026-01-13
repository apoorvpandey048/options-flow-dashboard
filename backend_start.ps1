Set-Location "C:\Users\Apoor\options-flow-dashboard\backend"
# Export Insight Sentry API key for this session (uses the key stored in config by default)
$env:INSIGHT_SENTRY_API_KEY = 'eyJhbGciOiJIUzI1NiJ9.eyJ1dWlkIjoiYXdlc29tZWJsb2dzMjAxMEBnbWFpbC5jb20iLCJwbGFuIjoidWx0cmEiLCJuZXdzZmVlZF9lbmFibGVkIjp0cnVlLCJ3ZWJzb2NrZXRfc3ltYm9scyI6NSwid2Vic29ja2V0X2Nvbm5lY3Rpb25zIjoxfQ.zfYCHDg7v1O3Bkb6_JLlus90FtBUfcRH_Px6_sut-Ks'
$env:PORT = '10000'
& "C:\Users\Apoor\options-flow-dashboard\.venv\Scripts\python.exe" app.py
Pause
