# Módulo 4C - Analytics Dashboard

**Estado:** 🔄 En Desarrollo (0%)  
**Última actualización:** 2026-04-17

## 📊 Descripción

Dashboard de métricas en tiempo real para redes sociales. Visualiza engagement, compara plataformas, y genera reportes automáticos exportables.

## 🎯 Características Principales

### Métricas en Tiempo Real
- Vistas, likes, comentarios, shares, reach, impressions
- Actualización automática cada hora
- Datos de 5 plataformas: Instagram, Twitter, LinkedIn, TikTok, YouTube

### Reportes Automáticos
- Programables (diario/semanal/mensual)
- Exportación en PDF, CSV, Excel

## 🚀 Instalación

### Instalar dependencias:
pip install -r requirements.txt --break-system-packages

### Ejecutar localmente:
python dashboard.py

## 📝 Endpoints API

- GET /api/metrics/{platform} - Métricas de una plataforma
- GET /api/metrics/compare - Comparativa entre plataformas
- GET /api/reports - Listar reportes programados
- POST /api/reports - Crear reporte programado

## 👤 Autor

Harold Maldonado (HMV)  
GitHub: haroldmaldonado5
