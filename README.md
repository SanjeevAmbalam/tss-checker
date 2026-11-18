# TSS Checker

TSS Checker polls [UC San Diego TSS](https://tss.ucsd.edu/) every 15 seconds and emails you when it first returns an HTTP 2xx response. It also sends the alert if the site is already up when you start the script.

## Run locally

You need Python 3.10 or newer and a sender account that supports SMTP over SSL on port 465. The script uses the Python standard library.

Set the sender configuration in PowerShell. This example uses Gmail and a [Google app password](https://support.google.com/accounts/answer/185833).

```powershell
$env:SMTP_HOST = "smtp.gmail.com"
$env:SMTP_USER = "your-address@gmail.com"
$env:SMTP_PASSWORD = Read-Host "SMTP app password" -MaskInput
py .\tss_checker.py
```

Enter the recipient's email address when prompted. Keep the terminal running until you receive the alert. The checker retries a failed send on the next successful site check and sends one alert per run. Press Ctrl+C to stop monitoring.

To monitor a different URL, pass `--url https://example.com/`.
