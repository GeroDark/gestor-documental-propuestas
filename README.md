# Sistema de Gestión Documental y Propuestas Empresariales

Sistema web empresarial desarrollado con Django para la gestión de clientes, propuestas comerciales, documentos, seguimiento operativo y auditoría interna.

## Descripción

Este proyecto fue construido como una solución modular para centralizar procesos comerciales y documentales dentro de una organización. Permite registrar clientes, gestionar propuestas, adjuntar documentos, hacer seguimiento del estado de cada propuesta, visualizar métricas en dashboard y mantener trazabilidad mediante auditoría.

## Objetivos del proyecto

- Centralizar la gestión de clientes y propuestas
- Mejorar la organización documental
- Mantener trazabilidad de cambios y acciones
- Exponer funcionalidades mediante API REST
- Mostrar una arquitectura profesional lista para escalar y desplegar

## Funcionalidades principales

- Autenticación de usuarios
- Usuario personalizado
- Gestión de perfil
- Roles por grupos:
  - Administrador
  - Asesor comercial
  - Supervisor
- CRUD de clientes
- CRUD de propuestas
- Cambio de estados de propuestas
- Historial de estados
- Comentarios en propuestas
- Gestión documental:
  - subida
  - listado
  - detalle
  - descarga
- Dashboard con resumen general
- Auditoría de acciones
- API REST con Django REST Framework
- Documentación automática con Swagger y Redoc
- Entorno Docker con PostgreSQL
- Datos demo mediante comando personalizado

## Stack tecnológico

- Python
- Django
- Django REST Framework
- Django Templates
- Bootstrap
- SQLite en desarrollo local tradicional
- PostgreSQL con Docker Compose
- JWT
- drf-spectacular / Swagger / Redoc
- Docker
- Docker Compose

## Arquitectura del proyecto

El proyecto está organizado de forma modular por aplicaciones:

- `core`: configuración base y utilidades generales
- `accounts`: autenticación, usuario personalizado y perfil
- `clients`: gestión de clientes
- `proposals`: gestión de propuestas, estados y comentarios
- `documents`: gestión documental
- `notifications`: base para notificaciones
- `audit`: trazabilidad y auditoría
- `dashboard`: resumen general del sistema

## Configuración por entornos

El proyecto usa settings separados:

- `config.settings.local` → desarrollo local con SQLite
- `config.settings.docker` → desarrollo con Docker + PostgreSQL
- `config.settings.production` → base para despliegue profesional

## Ejecución local sin Docker

### 1. Clonar repositorio

```powershell
git clone https://github.com/GeroDark/gestor-documental-propuestas.git
cd gestor-documental-propuestas
```

### 2. Crear entorno virtual

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```powershell
pip install -r requirements\base.txt
```

### 4. Crear archivo `.env`

Copiar desde `.env.example`:

```powershell
Copy-Item .env.example .env
```

### 5. Ejecutar migraciones

```powershell
python manage.py migrate
```

### 6. Crear superusuario

```powershell
python manage.py createsuperuser
```

### 7. Cargar datos demo

```powershell
python manage.py seed_demo --reset
```

### 8. Levantar servidor

```powershell
python manage.py runserver
```

## Ejecución con Docker

### 1. Crear archivo `.env`

```powershell
Copy-Item .env.example .env
```

### 2. Levantar contenedores

```powershell
docker compose up --build -d
```

### 3. Ejecutar migraciones

```powershell
docker compose exec web python manage.py migrate
```

### 4. Crear superusuario

```powershell
docker compose exec web python manage.py createsuperuser
```

### 5. Cargar datos demo

```powershell
docker compose exec web python manage.py seed_demo --reset
```

### 6. Apagar contenedores

```powershell
docker compose down
```

## Variables de entorno de ejemplo

El proyecto incluye un archivo `.env.example` como referencia.

Ejemplo base:

```env
SECRET_KEY=django-insecure-change-me
DEBUG=True
DJANGO_SETTINGS_MODULE=config.settings.docker

ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000

DB_NAME=gestor_documental
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

## Usuarios demo

El comando `seed_demo` crea usuarios de prueba:

- `admin_demo`
- `asesor_demo`
- `supervisor_demo`

Contraseña común para todos:

```text
Demo12345!
```

## Rutas importantes

- Inicio: `http://127.0.0.1:8000/`
- Admin: `http://127.0.0.1:8000/admin/`
- Swagger: `http://127.0.0.1:8000/api/docs/swagger/`
- Redoc: `http://127.0.0.1:8000/api/docs/redoc/`

## Datos demo

El proyecto incluye un comando personalizado para poblar el sistema con información de demostración.

En entorno local:

```powershell
python manage.py seed_demo --reset
```

Con Docker:

```powershell
docker compose exec web python manage.py seed_demo --reset
```

Este comando crea:

- usuarios demo
- clientes demo
- propuestas con distintos estados
- comentarios
- historial de estados
- documentos demo

## Estructura general del proyecto

```text
gestor-documental-propuestas/
├── apps/
│   ├── accounts/
│   ├── audit/
│   ├── clients/
│   ├── core/
│   ├── dashboard/
│   ├── documents/
│   ├── notifications/
│   └── proposals/
├── config/
│   └── settings/
│       ├── base.py
│       ├── local.py
│       ├── docker.py
│       └── production.py
├── requirements/
├── templates/
├── Dockerfile
├── docker-compose.yml
├── manage.py
└── README.md
```

## Calidad técnica aplicada

- Separación modular por apps
- Configuración por entornos
- API documentada
- Flujo con Docker y PostgreSQL
- Datos demo reproducibles
- Base preparada para CI/CD, testing y despliegue profesional

## Próximas mejoras planificadas

- GitHub Actions
- Tests automáticos
- Exportación CSV/Excel
- Alertas de vencimiento
- Deploy productivo
- Mejoras visuales y capturas para documentación

## Autor

Proyecto desarrollado por **GeroDark** **Walter Gerald Arzapalo Janampa** como parte de su portafolio profesional de desarrollo backend/full stack con Django.