# Usar una imagen oficial de Python basada en Debian Bullseye (más estable para drivers)
FROM python:3.11-slim-bullseye

# Evitar archivos .pyc y habilitar logs
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 1. Actualizar e instalar dependencias base
RUN apt-get update && apt-get install -y curl gnupg2 unixodbc-dev

# 2. Descargar y preparar la llave de Microsoft
RUN curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /usr/share/keyrings/microsoft-prod.gpg

# 3. Añadir el repositorio de Microsoft SQL Server
RUN curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list

# 4. Actualizar repositorios e instalar el driver de SQL Server
# El ACCEPT_EULA=Y es obligatorio para aceptar la licencia de Microsoft
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# 5. Limpiar para reducir tamaño de imagen
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requerimientos e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del backend
COPY . .

# Exponer puerto
EXPOSE 5001

# Comando de inicio
CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:${PORT:-5001} --workers 2"]
