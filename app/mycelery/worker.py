import os
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.mycelery.app import celery_app

@celery_app.task(name="create_task")
def create_task(task_type):
    time.sleep(int(task_type) * 10)
    return True

@celery_app.task(name="send_password_otp")
def send_password_otp(email: str, otp: str):
    """Envia OTP por email usando Gmail SMTP"""
    try:
        # Configurações SMTP
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_username = os.getenv("SMTP_USERNAME")
        smtp_password = os.getenv("SMTP_PASSWORD")
        from_email = os.getenv("SMTP_FROM_EMAIL", smtp_username)
        from_name = os.getenv("SMTP_FROM_NAME", "Sistema de Sindicância")

        if not smtp_username or not smtp_password:
            raise ValueError("SMTP credentials not configured")

        # Criar mensagem
        msg = MIMEMultipart()
        msg['From'] = f"{from_name} <{from_email}>"
        msg['To'] = email
        msg['Subject'] = "Código de Verificação - Sistema de Sindicância Applicativo"

        # Corpo do email
        body = f"""
        <html>
            <body>
                <h2>Código de Verificação</h2>
                <p>Você solicitou a recuperação de senha.</p>
                <p>Seu código de verificação é: <strong>{otp}</strong></p>
                <p>Este código expira em 10 minutos.</p>
                <p>Se você não solicitou esta recuperação, ignore este email.</p>
                <hr>
                <p><small>Sistema de Sindicância Applicativo - Não responda este email</small></p>
            </body>
        </html>
        """

        msg.attach(MIMEText(body, 'html'))

        # Conectar e enviar
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Habilita criptografia TLS
        server.login(smtp_username, smtp_password)
        text = msg.as_string()
        server.sendmail(from_email, email, text)
        server.quit()

        return {"sent": True, "email": email}

    except Exception as e:
        # Log do erro (em produção, use logging adequado)
        print(f"Erro ao enviar email para {email}: {str(e)}")
        return {"sent": False, "error": str(e)}

@celery_app.task(name="send_password_otp_local")
def send_password_otp_local(email: str, otp: str):
    """Simula envio de OTP localmente (para desenvolvimento)"""
    print(f"=== EMAIL SIMULADO ===")
    print(f"Para: {email}")
    print(f"Assunto: Código de Verificação - Sistema de Sindicância Applicativo")
    print(f"Código: {otp}")
    print(f"====================")
    return {"sent": True}
