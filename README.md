# API de Órdenes - Backend

Sistema de compras y gestión de órdenes desarrollado con **FastAPI**, **SQLModel** y **PostgreSQL**. Este proyecto implementa una arquitectura robusta basada en patrones de diseño como **Unit of Work** y **Repository Pattern**, asegurando la integridad transaccional y la mantenibilidad del código.

## 🚀 Tecnologías Principales

- **[FastAPI](https://fastapi.tiangolo.com/):** Framework moderno y rápido para construir APIs con Python.
- **[SQLModel](https://sqlmodel.tiangolo.com/):** Biblioteca que combina SQLAlchemy y Pydantic para interactuar con bases de datos.
- **[PostgreSQL](https://www.postgresql.org/):** Base de datos relacional para almacenamiento persistente.
- **[Pydantic Settings](https://docs.pydantic.dev/latest/usage/pydantic_settings/):** Gestión de configuraciones mediante variables de entorno.
- **[Uvicorn](https://www.uvicorn.org/):** Servidor ASGI de alto rendimiento.

## 🏗️ Arquitectura y Patrones

El proyecto sigue una estructura modular y aplica principios de **Clean Architecture**:

- **Repository Pattern:** Desacopla la lógica de negocio del acceso directo a la base de datos, facilitando pruebas y cambios en la persistencia.
- **Unit of Work (UoW):** Coordina múltiples repositorios en una única transacción atómica, garantizando que todos los cambios se apliquen o se reviertan juntos.
- **Service Layer:** Contiene la lógica de negocio pura, orquestando repositorios y UoW sin depender de los detalles de la API (routers).
- **Schemas (DTOs):** Separación clara entre los modelos de base de datos y los esquemas de entrada/salida (Pydantic).

## 📂 Estructura del Proyecto

```text
app/
├── core/               # Configuraciones globales (DB, Config, Base Patterns)
└── modules/            # Módulos de dominio
    ├── orden/          # Gestión de órdenes y sus ítems
    └── producto/       # Gestión del catálogo de productos
        ├── models.py      # Definición de tablas SQLModel
        ├── schemas.py     # DTOs de Pydantic
        ├── repository.py  # Acceso a datos especializado
        ├── unit_of_work.py# Transaccionalidad atómica
        ├── service.py     # Lógica de negocio
        └── router.py      # Endpoints de la API
```

## 🛠️ Instalación y Configuración

### 1. Clonar y preparar entorno
```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Variables de Entorno
Crea un archivo `.env` basado en `.env.example`:
```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=ordenes_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

### 3. Ejecutar la Aplicación
```bash
uvicorn main:app --reload
```
La aplicación creará automáticamente las tablas en la base de datos al iniciar gracias al hook de `lifespan`.

## 📖 Documentación de la API

Una vez en ejecución, puedes acceder a la documentación interactiva en:
- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Endpoints Principales

- **Productos:** `GET /products`, `POST /products`, `GET /products/{id}`
- **Órdenes:** `GET /orders`, `POST /orders`, `GET /orders/{id}`

## 📝 Reglas de Negocio Implementadas

- **Cálculo Automático:** El total de la orden se calcula sumando el (precio * cantidad) de cada ítem.
- **Instantánea de Precios:** Al crear una orden, se guarda el `unit_price` actual del producto en el `OrderItem` para evitar que cambios futuros en el precio afecten órdenes históricas.
- **Validación Atómica:** Si un producto solicitado no existe, la transacción se revierte completamente (gracias al UoW).
