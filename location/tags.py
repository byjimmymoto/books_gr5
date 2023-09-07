tags_metadata = [
    {
        "name": "sgraphql",
        "description": "Enrutador para uso de graphql, solo debe usuarse cambiando el acceso a "
                       "http://localhost:8000/sgraphql",
    },
    {
        "name": "JWT",
        "description": "Endpoints para crear usuarios y autenticación por token JWT, después de creado el usuario debe "
                       "usarse el botón superior derecho de Authorize, ingresar el usuario y password",
    },
    {
        "name": "Book_local",
        "description": "CRUD para libros en base de datos local.",
    },
    {
        "name": "API_Books",
        "description": "Consulta de libros por atributos en DB Local, en Google Books y OpenLibrary",
    },
]

description = """
## Book GR5

API REST con la finalidad de dar solución a los siguientes retos:

* **Autenticación basada en generación y uso de token JWT, con expiración del mismo.**
* **Conectividad y uso de base de datos en AZURE PostgresSQL con manejo relacional.**
* **Entorno API REST para generación de CRUD de libros.**
* **Manejo de Paralelismo y asincronía para consulta de API de Google Books y OpenLibrary.**
* **Soporte de GraphQL funcional.**
* **Uso de Celery y Redis, con acceso por el puerto 5000.**
* **Incluye de logs y test.**

"""

