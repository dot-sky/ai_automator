# Proyecto Staff HTML Analyzer

Este proyecto automatiza la extracción y análisis de información de staff desde HTML generado por un script R, utilizando Python y agentes de inteligencia artificial.

## Requisitos

- Python 3.11 instalado ([descargar aquí](https://www.python.org/downloads/))
- R instalado (para ejecutar scripts `.R`)
- Acceso a la API de Gemini (Google AI) y su API KEY

## 1. Clona el repositorio

```bash
git clone https://github.com/paukiss/hackaton-coderoad.git
cd hackaton-coderoad
````

## 2. Crea un entorno virtual con Python 3.11

```bash
python3.11 -m venv venv
```


## 3. Activa el entorno virtual

* En **Linux/Mac**:

  ```bash
  source venv/bin/activate
  ```

* En **Windows**:

  ```bat
  venv\Scripts\activate
  ```

## 4. Instala las dependencias

```bash
pip install -r requirements.txt
```

## 5. Configura tus variables de entorno

Asegúrate de tener tu clave de API para Gemini en la variable de entorno `GOOGLE_API_KEY`.
Puedes exportarla así en Linux/Mac:

```bash
export GOOGLE_API_KEY="tu_clave_aqui"
```

O en Windows (CMD):

```bat
set GOOGLE_API_KEY=tu_clave_aqui
```

## 6. Ejecuta el proyecto

```bash
python main.py
```

