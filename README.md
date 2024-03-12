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
   ```

4. Levanta el servicio de la base de datos y aplica las migraciones:
   ```bash
   $ docker compose -f docker-compose.dev.yml up -d tusdatos-postgres-db
   ```
   ```bash
   $ docker compose -f docker-compose.dev.yml run --rm tusdatos alembic upgrade head
   ```

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

## Consultas ~paralelas~ concurrentes

Ejecutar 15 consultas paralelas implica un requerimiento de hardware, donde 15 procesos están siendo ejecutados simultáneamente por distintos CPUs. Lamentablemente, mi máquina no tiene tantos CPUs, por lo que no podría replicar con exactitud el escenario. Sin embargo, el escenario que mi máquina sí permite replicar es el de 15 consultas concurrentes, es decir, 15 procesos que serán ejecutados en un mismo periodo de tiempo (pero no simultáneos).

### Preparación

Antes de iniciar los distintos escenarios será necesario preparar un punto de entrada para nuestra clase scraper, que nos servirá para más adelante:

```python
# run.py

import asyncio

from tusdatos.services.scraper import JudicialProcessScraper


async def main():
    user_document_num = "0968599XXXXXX"
    search_role = "ACTOR"

    scraper = JudicialProcessScraper(
        user_document_num=user_document_num,
        search_role=search_role,
    )
    await scraper.extract_data()


if __name__ == "__main__":
    asyncio.run(main())
```

### x1 Consultas Concurrentes

El primer escenario será ejecutar una única consulta concurrente; para ello, bastará con ejecutar el script anterior, observar el tiempo tardado y el comportamiento del scraper.

![](https://i.ibb.co/MN3yQFM/x1-consulta-concurrente.png)

Como vemos, es relativamente rápido para la cantidad de consultas que realiza y no presentó ningún inconveniente. Veamos qué pasa si aumentamos aún más el número de consultas concurrentes.

### x5 Consultas Concurrentes

Para este escenario, será necesario hacer una pequeña modificación en nuestro punto de entrada, permitiendo así un grupo de 5 corutinas, ejecutarlas y validar el comportamiento:

```python
# run.py

import asyncio

from tusdatos.services.scraper import JudicialProcessScraper


async def main():
    user_document_num = "0968599XXXXXX"
    search_role = "ACTOR"

    corroutines = []
    for _ in range(0, 5):
        scraper = JudicialProcessScraper(
            user_document_num=user_document_num,
            search_role=search_role,
        )
        corroutines.append(scraper.extract_data())

    await asyncio.gather(*corroutines)


if __name__ == "__main__":
    asyncio.run(main())
```

Ahora hagamos la prueba y veamos como se comporta:

![](https://i.ibb.co/1LcPRSC/x5-consulta-concurrente.png)

Como se evidencia no hay ningún problema en correr 5 consultas concurrentes y el incremento de tiempo es aceptable.
   
### x10 Consultas Concurrentes

Aumentemos la apuesta, veamos que ocurre con 10 consultas concurrentes:

```python
# run.py

# Mismo código anterior...

    corroutines = []
    for _ in range(0, 10): # <-- Incremento
        scraper = JudicialProcessScraper(
            user_document_num=user_document_num,
            search_role=search_role,
        )
        corroutines.append(scraper.extract_data())

# Continúa el código...
```

### x25 Consultas Concurrentes

Qué pasaría si se hacen 25 consultas concurrentes a la página de consulta. Veamoslo:

![image](https://github.com/xgabrielmorales/tusdatos/assets/50029987/96326c09-4a30-4bcf-932c-f39537f0eeb5)

Como vemos, lo único que ocurre es aumentar el tiempo de respuesta, sin embargo, el servidor de consulta responde sin ningún problema.

### Problemas de conexión y límite de requests

El caso de ejemplo anterior se realizó en un Droplet de DigitalOcean y la decisión no fue arbitraria. Durante el desarrollo de esta prueba, al hacer pruebas en mi máquina local, obtuve tiempos de respuesta similares a los expuestos en los ejemplos anteriores. Sin embargo, en los últimos días de la prueba, empecé a tener problemas de conexión con el servidor de consultas:

![](https://i.ibb.co/bFPh57S/httpx-error-conexion.png)

De alguna manera, desde mi máquina local, las conexiones fallaban cada vez con más frecuencia. La solución a este problema fue agregar un semáforo con la intención de limitar el número de corutinas relacionadas con consultas HTTP al servidor de consultas:

https://github.com/xgabrielmorales/tusdatos/blob/85d621e9ee517daa452e9a590d09f22024fb4be7/tusdatos/services/scraper.py#L27
https://github.com/xgabrielmorales/tusdatos/blob/85d621e9ee517daa452e9a590d09f22024fb4be7/tusdatos/services/scraper.py#L130

Esto supuso un alivio considerable, pero, por supuesto, los tiempos de respuesta iban a aumentar. Sin embargo, la implementación del semáforo se conservó, dado que no es recomendable abusar del servidor de consultas debido a la cantidad de solicitudes que se realizan por cada consulta única (aproximadamente +150 solicitudes por consulta para los números de documento compartidos).
