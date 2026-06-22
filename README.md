# hub-ms-operacion

Microservicio de Viajes / Operaciones del Hub Empresarial. Expone una API REST (Quart, async) para crear, listar, actualizar y eliminar viajes.

Repos relacionados: [`hub-infra`](https://github.com/benjaminAndaur/hub-infra) (nginx, docker-compose, base de datos), [`hub-backends`](https://github.com/benjaminAndaur/hub-backends) (resto de microservicios), [`hub-ms-facturacion`](https://github.com/benjaminAndaur/hub-ms-facturacion) (microservicio hermano con BD propia), [`hub-frontends`](https://github.com/benjaminAndaur/hub-frontends), [`hub-bff`](https://github.com/benjaminAndaur/hub-bff) (BFF en NestJS que agrega este microservicio + facturación, protegido con Circuit Breaker).

## Persistencia de datos — Database per Service

A diferencia del resto de los módulos del Hub (que comparten la base de datos `asdf_db`), `modulo_operacion` tiene **su propia base de datos PostgreSQL aislada** (`operacion_db`, contenedor `db-operacion`). Esto implementa el patrón **Database per Service**: este microservicio es el único dueño de su esquema, nadie más puede leer o escribir directamente sobre él.

- Motor: PostgreSQL 15.
- Acceso: exclusivamente vía SQLAlchemy 2.0 async + asyncpg, desde la capa `src/repository`.
- Schema inicial: [`hub-infra/db_operacion/init.sql`](https://github.com/benjaminAndaur/hub-infra/blob/main/db_operacion/init.sql) (tabla `viajes`, índices y datos semilla). El ORM además ejecuta `Base.metadata.create_all()` al arrancar como red de seguridad.
- Variable de entorno: `DATABASE_URL=postgresql+asyncpg://admin:admin123@db-operacion:5432/operacion_db`.
- Sin FK hacia otros módulos: `conductor_id`, `tracto_id`, `rampla_id`, `cliente_id` son IDs externos denormalizados (junto a su valor textual, ej. `conductor_nombre`). No hay integridad referencial entre microservicios, por diseño, para permitir despliegue e infraestructura de datos independientes.

El endpoint `GET /api/v1/operacion/health` reporta el estado de la conexión a su propia base de datos (`db_status: "connected" | "error"`), evidenciando que la gestiona de forma independiente.

## Capas

```
main.py                                # entrypoint Quart; inyecta repo/service/sesión en g{}
src/
  models/operacion_db.py               # ORM SQLAlchemy (Viaje)
  repository/operacion_repository.py   # acceso a datos async, sin lógica de negocio
  service/operacion_service.py         # lógica de negocio
  controller/operacion_controller.py   # Blueprint Quart, valida y expone endpoints
  utils/auth.py                        # decoradores @login_required y @require_permission
```

## Cómo ejecutar

**Standalone:**
```bash
git clone https://github.com/benjaminAndaur/hub-ms-operacion.git
cd hub-ms-operacion
pip install -r requirements.txt

export DATABASE_URL=postgresql+asyncpg://admin:admin123@localhost:5432/operacion_db
export JWT_SECRET=super-secret-key-123

uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Stack completo:** clonar este repo como hermano de `hub-infra`, `hub-backends` y `hub-frontends` (mismo directorio padre), luego desde `hub-infra` ejecutar `docker-compose up --build` (levanta `db-operacion` automáticamente).

## Cómo probar

```bash
# Health-check (público)
curl http://localhost:8080/api/v1/operacion/health

# Con JWT (requiere login previo en /api/v1/administracion/login)
curl -H "Authorization: Bearer <token>" http://localhost:8080/api/v1/operacion/viajes
```

## Endpoints

| Método | Ruta | Permiso |
|---|---|---|
| GET | `/api/v1/operacion/health` | público |
| POST | `/api/v1/operacion/viajes` | `operacion:edit` |
| GET | `/api/v1/operacion/viajes` | `operacion:view` |
| PUT | `/api/v1/operacion/viajes/<id>` | `operacion:edit` |
| DELETE | `/api/v1/operacion/viajes/<id>` | `operacion:edit` |
