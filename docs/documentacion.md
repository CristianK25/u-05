# Guía de Documentación — Estilo del Profesor

Este documento analiza **exactamente** cómo documenta el profesor su código
en la `unidad5` y establece las reglas que debemos respetar para mantener
consistencia visual y de contenido en nuestro proyecto.

---

## 1. Estructura general de un archivo

Todo archivo `.py` abre con un **bloque de contexto** formado por:

```python
# app/modules/heroes/models.py
#
# Contiene SOLO el modelo de tabla SQLModel (Hero).
# Los schemas Pydantic de entrada/salida viven en schemas.py.
```

### Reglas del bloque de contexto:
- **Línea 1**: Ruta relativa del archivo como comentario (`# app/...`).
- **Línea 2**: Comentario vacío (`#`) que actúa como separador visual.
- **Líneas 3+**: Descripción breve (1-3 líneas) de qué contiene el archivo
  y qué **NO** contiene (para dejar clara la separación de responsabilidades).

> **Aplica en:** `models.py`, `schemas.py`.  
> **No aplica en:** `service.py`, `router.py`, `repository.py` (estos usan solo la línea 1).

---

## 2. Separadores visuales con líneas ASCII

El profesor usa separadores con el carácter `─` para dividir secciones lógicas
dentro de un archivo. El formato es:

```python
# ── Entrada ───────────────────────────────────────────────────────────────────
```

### Dónde los usa:
| Archivo        | Secciones que separa                                         |
|----------------|--------------------------------------------------------------|
| `schemas.py`   | `# ── Entrada`, `# ── Salida`                               |
| `service.py`   | `# ── Helpers privados`, `# ── Casos de uso`                |
| `router.py`    | `# ── Endpoints`                                             |

### Formato exacto:
- Prefijo: `# ── `
- Nombre de sección (capitalizado)
- Sufijo: ` ` + `─` repetido hasta completar ~80 columnas

---

## 3. Docstrings de clase

Toda clase tiene un docstring con el siguiente formato:

### 3.1 Clases simples (Models, Schemas, Repositorios cortos)

Docstring de **una sola línea**:

```python
class Hero(SQLModel, table=True):
    """Tabla heroes en la base de datos."""
```

```python
class HeroCreate(SQLModel):
    """Body para POST /heroes/"""
```

### 3.2 Clases complejas (Services, UoW, BaseRepository)

Docstring **multilínea estructurado** con secciones bien definidas:

```python
class HeroService:
    """
    Capa de lógica de negocio para Heroes.

    Responsabilidades:
    - Validaciones de dominio (alias único, etc.)
    - Coordinar repositorios a través del UoW
    - Levantar HTTPException cuando corresponde
    - NUNCA acceder directamente a la Session

    REGLA IMPORTANTE — objetos ORM y commit():
    Después de que el UoW hace commit(), SQLAlchemy expira los atributos
    del objeto ORM. Toda serialización (model_dump / model_validate)
    debe ocurrir DENTRO del bloque `with uow:`, antes de que __exit__
    dispare el commit.
    """
```

### Secciones usadas en docstrings de clase:
| Sección             | Cuándo se usa                                                  |
|---------------------|----------------------------------------------------------------|
| `Responsabilidades` | Services: lista con guiones de qué hace y qué NO hace         |
| `Características`   | Services complejos: notas sobre cross-module, etc.             |
| `Principio`         | BaseRepository: regla arquitectónica que cumple                |
| `Tipado`            | BaseRepository: explicación del Generic                        |
| `REGLA IMPORTANTE`  | Services: advertencia sobre serialización dentro del `with`    |
| `Uso en servicios`  | UnitOfWork: ejemplo de código mostrando el patrón `with`       |
| `Repositorios expuestos` | UoW específicos: lista de repos disponibles               |

---

## 4. Docstrings de método

Este es el patrón más detallado y consistente del profesor.
Usa un formato inspirado en **Google Style** con las siguientes secciones:

### 4.1 Formato completo (métodos importantes)

```python
def create(self, data: HeroCreate) -> HeroPublic:
    """
    Crea un nuevo héroe.

    Flujo:
    - Valida unicidad de alias
    - Construye entidad desde DTO
    - Persiste usando repositorio
    - Serializa antes de cerrar la transacción

    Args:
        data (HeroCreate): Datos de entrada.

    Returns:
        HeroPublic: DTO de salida.
    """
```

### 4.2 Formato con Raises (helpers de validación)

```python
def _get_or_404(self, uow: HeroUnitOfWork, hero_id: int) -> Hero:
    """
    Obtiene un héroe por ID o lanza excepción HTTP 404 si no existe.

    Args:
        uow (HeroUnitOfWork): Unidad de trabajo activa.
        hero_id (int): ID del héroe.

    Returns:
        Hero: Instancia encontrada.

    Raises:
        HTTPException: 404 si el héroe no existe.
    """
```

