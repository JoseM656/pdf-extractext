# pdf-extractext

## Descripción

**pdf-extractext** es una herramienta orientada a la extracción de texto desde documentos PDF utilizando técnicas de procesamiento y automatización.

El objetivo principal del proyecto es facilitar la obtención de información textual desde archivos PDF para su posterior análisis, almacenamiento o procesamiento mediante herramientas de inteligencia artificial.

Este proyecto busca resolver problemas comunes como:

- Extraer texto estructurado desde documentos PDF
- Automatizar el procesamiento de documentos
- Preparar datos para pipelines de análisis o IA
- Integrar extracción de información con bases de datos

---

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
| `docs/` | Documentación adicional del proyecto |
| `README.md` | Documentación principal del repositorio |
| `requirements.txt` / `pyproject.toml` | Dependencias del proyecto |
| `.gitignore` | Archivos ignorados por Git |

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