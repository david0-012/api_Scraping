# API de Scraping MercadoLibre

## Descripción
Esta API proporciona funcionalidad para realizar scraping en el sitio web de MercadoLibre y consultar datos de productos basados en palabras clave. Además, permite exportar datos scrapeados, realizar consultas avanzadas y obtener estadísticas sobre los datos recolectados.

## Instrucciones de Uso

### Iniciar el Servidor
1. Iniciar el servidor de la aplicación Flask.

### Búsqueda de Productos - Scraping
1. Ruta: `/scrape`
   - Recibe una solicitud GET para buscar productos.
   - Realiza scraping del sitio web de MercadoLibre basado en palabras clave.
   - Devuelve los resultados de búsqueda en formato JSON.

### Consulta de Precios - Scraping
1. Ruta: `/prices`
   - Recibe una solicitud GET para obtener una lista de precios.
   - Realiza scraping del sitio web de MercadoLibre basado en palabras clave.
   - Devuelve los precios de los productos en formato JSON.

### Exportación de Datos - MongoDB
1. Ruta: `/export`
   - Recibe una solicitud GET para exportar datos scrapeados.
   - Conecta a una base de datos MongoDB.
   - Recupera los datos scrapeados de la base de datos.
   - Devuelve los datos en formato JSON.

### Consulta Avanzada de Datos - Filtrado
1. Ruta: `/data`
   - Recibe una solicitud GET para realizar una consulta avanzada de datos.
   - Conecta a una base de datos MongoDB.
   - Filtra los productos según criterios específicos (precio mínimo, precio máximo, calificación mínima, calificación máxima).
   - Devuelve los resultados de la consulta en formato JSON.

### Estadísticas de Datos - Análisis
1. Ruta: `/stats`
   - Recibe una solicitud GET para obtener estadísticas de los datos scrapeados.
   - Conecta a una base de datos MongoDB.
   - Calcula estadísticas como el precio promedio de los productos y la calificación promedio.
   - Devuelve las estadísticas en formato JSON.

## Requisitos
- Python 3.7 o superior
- Flask
- BeautifulSoup
- pymongo
- dnspython

## Ejecución
1. Clona este repositorio.
2. Instala las dependencias con `pip install -r requirements.txt`.
3. Configura la variable de entorno `API_KEY` con tu clave de servicio.
4. Ejecuta la aplicación con `python app.py`.

# Diagrama de Funcionalidad del API

El API de Scraping MercadoLibre ofrece las siguientes funcionalidades:

1. Búsqueda de Productos - Scraping
    1. Ruta: `/scrape`
        - Realiza scraping en el sitio web de MercadoLibre.
        - Recibe palabras clave como entrada.
        - Devuelve los resultados de búsqueda en formato JSON.

2. Consulta de Precios - Scraping
    1. Ruta: `/prices`
        - Realiza scraping en el sitio web de MercadoLibre.
        - Recibe palabras clave como entrada.
        - Devuelve los precios de los productos en formato JSON.

3. Exportación de Datos - MongoDB
    1. Ruta: `/export`
        - Conecta a una base de datos MongoDB.
        - Recupera los datos scrapeados de la base de datos.
        - Devuelve los datos en formato JSON.

4. Consulta Avanzada de Datos - Filtrado
    1. Ruta: `/data`
        - Conecta a una base de datos MongoDB.
        - Aplica filtros avanzados (precio mínimo, precio máximo, calificación mínima, calificación máxima) a los datos.
        - Devuelve los resultados de la consulta en formato JSON.

5. Estadísticas de Datos - Análisis
    1. Ruta: `/stats`
        - Conecta a una base de datos MongoDB.
        - Calcula estadísticas como el precio promedio de los productos y la calificación promedio.
        - Devuelve las estadísticas en formato JSON.

6. Inicio de la Aplicación
    - La aplicación Flask se inicia en el puerto 5000 o el puerto proporcionado por Heroku.


## Documentación
Para obtener más detalles sobre el uso de esta API, [Consulta la documentación en Postman](https://documenter.getpostman.com/view/23134211/2s9YBz4FdF)
.

## Autor
Autor: [Christian Felipe Cruz](tu-email@example.com)-[Juan David Casallas Pava](davidcasallas1202@gmail.com)

## Licencia
NN