### 4.3 Formato con Nota (aclaraciones técnicas)

```python
def get_all(self, offset: int = 0, limit: int = 20) -> HeroList:
    """
    Obtiene lista paginada de héroes activos.

    Args:
        offset (int): Desplazamiento.
        limit (int): Límite de resultados.

    Returns:
        HeroList: DTO con lista de héroes y total.

    Nota:
        El total se calcula con una query separada.
    """
```

### 4.4 Formato con Importante (advertencias críticas)

```python
def add(self, instance: ModelT) -> ModelT:
    """
    Persiste una nueva entidad en la sesión actual.

    Flujo:
    - add(): marca la entidad para inserción
    - flush(): ejecuta INSERT en la DB sin commit (genera ID)
    - refresh(): sincroniza el estado del objeto con la DB

    Args:
        instance (ModelT): Instancia a persistir.

    Returns:
        ModelT: La misma instancia, con su ID ya generado.

    Importante:
        NO hace commit. Esto lo maneja el UnitOfWork.
    """
```

### Secciones de docstring de método (orden de aparición):
1. **Descripción** — Línea 1, breve y directa
2. **Flujo** — Lista de pasos secuenciales (solo en métodos complejos)
3. **Caso cross-module** — Cuando toca más de un dominio
4. **Args** — Parámetros con tipo y descripción
5. **Returns** — Tipo de retorno y descripción
6. **Raises** — Excepciones posibles
7. **Nota** — Aclaraciones técnicas opcionales
8. **Importante** — Advertencias críticas

---

## 5. Docstrings cortos (una línea)

El profesor los usa en:

- **Factory functions del Router**:
  ```python
  def get_hero_service(...) -> HeroService:
      """Factory de dependencia: inyecta el servicio con su Session."""
  ```

- **Funciones del database**:
  ```python
  def create_db_and_tables() -> None:
      """Crea todas las tablas definidas con SQLModel al iniciar la app."""
  ```

- **Endpoints del Router** (dentro del decorador + docstring):
  ```python
  @router.post("/", ..., summary="Crear un héroe")
  def create_hero(...) -> HeroPublic:
      """Router delega al servicio — sin lógica de negocio aquí."""
  ```

---

## 6. Comentarios inline

El profesor **casi no usa** comentarios inline dentro del código.
Cuando lo hace, son breves y técnicos:

```python
self.session.flush()  # obtiene el ID sin hacer commit
```

```python
.where(Hero.is_active == True)  # noqa: E712
```

### Regla: NO poner comentarios explicativos largos tipo tutorial.
El docstring del método ya explica el "qué" y "por qué".
Los comentarios inline solo aclaran una línea puntual que sería confusa sin contexto.

---

## 7. Decoradores del Router

El profesor usa el decorador del endpoint con **parámetros nombrados**
en múltiples líneas cuando son 3+ argumentos:

```python
@router.post(
    "/",
    response_model=HeroPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un héroe",
)
def create_hero(
    data: HeroCreate,
    svc: HeroService = Depends(get_hero_service),
) -> HeroPublic:
    """Router delega al servicio — sin lógica de negocio aquí."""
    return svc.create(data)
```

### Detalles del estilo:
- El decorador tiene siempre `summary=` para la documentación Swagger.
- La función tiene return type annotation (`-> HeroPublic`).
- El parámetro del servicio se llama `svc` (abreviado), no `service`.
- El `Query` usa `default=` explícito: `Query(default=0, ge=0)`.
- Hay una línea en blanco entre cada endpoint.

---

## 8. Naming del Router

```python
router = APIRouter()  # SIN prefix ni tags (se ponen en main.py con include_router)
```

El profesor define el router **limpio** y le agrega el prefix desde `main.py`:
```python
app.include_router(hero_router, prefix="/heroes", tags=["Heroes"])
```

---

## 9. Init del Service

El `__init__` del Service tiene su propio docstring completo:

```python
def __init__(self, session: Session) -> None:
    """
    Inicializa el servicio con una sesión de base de datos.

    Args:
        session (Session): Sesión activa que será utilizada por el UnitOfWork.

    Nota:
        El servicio no maneja directamente la transacción; delega en HeroUnitOfWork.
    """
    self._session = session
```

---

## 10. Schemas — Documentación particular

### Comentario de módulo (bloque de contexto):
```python
# app/modules/heroes/schemas.py
#
# Schemas Pydantic de entrada y salida para el módulo heroes.
# Separados del modelo de tabla para respetar el principio de
# responsabilidad única: models.py define la DB, schemas.py define
# los contratos HTTP.
```

### Schemas con BaseModel (para anidación):
Cuando un schema necesita anidar relaciones ORM, hereda de `BaseModel`
y se le agrega un docstring explicando **por qué** no usa `SQLModel`:

