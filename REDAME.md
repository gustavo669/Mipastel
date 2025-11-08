Sistema de Gestión de Pedidos "Mi Pastel" 

"Mi Pastel" es un sistema de gestión de pedidos híbrido diseñado para pastelerías. Combina una aplicación web (FastAPI) para que las sucursales ingresen pedidos y una potente aplicación de escritorio (PySide6) para que la administración central gestione ventas, precios y reportes.

Características Principales

El sistema está dividido en dos componentes principales que se ejecutan simultáneamente:

1. Aplicación de Administración (Escritorio - PySide6)

Es el centro de control para los administradores.

Interfaz Moderna: Tema oscuro completo (estilo "Dracula" Morado/Rosado) con fuentes limpias (Segoe UI / Lato).

Gestión CRUD Completa: Funcionalidad total de Crear, Leer, Editar y Eliminar para pedidos Normales y de Clientes.

Gestión de Precios Centralizada: Un diálogo emergente (Administrar Precios) permite editar la lista de precios maestra directamente en la base de datos.

Filtrado Avanzado: Permite filtrar los pedidos por fecha y por sucursal.

Reportes PDF Avanzados: Genera dos tipos de reportes en PDF:

Reporte de Clientes: Un listado detallado con columnas personalizadas (Sabor, ID, Cantidad, Sucursal, Detalles, etc.).

Reporte de Normales: Incluye dos tablas pivot:

Una tabla de Sabor-Tamaño vs. Sucursales (excluyendo medias planchas).

Una tabla de Total por Sabor vs. Sucursales (incluyendo todos los tamaños) con una fila de "TOTAL GENERAL".
 
Aplicación Web (Servidor - FastAPI)

Es la interfaz ligera que usan las sucursales para ingresar nuevos pedidos.

Formularios de Ingreso: Páginas separadas para "Pasteles Normales" y "Pedidos de Clientes".

Cálculo Automático de Precios: Los formularios consultan la base de datos en tiempo real para calcular el precio unitario y total.

Subida de Imágenes: El formulario de clientes permite adjuntar una foto para el pedido, la cual se guarda en el servidor.

Validación: El backend valida los datos antes de ingresarlos a la base de datos.

3. Base de Datos (SQL Server)

Arquitectura de Doble Base de Datos:

MiPastel: Almacena PastelesNormales y la lista maestra PastelesPrecios.

MiPastel_Clientes: Almacena PastelesClientes.

Triggers SQL: Un trigger en la tabla PastelesClientes calcula automáticamente la columna total (cantidad * precio) al insertar o actualizar un pedido, asegurando la integridad de los datos.

IDs Personalizados: Todos los pedidos (normales y clientes) inician con un ID de 5 dígitos (IDENTITY(10000, 1)).

4. Arquitectura de Código

Configuración Centralizada (config.py): Un único archivo define las listas maestras de SUCURSALES, SABORES y TAMANOS. Esto permite que la app web, la app de admin y los reportes usen exactamente los mismos datos.

Lanzador Unificado (run.py): Un script principal que inicia el servidor web FastAPI en un subproceso y luego lanza la aplicación de escritorio PySide6. Al cerrar la ventana de admin, el servidor también se detiene.

Tecnologías Utilizadas

Backend (Servidor Web): FastAPI, Uvicorn

Frontend (App Admin): PySide6 (Qt for Python)

Base de Datos: SQL Server (conectado vía pyodbc)

Reportes: ReportLab

Lenguaje: Python 3

Estructura del Proyecto

/Mipastel/
│
├── admin/
│   ├── admin_app.py     # Aplicación principal de admin (UI y lógica)
│   └── dialogos.py      # Diálogos emergentes (Nuevo/Editar/Precios)
│
├── routers/
│   ├── admin.py         # Endpoints API para la app de admin
│   ├── clientes.py      # Endpoints para el formulario web de clientes
│   └── normales.py      # Endpoints para el formulario web de normales
│
├── templates/
│   ├── index.html       # Formulario web principal
│   ├── exito.html       # Página de "Pedido guardado"
│   └── admin.html       # Página de "Panel de administración - Solo Lectura"
│
├── static/
│   └── uploads/         # Aquí se guardan las fotos de clientes
│
├── app.py               # Servidor Web FastAPI (app principal)
├── config.py            # Listas maestras (Sabores, Sucursales)
├── database.py          # Lógica de conexión y CRUD con SQL Server
├── reportes.py          # Lógica de generación de PDFs con ReportLab
├── run.py               # El lanzador que inicia todo
├── Mipastel.sql         # Script para crear las base de datos
└── requirements.txt     # Dependencias 

