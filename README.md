# 🛒 Web Scraper Semi-Avanzado: Mercado Libre (Python + Selenium)

Este proyecto demuestra un Web Scraper robusto y modular capaz de extraer información de productos de Mercado Libre, un sitio dinámico que requiere técnicas de automatización avanzadas.

---

## 🌟 Características

* **Anti-Bloqueo:** Simula comportamiento humano (pausas aleatorias, User-Agent real) para evitar ser detectado.
* **Paginación Automática:** Recorre automáticamente todas las páginas de resultados (scroll forzado y esperas explícitas).
* **Robustez de Extracción:** Utiliza selectores flexibles y manejo de excepciones para saltar anuncios y extraer datos de tarjetas con estructuras variables.
* **Calidad de Datos:** Elimina duplicados por URL y limpia los precios (manejo de enteros y decimales) para asegurar precisión.
* **Exportación Profesional:** Guarda los resultados limpios en un archivo Excel (`.xlsx`).

## 🛠️ Tecnologías Utilizadas

* **Python 3.x**
* **Selenium:** Para la automatización del navegador (manejo de JavaScript, scroll, clics).
* **Pandas:** Para la manipulación, limpieza y exportación de datos.
* **openpyxl:** Librería necesaria para exportar a formato `.xlsx`.

## ⚙️ Cómo Ejecutar el Proyecto

### 1. Preparación del Entorno

1.  Clona este repositorio:
    ```bash
    git clone [https://github.com/lk02-bz/Python-MercadoLibre-Scraper.git](https://github.com/lk02-bz/Python-MercadoLibre-Scraper.git)
    cd Python-MercadoLibre-Scraper
    ```
2.  Crea y activa el Entorno Virtual:
    ```bash
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    ```
3.  Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```
    *(Nota: Asegúrate de que tu archivo `requirements.txt` esté actualizado. Puedes generarlo con `pip freeze > requirements.txt`)*

### 2. Ejecución

Ejecuta el script principal desde la terminal (con el entorno `.venv` activo):

```bash
python main.py