```python
class TeamWithHeroes(BaseModel):
    """
    Response model para GET /teams/{id}/heroes.
    Usa BaseModel puro (no SQLModel) para evitar conflictos del validador
    de SQLModel al anidar instancias Pydantic en la construcción del dict.
    """
    ...
    model_config = {"from_attributes": True}
```

---

## 11. UnitOfWork — Docstring del __init__ extendido

El UoW específico tiene un docstring **largo** en el `__init__`
(no solo en la clase) con estas secciones:

```python
def __init__(self, session: Session) -> None:
    """
    UnitOfWork específico del dominio Hero.

    Extiende el UnitOfWork base y registra los repositorios necesarios
    para operar dentro de una misma transacción consistente.

    Repositorios expuestos:
        - heroes: acceso a operaciones sobre Hero
        - teams: acceso a operaciones sobre Team (usado para validaciones
                 de integridad antes de persistir héroes)

    Args:
        session (Session): Sesión activa de base de datos compartida
                           por todos los repositorios.

    Responsabilidad:
        - Garantizar que todas las operaciones (Hero, Team, etc.)
          se ejecuten dentro de la misma transacción
        - Centralizar commit() y rollback() (heredado del UoW base)
        - Coordinar múltiples repositorios bajo una única unidad de trabajo

    Uso típico:

        with HeroUnitOfWork(session) as uow:
            team = uow.teams.get_by_id(team_id)
            hero = Hero(...)
            uow.heroes.add(hero)
    """
```

---

## 12. Resumen: Checklist de documentación por archivo

| Archivo           | Bloque contexto | Separadores | Docstring clase | Docstring método | summary= | Return type |
|-------------------|:-:|:-:|:-:|:-:|:-:|:-:|
| `models.py`       | ✅ (3 líneas) | ❌ | ✅ (1 línea) | ❌ | — | — |
| `schemas.py`      | ✅ (5 líneas) | ✅ Entrada/Salida | ✅ (1 línea) | ❌ | — | — |
| `repository.py`   | ✅ (1 línea) | ❌ | ✅ (multilínea) | ✅ (completo) | — | — |
| `unit_of_work.py` | ❌ | ❌ | ✅ (multilínea) | ✅ (__init__ largo) | — | — |
| `service.py`      | ✅ (1 línea) | ✅ Helpers/Casos | ✅ (multilínea) | ✅ (completo) | — | — |
| `router.py`       | ✅ (1 línea) | ✅ Endpoints | ❌ | ✅ (1 línea) | ✅ | ✅ `-> Type` |
| `config.py`       | ✅ (1 línea) | ❌ | ✅ (multilínea) | ❌ | — | — |
| `database.py`     | ❌ | ❌ | ❌ | ✅ (1 línea) | — | — |

---

## 13. Diferencias detectadas entre nuestro código y el del profesor

### Router:
| Aspecto | Profesor | Nuestro código |
|---------|----------|----------------|
| `prefix=` | Lo pone en `main.py` con `include_router` | Lo ponemos en el `APIRouter()` |
| `summary=` | Siempre presente en decoradores | Falta |
| Nombre del servicio inyectado | `svc` | `service` |
| Return type en funciones | `-> HeroPublic` | Falta |
| `Query(default=...)` | Usa `default=` explícito | No lo usamos |

### Service:
| Aspecto | Profesor | Nuestro código |
|---------|----------|----------------|
| `__init__` docstring | Completo con Args y Nota | Falta |
| Separadores `# ──` | `Helpers privados` / `Casos de uso` | Faltan |
| Docstring de cada método | Formato Google completo (Flujo, Args, Returns, Raises) | Algunos cortos |
| Comentarios inline | Casi inexistentes | Muchos comentarios explicativos |

### UoW:
| Aspecto | Profesor | Nuestro código |
|---------|----------|----------------|
| `__init__` docstring | Largo con Repositorios, Responsabilidad, Uso típico | Falta |

### Schemas:
| Aspecto | Profesor | Nuestro código |
|---------|----------|----------------|
| Bloque de contexto | 5 líneas con explicación de separación | Similar pero más corto |

---

## 14. Acciones pendientes

Para que nuestro código quede **indistinguible** del estilo del profesor,
hay que aplicar los siguientes cambios:

1. **Routers**: Agregar `summary=`, return types (`-> Tipo`), renombrar `service` a `svc`, mover `prefix`/`tags` al `main.py`, usar `Query(default=...)`.
2. **Services**: Agregar docstring completo al `__init__`, poner separadores `# ──`, expandir docstrings de métodos al formato Google completo, reducir comentarios inline.
3. **UoW específicos**: Agregar docstring largo al `__init__` con Repositorios expuestos, Responsabilidad y Uso típico.
4. **Models**: Agregar bloque de contexto de 3 líneas.
5. **Schemas**: Completar bloque de contexto de schemas de orden.
