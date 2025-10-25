# Importamos las librerías esenciales para nuestro proyecto
from selenium import webdriver # Herramienta principal para automatizar navegadores.
from selenium.webdriver.chrome.options import Options # Para configurar el navegador (ej. User-Agent).
from selenium.webdriver.common.by import By # Para especificar cómo buscar un elemento (ej. por CSS).
from selenium.webdriver.support.ui import WebDriverWait # Permite establecer 'esperas inteligentes' (Explicit Waits).
from selenium.webdriver.support import expected_conditions as EC # Define las condiciones para las esperas (ej. elemento visible).
import time # Para pausas simples (time.sleep).
import random # Para generar pausas aleatorias (Anti-Bloqueo).
import pandas as pd # Librería para manejo y exportación de datos (DataFrames).
import os # Módulo para interactuar con el sistema operativo (ej. crear la carpeta 'data').

# ====================================================================================
# PARTE I: CONFIGURACIÓN INICIAL Y OPCIONES ANTI-BLOQUEO
# ====================================================================================

def configurar_driver():
    """
    Configura y retorna una instancia del WebDriver de Chrome con opciones anti-bloqueo.
    """
    opciones = Options()
    
    # 💡 Anti-Bloqueo 1: Cambiamos el User-Agent para simular un navegador real.
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    opciones.add_argument(f'user-agent={user_agent}')
    
    # 💡 Anti-Bloqueo 2: Ocultamos las huellas de automatización de Selenium.
    opciones.add_argument('--disable-blink-features=AutomationControlled')
    opciones.add_argument('--log-level=3') 
    
    print("Iniciando el WebDriver...")
    driver = webdriver.Chrome(options=opciones)
    return driver

# ====================================================================================
# PARTE II: EXTRACCIÓN DE DATOS CON PAGINACIÓN (VERSIÓN FINAL Y ROBUSTA)
# ====================================================================================

def ejecutar_scraper(busqueda):
    """
    Función principal para inicializar el driver, navegar y realizar la paginación.
    """
    driver = configurar_driver()
    url_base = "https://listado.mercadolibre.com.ar/" 
    termino_url = busqueda.replace(' ', '-')
    url_inicial = f"{url_base}{termino_url}"
    
    print(f"Navegando a: {url_inicial}")
    driver.get(url_inicial)

    datos_extraidos = [] 
    pagina_actual = 1

    # 💡 Bucle de Paginación: Repite la extracción mientras exista un botón 'Siguiente'
    while True:
        print(f"\n--- Raspando Página {pagina_actual} (URL: {driver.current_url}) ---")
        
        # 💡 Anti-Bloqueo 3: Espera aleatoria al inicio de cada página
        tiempo_espera = random.uniform(2, 4) 
        print(f"Esperando {tiempo_espera:.2f} segundos...")
        time.sleep(tiempo_espera) 
        
        # ANTI-BLOQUEO: Manejar Banners de Cookies (Solo necesario en la primera carga)
        if pagina_actual == 1:
            try:
                boton_aceptar = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.cookie-consent-button, button[data-testid='action:understood-button']"))
                )
                boton_aceptar.click()
                print("Banner de cookies cerrado.")
                time.sleep(1) 
            except Exception:
                pass

        # 1. Espera Explícita para la carga de elementos de la lista
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.ui-search-layout__item, div.poly-card__content"))
            )
            print("Elementos de la página cargados.")
        except Exception:
            print("Error crítico al cargar los elementos. Deteniendo el scraping.")
            break 

        # 2. Localizar y Extraer datos
        productos = driver.find_elements(By.CSS_SELECTOR, "li.ui-search-layout__item, div.poly-card__content")
        print(f"Productos encontrados en esta página: {len(productos)}")

        # Lógica de Extracción (Iteración sobre cada tarjeta de producto)
        for i, producto in enumerate(productos):
            try:
                # 💡 DOBLE ROBUSTEZ: Intentamos encontrar el link. Si no existe, es un anuncio y lo saltamos.
                try:
                    # a. EXTRAER LINK Y URL
                    link_element = producto.find_element(By.TAG_NAME, "a") 
                    url = link_element.get_attribute("href")
                except:
                    # Si no hay link 'a' es un banner o anuncio, y lo saltamos.
                    continue 
                
                # b. EXTRAER NOMBRE: Flexibilidad buscando H2 o H3
                nombre_elements = link_element.find_elements(By.CSS_SELECTOR, "h2, h3")
                if nombre_elements:
                    nombre = nombre_elements[0].text
                else:
                    nombre = link_element.text # Respaldo con el texto del link
                
                # Limpieza Estética: 
                nombre = nombre.strip().replace('\n', ' ').replace('\r', ' ')
                if not nombre:
                    nombre = "Nombre no encontrado"

                # c. EXTRAER PRECIO
                precio_element = producto.find_element(By.CSS_SELECTOR, "span.price-tag-fraction, span.price-tag-amount, div.poly-price__current")
                precio = precio_element.text
                
                # Almacenamos los datos en la lista principal
                datos_extraidos.append({
                    "Nombre": nombre,
                    "Precio": precio, 
                    "URL": url
                })
                time.sleep(random.uniform(0.1, 0.5)) 
            except Exception:
                # Si el precio o nombre fallan, se salta el producto.
                continue 
        
        # Muestra el total de registros acumulados hasta el momento.
        print(f"-> Datos recopilados hasta ahora: {len(datos_extraidos)} registros.")
        
        # 3. Lógica de Paginación: Buscar y hacer clic en el botón Siguiente (ROBUSTEZ FINAL)
        try:
            # 💡 MEJORA: Forzamos el scroll suave hasta el final para cargar el botón.
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(2, 3)) # Pausa para que el scroll se complete.
            
            # CLAVE: Buscamos el elemento LI con la clase 'andes-pagination__button--next' (el selector más estable)
            li_siguiente = WebDriverWait(driver, 10).until( 
                EC.element_to_be_clickable((By.CSS_SELECTOR, "li.andes-pagination__button--next"))
            )
            
            # Dentro del LI, buscamos el link 'a' y hacemos clic.
            boton_siguiente = li_siguiente.find_element(By.TAG_NAME, "a")
            
            time.sleep(random.uniform(0.5, 1.5)) # Pausa antes de hacer clic
            
            boton_siguiente.click()
            pagina_actual += 1
            print("-> Navegando a la siguiente página...")
            
            # 💡 Anti-Bloqueo 5: Tiempo de espera más largo después de la navegación
            time.sleep(random.uniform(5, 8)) 

        except Exception:
            # Si el botón no se encuentra después de 10 segundos, asumimos que terminamos.
            print("¡Paginación completa! El botón 'Siguiente' no está disponible o la búsqueda terminó.")
            break 

    print(f"\nExtracción finalizada. Total de registros recopilados: {len(datos_extraidos)}")
    driver.quit()
    return datos_extraidos

