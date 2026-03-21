# Sistema de Gestión Documental y Propuestas Empresariales

Sistema web empresarial desarrollado con Django para la gestión de clientes, propuestas comerciales, documentos, seguimiento operativo y auditoría interna.

## Descripción

Este proyecto fue construido como una solución modular para centralizar procesos comerciales y documentales dentro de una organización. Permite registrar clientes, gestionar propuestas, adjuntar documentos, hacer seguimiento del estado de cada propuesta, visualizar métricas en un dashboard, exportar información, detectar vencimientos y mantener trazabilidad mediante auditoría.

Está pensado como proyecto profesional de portafolio, con una base sólida para entrevistas técnicas, demostraciones funcionales y evolución hacia un entorno de despliegue real.

## Objetivos del proyecto

- Centralizar la gestión de clientes y propuestas comerciales
- Mejorar la organización documental
- Mantener trazabilidad de cambios y acciones críticas
- Exponer funcionalidades mediante API REST
- Mostrar una arquitectura profesional, modular y escalable
- Incorporar buenas prácticas de Docker, testing y CI

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
- Dashboard con métricas generales
- Auditoría de acciones
- API REST con Django REST Framework
- Documentación automática con Swagger y Redoc
- Entorno Docker con PostgreSQL
- Datos demo mediante comando personalizado
- Exportación CSV de clientes y propuestas
- Alertas de vencimiento mediante management command
- Integración continua con GitHub Actions
- Tests automáticos básicos de negocio

## Roles del sistema

### Administrador
- Acceso general al sistema
- Gestión completa de clientes, propuestas y documentos
- Cambio de estados sensibles
- Supervisión de trazabilidad y auditoría

### Supervisor
- Seguimiento y validación operativa
- Aprobación o rechazo de propuestas según flujo del sistema
- Revisión de estados y vencimientos

### Asesor comercial
- Registro y gestión operativa de clientes
- Creación y seguimiento de propuestas
- Registro de comentarios y carga documental

## Stack tecnológico

- Python
- Django
- Django REST Framework
- Django Templates
- Bootstrap
- SQLite para desarrollo local tradicional
- PostgreSQL con Docker Compose
- JWT
- drf-spectacular
- Swagger / Redoc
- Docker
- Docker Compose
- GitHub Actions

## Arquitectura del proyecto

El proyecto está organizado de forma modular por aplicaciones:

- `core`: configuración base y utilidades generales
- `accounts`: autenticación, usuario personalizado y perfil
- `clients`: gestión de clientes
- `proposals`: gestión de propuestas, estados y comentarios
- `documents`: gestión documental
- `notifications`: alertas y comandos relacionados con vencimientos
- `audit`: trazabilidad y auditoría
- `dashboard`: resumen general del sistema

## Configuración por entornos

El proyecto usa settings separados:

- `config.settings.local` → desarrollo local con SQLite
- `config.settings.docker` → desarrollo con Docker + PostgreSQL
- `config.settings.production` → base para despliegue profesional

## Casos de uso principales

1. Registrar un cliente
2. Crear una propuesta comercial
3. Asignar responsable y fecha de vencimiento
4. Cambiar el estado de la propuesta según el avance
5. Registrar comentarios de seguimiento
6. Adjuntar documentos relacionados
7. Consultar métricas en dashboard
8. Exportar información en CSV
9. Detectar propuestas por vencer o vencidas
10. Mantener auditoría de acciones relevantes

## API disponible

El proyecto expone endpoints REST para los principales módulos:

- clientes
- propuestas
- documentos
- resumen del dashboard

También incluye:

- autenticación con JWT
- documentación interactiva con Swagger
- documentación alternativa con Redoc

## Prerrequisitos

Para trabajar con este proyecto se recomienda tener instalado:

- Python 3.12
- Git
- VS Code
- Docker Desktop

## Ejecución local sin Docker

### 1. Clonar el repositorio

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

### 4. Crear archivo `.env` para desarrollo local

> Importante: el archivo `.env.example` está orientado al flujo con Docker.  
> Para correr sin Docker, crea un `.env` local con este contenido:

```env
SECRET_KEY=django-insecure-change-me
DEBUG=True
DJANGO_SETTINGS_MODULE=config.settings.local
ALLOWED_HOSTS=127.0.0.1,localhost
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

Copia el archivo de ejemplo:

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

## Variables de entorno de ejemplo para Docker

El proyecto incluye un archivo `.env.example` pensado para el flujo con Docker:

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

## Exportación CSV

El sistema permite exportar listados a CSV desde la interfaz web.

Actualmente incluye:

- exportación CSV de clientes
- exportación CSV de propuestas

La exportación respeta los filtros aplicados en cada listado, lo que permite descargar exactamente la información que se está visualizando en pantalla.

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

## Alertas de vencimiento

El proyecto incluye un comando para revisar propuestas por vencer y propuestas vencidas.

En entorno local:

```powershell
python manage.py check_proposal_deadlines
```

Con Docker:

```powershell
docker compose exec web python manage.py check_proposal_deadlines
```

Para marcar automáticamente como vencidas las propuestas atrasadas y dejar historial de estado y auditoría:

```powershell
python manage.py check_proposal_deadlines --mark-expired --changed-by admin_demo
```

Con Docker:

```powershell
docker compose exec web python manage.py check_proposal_deadlines --mark-expired --changed-by admin_demo
```

## Testing

El proyecto incluye pruebas automáticas básicas orientadas a flujos útiles del negocio, entre ellas:

- creación de datos demo
- métricas del dashboard
- validación de flujo de estados de propuestas
- exportación CSV
- alertas de vencimiento

Ejecutar tests:

```powershell
python manage.py test -v 2
```

## Integración continua

Se configuró GitHub Actions para validar automáticamente:

- consistencia de migraciones
- chequeo general de Django
- ejecución de tests

Cada push a `main` ejecuta el workflow de CI.

## Rutas importantes

- Inicio: `http://127.0.0.1:8000/`
- Admin: `http://127.0.0.1:8000/admin/`
- Swagger: `http://127.0.0.1:8000/api/docs/swagger/`
- Redoc: `http://127.0.0.1:8000/api/docs/redoc/`

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
├── .github/
│   └── workflows/
├── Dockerfile
├── docker-compose.yml
├── manage.py
└── README.md
```

## Calidad técnica aplicada

- Separación modular por apps
- Configuración por entornos
- API documentada
- Uso de Docker y PostgreSQL
- Datos demo reproducibles
- Exportación de datos
- Comandos de mantenimiento y seguimiento
- CI con GitHub Actions
- Tests básicos orientados a lógica real del sistema

## Próximas mejoras planificadas

- Exportación Excel
- Mayor cobertura de tests
- Mejoras visuales en interfaz
- Capturas o GIF de demostración en README
- Endurecimiento adicional para deploy productivo
- Automatización programada de alertas de vencimiento

## Autor

Proyecto desarrollado por **Walter Gerald Arzapalo Janampa**  
GitHub: **GeroDark**