import argparse
import os
import smtplib
import ssl
import time
from datetime import datetime
from email.errors import HeaderParseError
from email.headerregistry import Address
from email.message import EmailMessage
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def main():
    parser = argparse.ArgumentParser(description="Check website availability every 15 seconds.")
    parser.add_argument("--url", default="https://tss.ucsd.edu/")
    args = parser.parse_args()
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    if not all((smtp_host, smtp_user, smtp_password)):
        parser.error("Set SMTP_HOST, SMTP_USER, and SMTP_PASSWORD before running the monitor.")

    interval = 15
    notified = False

    try:
        while True:
            email = input("Enter the email address to notify: ").strip()
            try:
                recipient = Address(addr_spec=email)
                if recipient.username and recipient.domain:
                    break
            except (HeaderParseError, ValueError):
                pass
            print("Enter a valid email address.")

        next_check = time.monotonic()
        while True:
            timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
            request = Request(args.url, headers={"User-Agent": "WebsiteAvailabilityMonitor/1.0"})
            is_up = False
            try:
                with urlopen(request, timeout=10) as response:
                    status = response.status
                    is_up = 200 <= status < 300
                    label = "UP" if is_up else "DOWN"
                    print(f"{timestamp} {label}: HTTP {status} {args.url}", flush=True)
            except HTTPError as error:
                print(f"{timestamp} DOWN: HTTP {error.code} {args.url}", flush=True)
                error.close()
            except (URLError, TimeoutError, OSError) as error:
                print(f"{timestamp} DOWN: {error} {args.url}", flush=True)

            if is_up and not notified:
                message = EmailMessage()
                message["From"] = smtp_user
                message["To"] = str(recipient)
                message["Subject"] = "TSS is up"
                message.set_content(f"TSS is up.\n\n{args.url} returned HTTP {status} at {timestamp}.")
                try:
                    with smtplib.SMTP_SSL(smtp_host, timeout=10, context=ssl.create_default_context()) as smtp:
                        smtp.login(smtp_user, smtp_password)
                        smtp.send_message(message)
                        notified = True
                    print(f"Notification sent to {recipient}.", flush=True)
                except (smtplib.SMTPException, OSError) as error:
                    print(f"{timestamp} Email connection error: {error}", flush=True)

            next_check += interval
            delay = next_check - time.monotonic()
            if delay <= 0:
                next_check = time.monotonic() + interval
                delay = interval
            time.sleep(delay)
    except KeyboardInterrupt:
        print("\nMonitoring stopped.", flush=True)
    except EOFError:
        print("\nNo email address entered. Monitoring stopped.", flush=True)


if __name__ == "__main__":
    main()
