import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import bs4 as bs
import requests
from tqdm import tqdm
import pandas as pd
import re
from bs4 import BeautifulSoup
from pymongo import MongoClient
from bson.decimal128 import Decimal128
from decimal import Decimal
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_DOWN
import locale
from tqdm import tqdm
app = Flask(__name__)
CORS(app)

# Validación del servicio
def validate_service_key(api_key):
    # Implementa aquí la validación de la clave del servicio
    # Puedes comparar api_key con una clave predefinida
    valid_key = "tu_clave_secreta"
    return api_key == valid_key

@app.route('/scrape', methods=['GET'])
def scrape():
    # Validar la clave del servicio
    api_key = request.headers.get('Api-Key')
    if not api_key or not validate_service_key(api_key):
        return jsonify({"error": "Acceso no autorizado"}), 401

    keywords = request.args.get('keywords')
    url = f"https://listado.mercadolibre.com.co/{keywords}"

    resp = requests.get(url)
    resp = resp.text
    soup = bs.BeautifulSoup(resp, 'lxml')
    table = soup.find('section', {'class': 'ui-search-results ui-search-results--without-disclaimer shops__search-results'})

    titles = []
    links = []
    prices = []
    qualifications = []
    seen_prices = set()

    rows = table.find_all('li')
    stop_index = len(rows) - 3
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    for row in tqdm(rows[:stop_index]):
        link = row.find('a')['href']
        title = row.find('h2').text

        price_div = row.find("div", class_="ui-search-price__second-line shops__price-second-line")
        price = price_div.find("span", class_="ui-search-price__part").text.strip().split()[1]

        price = price.replace("pesos", "")
        if price not in seen_prices:
            seen_prices.add(price)

        qualification_span = row.find("span", class_="andes-visually-hidden", text=re.compile(r'Calificación \d+\.\d+'))
        if qualification_span:
            qualification_text = qualification_span.text
            match = re.search(r'(\d+\.\d+)', qualification_text)
            if match:
                qualification = match.group(0)
            else:
                qualification = "Calificación no disponible"
        else:
            qualification = "Calificación no disponible"

        titles.append(title)
        links.append(link)
        prices.append(price)
        qualifications.append(qualification)
        

    ## Crear una lista de diccionarios con los datos extraídos

    data = []
    for i in range(len(titles)):
        data.append({
            'title': titles[i],
            'price': prices[i],
            'qualification': qualifications[i],
            'link': links[i]
        })

    # Conectar a la base de datos MongoDB y verificar la conexión exitosa
    try:
        client = MongoClient('mongodb+srv://usuarioP:45678@cluster0.e3bbg5b.mongodb.net/?retryWrites=true&w=majority')
        db = client['scraped_data']
        collection = db[keywords]
        client.server_info()
        print("Conexión a la base de datos exitosa.")
    except Exception as e:
        return jsonify({"error": f"Error al conectar a la base de datos: {str(e)}"}), 500

    # Insertar los datos en la base de datos
    result = collection.insert_many(data)
    print(f"Se insertaron {len(result.inserted_ids)} documentos en la colección.")

    scraped_data = {
        "titles": titles,
        "links": links,
        "prices": prices,
        "qualifications": qualifications
    }

    return jsonify(scraped_data)

@app.route('/prices', methods=['GET'])
def get_prices():
    # Validar la clave del servicio
    api_key = request.headers.get('Api-Key')
    if not api_key or not validate_service_key(api_key):
        return jsonify({"error": "Acceso no autorizado"}), 401

    keywords = request.args.get('keywords')
    url = f"https://listado.mercadolibre.com.co/{keywords}"

    resp = requests.get(url)
    resp = resp.text
    soup = bs.BeautifulSoup(resp, 'lxml')
    table = soup.find('section', {'class': 'ui-search-results ui-search-results--without-disclaimer shops__search-results'})

    prices = []
    products = []

    rows = table.find_all('li')
    stop_index = len(rows) - 3

    for row in rows[:stop_index]:
        product_title = row.find('h2').text
        products.append(product_title)
        price_div = row.find("div", class_="ui-search-price__second-line shops__price-second-line")
        price = price_div.find("span", class_="ui-search-price__part").text.strip().split()[1]
        price = price.replace("pesos", "")
        prices.append(price)

    prices_data = {
        "products": products,
        "prices": prices,
    }
    return jsonify(prices_data)

@app.route('/export', methods=['GET'])
def export_data():
    # Validar la clave del servicio
    api_key = request.headers.get('Api-Key')
    if not api_key or not validate_service_key(api_key):
        return jsonify({"error": "Acceso no autorizado"}), 401

    keywords = request.args.get('keywords')
    try:
        client = MongoClient('mongodb+srv://usuarioP:45678@cluster0.e3bbg5b.mongodb.net/?retryWrites=true&w=majority')
        db = client['scraped_data']
        collection = db[keywords]
        client.server_info()
        print("Conexión a la base de datos exitosa.")

        # Obtener todos los documentos de la colección
        data = list(collection.find({}, {'_id': 0}))

        # Devolver los datos en formato JSON
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": f"Error al exportar datos: {str(e)}"}), 500

