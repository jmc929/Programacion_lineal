# ==========================================
# Etapa 1: Compilación del Frontend (React + Vite)
# ==========================================
FROM node:20-alpine AS frontend-builder
WORKDIR /build

# Instalar dependencias
COPY Frontend_programación_lineal/package*.json ./
RUN npm install

# Copiar código fuente y compilar artefactos estáticos (dist)
COPY Frontend_programación_lineal/ ./
RUN npm run build

# ==========================================
# Etapa 2: Backend (FastAPI) y Servidor Integrado
# ==========================================
FROM python:3.11-slim
WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STATIC_DIR=/app/static

# Instalar dependencias de Python
COPY Backend_programación_lineal/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el backend
COPY Backend_programación_lineal/ ./

# Copiar los archivos estáticos generados por el frontend
COPY --from=frontend-builder /build/dist /app/static

EXPOSE 8000

# Ejecutar el servidor con Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
