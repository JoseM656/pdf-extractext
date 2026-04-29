# pdf-extractext

## Integrantes

**Tomás Faure  | 10823**
**José Morata  | 10877**
**Braian Rojas | 10922**

## Descripción

**pdf-extractext** es una herramienta orientada a la extracción de texto desde documentos PDF utilizando técnicas de procesamiento y automatización.

El objetivo principal del proyecto es facilitar la obtención de información textual desde archivos PDF para su posterior análisis, almacenamiento o procesamiento mediante herramientas de inteligencia artificial.

Este proyecto busca resolver problemas comunes como:

- Extraer texto estructurado desde documentos PDF
- Automatizar el procesamiento de documentos
- Preparar datos para pipelines de análisis o IA
- Integrar extracción de información con bases de datos

---

## Requisitos previos

El programa se inicia levantando mongoDB en docker y en una terminal aparte fastAPI.

- Python 3.12
- uv
- Docker

---

## Instalación

```bash
uv sync
```

---

### Cómo levantar el proyecto

#### 1. Base de datos (MongoDB)

La primera vez, crear el contenedor:

```bash
docker run -d --name mongodb-pdf -p 27017:27017 mongo:7
```

Las veces siguientes, si el contenedor ya existe, solo iniciarlo:

```bash
docker start mongodb-pdf
```

> El contenedor conserva los datos entre sesiones. Solo usar `docker rm mongodb-pdf`
> si querés eliminar todos los documentos y empezar desde cero.

#### 2. API (terminal separada)

```bash
uv run uvicorn dev.servers.app:app --reload
```

Dejar esta terminal abierta mientras se usa el CLI.

#### 3. CLI

```bash
# Subir un PDF
uv run fast-pdf upload ruta/al/archivo.pdf

# Subir y ver detalles
uv run fast-pdf upload ruta/al/archivo.pdf --info

# Listar documentos
uv run fast-pdf list

# Ver texto extraído
uv run fast-pdf get <id>

# Eliminar un documento
uv run fast-pdf delete <id>
```

#### Detener el proyecto

```bash
# Detener MongoDB (conserva los datos)
docker stop mongodb-pdf

# Eliminar el contenedor y todos sus datos (opcional)
docker rm mongodb-pdf
```

## Makefile

make mongo   → levanta el contenedor de MongoDB
make server  → inicia la API con uvicorn
make start   → Iniciar el contenedor una vez ya creado 
make stop    → detiene y el contenedor de MongoDB
make remove  → borra el contenedor (elimina los datos de las sesiones)
make install → ejecuta uv sync

## Arquitectura

El proyecto sigue una arquitectura basada en **3 capas**, lo que permite separar responsabilidades y facilitar el mantenimiento.

### 1. Capa de Presentación

Encargada de la interacción con el usuario o sistema externo.

Responsabilidades:

- Recibir archivos PDF
- Iniciar el proceso de extracción
- Mostrar resultados o exportarlos

---

### 2. Capa de Lógica de Negocio

Contiene la lógica principal del sistema.

Responsabilidades:

- Procesamiento del PDF
- Extracción de texto
- Integración con herramientas de IA
- Transformación y limpieza de datos

---

### 3. Capa de Datos

Encargada del almacenamiento y persistencia.

Responsabilidades:

- Guardar texto extraído
- Conectar con bases de datos
- Manejo de almacenamiento estructurado

En este proyecto se utiliza **MongoDB** como sistema de almacenamiento.

---

## Estructura del Proyecto

A continuación se describe la estructura principal del repositorio:

| Carpeta / Archivo | Descripción |
|------------------|-------------|
| `dev/` | Código fuente principal del proyecto |
| `tests/` | Pruebas automatizadas del sistema |
| `upload` | Zonas de pruebas |
| `README.md` | Documentación principal del repositorio |
| `pyproject.toml` | Dependencias del proyecto |
| `.gitignore` | Archivos ignorados por Git |
| `Makefile` | Archivo Makefile para la automatización | 

Esta organización permite mantener una separación clara entre código, pruebas y documentación.

---

## Tecnologías Utilizadas

El proyecto utiliza diversas tecnologías para el procesamiento y análisis de documentos:

- **Python**  
  Lenguaje principal de desarrollo.

- **UV**  
  Herramienta moderna para la gestión de dependencias y entornos Python.

- **Inteligencia Artificial (IA)**  
  Utilizada para análisis avanzado del contenido extraído.

- **OpenCode**  
  Herramienta utilizada dentro del flujo de desarrollo.

- **MongoDB**  
  Base de datos NoSQL utilizada para almacenar la información extraída.

---

## Metodologías y Principios Aplicados

El proyecto sigue varias metodologías y principios de ingeniería de software para mejorar la calidad del código.

### TDD (Test Driven Development)

El desarrollo se basa en la creación de pruebas antes de implementar la funcionalidad. Esto permite:

- mejorar la calidad del código
- detectar errores temprano
- facilitar refactorizaciones

---

### 12-Factor App

Se aplican principios del modelo **12 Factor App**, orientados a construir aplicaciones escalables y mantenibles.

Algunos principios aplicados incluyen:

- configuración mediante variables de entorno
- separación entre código y configuración
- procesos stateless

---

### Principios de Desarrollo

El proyecto también sigue principios clásicos de diseño de software:

**KISS (Keep It Simple, Stupid)**  
Mantener el código simple y fácil de entender.

**DRY (Don't Repeat Yourself)**  
Evitar duplicación de lógica en el código.

**YAGNI (You Aren't Gonna Need It)**  
Implementar solo lo necesario.

**SOLID**  
Conjunto de principios para diseño orientado a objetos que mejora la mantenibilidad del software.

---

## Objetivo del Proyecto

El objetivo es construir una herramienta robusta y extensible para el procesamiento automático de documentos PDF dentro de pipelines de datos y sistemas de inteligencia artificial.