@app.route('/data', methods=['GET'])
def query_data():
    # Validar la clave del servicio
    api_key = request.headers.get('Api-Key')
    if not api_key or not validate_service_key(api_key):
        return jsonify({"error": "Acceso no autorizado"}), 401

    keywords = request.args.get('keywords')
    precio_min = request.args.get('precio_min')
    precio_max = request.args.get('precio_max')
    calificacion_min = request.args.get('calificacion_min')
    calificacion_max = request.args.get('calificacion_max')  # Nuevo parámetro

    try:
        client = MongoClient('mongodb+srv://usuarioP:45678@cluster0.e3bbg5b.mongodb.net/?retryWrites=true&w=majority')
        db = client['scraped_data']
        collection = db[keywords]
        client.server_info()
        print("Conexión a la base de datos exitosa.")

        # Obtener todos los documentos de la colección
        data = list(collection.find({}, {'_id': 0}))

        # Aplicar filtros en Python
        filtered_data = []
        seen_titles = set()  # Para mantener un registro de los títulos vistos
        for item in data:
            title = item['title']
            if title not in seen_titles:
                seen_titles.add(title)  # Agregar el título a los títulos vistos
                price = float(item['price'].replace("$", "").replace(".", "").replace(",", ""))
                qualification = item['qualification']
                if qualification == "Calificación no disponible":
                    # Si la calificación es "Calificación no disponible", asignar None en lugar de intentar convertirla
                    qualification = None
                else:
                    qualification = float(qualification)

                # Verificar si la calificación cumple con los filtros
                if (not precio_min or price >= float(precio_min)) and \
                    (not precio_max or price <= float(precio_max)) and \
                    (calificacion_min is None or (qualification is not None and qualification >= float(calificacion_min))) and \
                    (calificacion_max is None or (qualification is not None and qualification <= float(calificacion_max))):  # Nuevo filtro
                        filtered_data.append(item)

        # Devolver los datos filtrados en formato JSON
        return jsonify(filtered_data)
    except Exception as e:
        return jsonify({"error": f"Error al consultar datos: {str(e)}"}), 500



@app.route('/stats', methods=['GET'])
def get_statistics():
    # Validar la clave del servicio
    api_key = request.headers.get('Api-Key')
    if not api_key or not validate_service_key(api_key):
        return jsonify({"error": "Acceso no autorizado"}), 401

    keywords = request.args.get('keywords')
    try:
        client = MongoClient('mongodb+srv://usuarioP:45678@cluster0.e3bbg5b.mongodb.net/?retryWrites=true&w=majority')
        db = client['scraped_data']
        collection = db[keywords]
        client.server_info()
        print("Conexión a la base de datos exitosa.")

        # Obtener todos los documentos de la colección
        data = list(collection.find({}, {'_id': 0}))

        total_price = Decimal(0)  # Inicializar el total de precios como Decimal
        total_qualification = Decimal(0)  # Inicializar el total de calificaciones como Decimal
        total_items = 0  # Inicializar el contador de elementos
        total_items_with_qualification = 0  # Inicializar el contador de elementos con calificación

        for item in data:
            try:
                price_str = item['price'].replace("$", "").replace(".", "").replace(",", "").replace(" ", "").replace("pesos", "")
                price = Decimal(price_str)
                total_price += price
                total_items += 1

                qualification_str = item['qualification']
                match = re.search(r'(\d+\.\d+)', qualification_str)
                if match:
                    qualification = Decimal(match.group(0))
                    total_qualification += qualification
                    total_items_with_qualification += 1
            except (ValueError, TypeError) as e:
                # Manejar cualquier error de conversión de valores
                print(f"Error al convertir valores: {str(e)}")

        # Calcular el promedio de precios y calificaciones (para todos los elementos)
        avg_price = (total_price / total_items).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
        
        # Calcular el promedio de calificaciones (incluyendo elementos sin calificación)
        avg_qualification = (total_qualification / total_items).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
        
        # Calcular el promedio de calificaciones (solo para elementos con calificación)
        if total_items_with_qualification > 0:
            avg_qualification_with_rating = (total_qualification / total_items_with_qualification).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
        else:
            avg_qualification_with_rating = Decimal(0)  # No hay elementos con calificación

        # Formatear el valor de avg_price en formato de precio con puntos y decimales
        formatted_avg_price = f"{avg_price:,.2f}"

        # Devolver las estadísticas en formato JSON con los promedios
        stats = {
            "average_price": formatted_avg_price,
            "average_qualification_all": str(avg_qualification),
            "average_qualification_with_rating": str(avg_qualification_with_rating)
        }

        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": f"Error al obtener estadísticas: {str(e)}"}), 500
     
if __name__ == '__main__':
    app.run(debug=True)
