import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(
    host: str,
    port: int,
    login: str,
    password: str,
    to_addr: str,
    subject: str,
    body: str,
    use_tls: bool = True,
) -> tuple[bool, str]:
    """
    SMTP üzerinden e-posta gönder.
    Returns: (True, "") on success, (False, error_message) on failure.
    """
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = login
        msg["To"] = to_addr
        msg.attach(MIMEText(body, "plain", "utf-8"))

        if use_tls:
            context = ssl.create_default_context()
            with smtplib.SMTP(host, port, timeout=15) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(login, password)
                server.sendmail(login, to_addr, msg.as_string())
        else:
            with smtplib.SMTP_SSL(host, port, timeout=15) as server:
                server.login(login, password)
                server.sendmail(login, to_addr, msg.as_string())

        return True, ""
    except Exception as e:
        return False, str(e)


def test_connection(host: str, port: int, login: str, password: str, use_tls: bool = True) -> tuple[bool, str]:
    """SMTP bağlantısını doğrula — kendine test maili gönder."""
    return send_email(
        host, port, login, password,
        to_addr=login,
        subject="AusbildungBot — SMTP Test",
        body="Bu bir test e-postasıdır. SMTP ayarlarınız doğru çalışıyor.",
        use_tls=use_tls,
    )