# ====================================================================================
# PUNTO DE ENTRADA DEL PROGRAMA (MANEJO DE DATOS Y EXPORTACIÓN FINAL)
# ====================================================================================

if __name__ == "__main__":
    
    # 💡 Definición de la búsqueda a ejecutar.
    termino_busqueda = "laptop" 
    
    # Ejecuta la función principal de scraping
    resultados = ejecutar_scraper(termino_busqueda)
    
    if resultados:
        print("\n--- Guardando Datos ---")
        df = pd.DataFrame(resultados)
        
        # 💡 Estética 1: Reordenar las columnas
        df = df[["Nombre", "Precio", "URL"]] 

        # 💡 CALIDAD DE DATOS: Eliminación de duplicados
        filas_antes = len(df)
        df.drop_duplicates(subset=['URL'], keep='first', inplace=True) 
        filas_despues = len(df)
        print(f"Duplicados eliminados: {filas_antes - filas_despues} registros.")
        
        # 💡 Estética 2: Limpieza y FORMATO FINAL de precios (CON DECIMALES)
        
        # Función para formatear el número grande de Mercado Libre
        def formatear_precio(precio_str):
            try:
                # 1. Limpia solo para obtener dígitos (soluciona el error 'ValueError' y elimina símbolos)
                precio_str = "".join(filter(str.isdigit, str(precio_str)))
                
                if not precio_str:
                    return 0.00
                
                # 2. Lógica Clave: Si el precio es menor a 1000 (3 dígitos), asumimos que puede tener centavos.
                # Para precios grandes, asumimos que es un entero sin centavos.
                if len(precio_str) <= 3:
                    # Precio bajo, asumimos centavos (ej. "45" -> "0.45")
                    precio_str = precio_str.zfill(3)
                    precio_formato = precio_str[:-2] + '.' + precio_str[-2:]
                else:
                    # Precio alto, lo tratamos como entero (ej. "1042634" -> 1042634.00)
                    precio_formato = precio_str + '.00'
                    
                return float(precio_formato) 

            except Exception:
                # Si algo sale mal, devolvemos 0.00 para evitar que el programa colapse
                return 0.00

        # Aplicamos la función a la columna 'Precio'
        df['Precio'] = df['Precio'].apply(formatear_precio)
        
        # Estética: Redondeamos a 2 decimales
        df['Precio'] = df['Precio'].round(2) 
        try:
            df['Precio'] = pd.to_numeric(df['Precio'])
        except ValueError:
            print("Advertencia: Algunos precios no se pudieron convertir a números.")


        # 💡 Exportación Final: Crea la carpeta 'data' si no existe
        if not os.path.exists('data'):
            os.makedirs('data')
        
        # Creamos el nombre del archivo EXCEL (.xlsx)
        nombre_archivo_excel = f"data/{termino_busqueda.replace(' ', '_')}_mercadolibre.xlsx"
        
        try:
             # GUARDAR COMO EXCEL (.XLSX) - El formato ideal para datos limpios.
             df.to_excel(nombre_archivo_excel, index=False) 
             print(f"Datos guardados exitosamente en formato Excel (.xlsx): {nombre_archivo_excel}")
             
        except Exception as e:
             print(f"ERROR al guardar: {e}")
    else:
        print("No se extrajeron datos para guardar.")