# Sistema de Inventario en Python

Este es un programa de escritorio simple y moderno para gestionar el inventario de una tienda.

## Requisitos Previos

Parece que no tienes Python instalado. Para ejecutar este programa, necesitas instalarlo:

1.  Ve a [python.org/downloads](https://www.python.org/downloads/).
2.  Descarga la versión más reciente para Windows.
3.  **IMPORTANTE**: Al instalar, asegúrate de marcar la casilla **"Add Python to PATH"** (Agregar Python al PATH).

## Instalación

Una vez instalado Python, abre una terminal (PowerShell o CMD) en esta carpeta y ejecuta:

```bash
pip install -r requirements.txt
```

Esto instalará `customtkinter` (para la interfaz gráfica) y otras librerías necesarias.

## Cómo ejecutar

Para iniciar el programa, ejecuta:

```bash
python main.py
```

## Características

-   **Dashboard**: Navegación simple.
-   **Agregar Producto**: Formulario para ingresar nuevos items.
-   **Ver Inventario**: Lista de todos los productos con opción de eliminar.
-   **Base de Datos**: Los datos se guardan automáticamente en `inventory.db` (se crea solo).
