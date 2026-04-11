import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv(r'c:\Users\ASUS\Proyectos\APP-II\CarroceriaAlvarado\backend\.env')

SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USERNAME = os.environ.get('SMTP_USERNAME', 'victorguayanay@gmail.com')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', 'qzgl wxpz stvw uxdp')

print(f"Probando conexión SMTP a {SMTP_SERVER}:{SMTP_PORT} con usuario {SMTP_USERNAME}")

msg = MIMEMultipart()
msg['From'] = SMTP_USERNAME
msg['To'] = SMTP_USERNAME
msg['Subject'] = "Prueba de Conexión SMTP"
msg.attach(MIMEText("Este es un correo de prueba.", 'plain'))

try:
    print("Iniciando conexión...")
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        print("Enviando helo...")
        server.set_debuglevel(1)
        server.ehlo()
        print("Iniciando TLS...")
        server.starttls()
        print("Re-enviando ehlo tras TLS...")
        server.ehlo()
        print("Iniciando sesión...")
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        print("Enviando mensaje...")
        server.send_message(msg)
        print("¡ÉXITO! El correo se envió correctamente.")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
