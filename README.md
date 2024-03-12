# TusDatos: Prueba Técnica 🤓

Este repositorio contiene la resolución a la prueba técnica para el cargo de Backend Developer de la empresa [Tusdatos.co](https://www.tusdatos.co/) donde se solicitó extraer la información del sitio [Consulta de Procesos Judiciales de Ecuador](https://procesosjudiciales.funcionjudicial.gob.ec/expel-busqueda-avanzada) usando técnicas de scraping con Python.

## Estrategía

La estrategia utilizada para la resolución de la prueba técnica fue hacer uso de API Scraping, dado que el sitio web propuesto exponía una REST API, lo cual hacía más eficiente, computacionalmente hablando, la extracción de los datos en comparación con hacer Web Scraping.

Para la primera parte de la prueba, se implementó una funcionalidad asíncrona que consume y recupera la información del sitio para posteriormente ser almacenada en una base de datos no relacional (MongoDB). Esta funcionalidad permite la extracción de los **casos**, **detalles** y **acciones judiciales** de todos los procedimientos judiciales del actor o demandado.

Para la segunda parte, se implementó una API REST (en FastAPI) que expone los datos extraídos del sitio web; esta información está protegida y solo es accesible para los usuarios autenticados. Adicionalmente, esta API permite la consulta o actualización de los datos de un actor o demandado para posteriormente ser consultados.

## Inicializa el proyecto

1. Clona este repositorio en tu máquina local:
   ```bash
   $ git clone https://github.com/xgabrielmorales/tusdatos.git
   ````

2. Dentro de la carpeta del proyecto, crea un archivo .env y adicional las variables de entorno:
   ```bash
   $ cd tusdatos
   ````
   ```bash
   $ touch .env
   ````
   Aquí tienes unas de ejemplo que pueden servir: 🤙
    ```bash
    # Base
    # ==============================================================================
    SECRET_KEY=3RWM3zT68QEaOacQiYmSVzNyOHnJMpqVQi8mS2zN
    
    # Mongo DB
    # ==============================================================================
    MONGO_HOST=tusdatos-mongo-db
    MONGO_INITDB_ROOT_PASSWORD=password
    MONGO_INITDB_ROOT_USERNAME=admin
    
    # Postgres DB
    # ==============================================================================
    POSTGRES_DB=tusdatos-db
    POSTGRES_PASSWORD=e8617cc1dccfbeefe3777f6816bd6cce
    POSTGRES_HOST=tusdatos-postgres-db
    POSTGRES_USER=tusdatos-db
    ```


3. Haz build de la imagen de docker con el siguiente comando:
   ```bash
   $ docker compose -f docker-compose.dev.yml build
   ````

4. Levanta el servicio de la base de datos y aplica las migraciones:
   ```bash
   $ docker compose -f docker-compose.dev.yml up -d tusdatos-postgres-db
   ````
   ```bash
   $ docker compose -f docker-compose.dev.yml run --rm tusdatos alembic upgrade head
   ````

5. Levanta todos los servicios restantes:
   ```bash
   $ docker compose -f docker-compose.dev.yml up -d
   ```

Excelente, ya estás listo para consumir el REST API. 💪

## Documentación del API

Si completaste las sección aterior, entonces estás listo para consumir el API, la documentación de esta puede ser accedida desde tu navegador el la siguiente URL: http://localhost:8000/docs

> [!NOTE]
> Si no te es posible ver el sitio web de la documentación de OpenAPI de FastAPI es porque algo salió mal en la sección anterior. Asegurate de que los servicios de docker del proyecto estén corriendo y que no exista ningún otro servicios ocupando ya el puerto `8000`.
> 

## Consultas en paralelo

Ejecutar 15 consultas paralelas implica un requerimiento de hardware, donde 15 procesos están siendo ejecutados simultáneamente por distintos CPUs. Lamentablemente, mi máquina no tiene tantos CPUs, por lo que no podría replicar con exactitud el escenario. Sin embargo, el escenario que mi máquina sí permite replicar es el de 15 consultas concurrentes, es decir, 15 procesos que serán ejecutados en un mismo periodo de tiempo (pero no simultáneos).

