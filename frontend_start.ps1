Set-Location "C:\Users\Apoor\options-flow-dashboard\frontend"
# Point dev server at local backend for testing
$env:REACT_APP_API_URL = 'http://127.0.0.1:10000'
npm start
Pause
