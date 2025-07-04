# Simulador de Planificación de CPU
## Descripción
Sistema de simulación de algoritmos de planificación de CPU para Sistemas Operativos. 
Aplicación de escritorio que permite visualizar y analizar el comportamiento de 
diferentes algoritmos de planificación de procesos.

**Autor:** GERARDO ANDRES ZAPATA CABALLERO

## Algoritmos Implementados

- **FCFS (First Come First Served)** - Primero en llegar, primero en ser servido
- **SJF (Shortest Job First)** - Trabajo más corto primero
- **Round Robin** - Algoritmo circular con quantum de tiempo
- **Prioridad** - Planificación basada en prioridades de procesos

## Características

- Interfaz gráfica moderna basada en HTML/CSS/JavaScript
- Backend en Python con Flask
- Visualización en tiempo real de la ejecución de procesos
- Cálculo automático de métricas (tiempo de espera, tiempo de respuesta, etc.)
- Aplicación de escritorio standalone (requiere navegador edgechromium(CHROME))
- Multiplataforma (Windows, Linux, macOS)

## Requisitos 

### Desarrollo
- Python 3.8 o superior
- Windows 10/11, Linux, o macOS
- 4GB RAM mínimo
- 100MB espacio libre en disco

### Ejecución (Ejecutable)
- Windows 10/11 (para .exe)
- 4GB RAM mínimo
- 50MB espacio libre en disco

## Instalación

### Opción 1: Ejecutar desde código fuente

1. **Clonar el repositorio:**
   ```bash
   git clone <url-del-repositorio>
   cd simulador-cpu
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar la aplicación:**
   ```bash
   python launcher.py
   ```

### Opción 2: Usar ejecutable (Windows)

1. Descargar el archivo `SimuladorCPU.exe` desde releases
2. Ejecutar directamente el archivo `.exe`

### Opción 3: Compilar ejecutable

1. **Instalar PyInstaller:**
   ```bash
   pip install pyinstaller
   ```

2. **Compilar:**
   ```bash
   pyinstaller launcher.spec
   ```

3. **El ejecutable estará en:**
   ```
   dist/SimuladorCPU.exe
   ```

## Estructura del Proyecto

```
simulador-cpu/
├── launcher.py              # Launcher principal
├── launcher.spec           # Configuración PyInstaller
├── requirements.txt        # Dependencias Python
├── README.md              # Este archivo
│
├── frontend/              # Interfaz de usuario
│   ├── simulador_conectado.html
│
├── backend/               # Lógica del servidor
│   ├── simulador_backend_python.py
│	├── dist/               # Lógica del servidor
│   	├── simulador_backend_python.exe #ejecutable para levantar conexion
│   ├── templates/        # Templates Flask
│		├── simulador_conectado.html
│
├── dist/               # Lógica del servidor
│   	├── SimuladorCPU.exe #ejecutable
└── logs/                 # Archivos de log
    └── launcher.log
```

## Uso de la Aplicación

1. **Iniciar la aplicación:**
   - Desde código: `python launcher.py`
   - Desde ejecutable: doble clic en `SimuladorCPU.exe`

2. **Agregar procesos:**
   - Especificar tiempo de llegada
   - Definir tiempo de ráfaga (burst time)
   - Asignar prioridad (si aplica)

3. **Seleccionar algoritmo:**
   - FCFS, SJF, Round Robin, o Prioridad
   - Configurar quantum para Round Robin

4. **Ejecutar simulación:**
   - Ver diagrama de Gantt en tiempo real
   - Analizar métricas calculadas
   - Comparar diferentes algoritmos

## Métricas Calculadas

- **Tiempo de Espera:** Tiempo que un proceso espera en la cola
- **Tiempo de Respuesta:** Tiempo desde llegada hasta primera ejecución
- **Tiempo de Retorno:** Tiempo total desde llegada hasta finalización
- **Throughput:** Procesos completados por unidad de tiempo
- **Utilización de CPU:** Porcentaje de tiempo que la CPU está ocupada

## Solución de Problemas

### La aplicación no inicia

1. **Verificar logs:**
   ```bash
   tail -f launcher.log
   ```

2. **Problemas comunes:**
   - Puerto 5000 ocupado → El backend cambiará automáticamente de puerto
   - Archivos faltantes → Verificar estructura de carpetas
   - Permisos → Ejecutar como administrador si es necesario

### Backend no responde

1. **Verificar que Flask esté instalado:**
   ```bash
   python -c "import flask; print('Flask OK')"
   ```

2. **Verificar puerto:**
   ```bash
   netstat -an | grep :5000
   ```

3. **Reiniciar aplicación:**
   - Cerrar completamente
   - Esperar 5 segundos
   - Volver a abrir

### Problemas de visualización

1. **Actualizar navegador interno:**
   - La aplicación usa WebView2 en Windows
   - Instalar Microsoft Edge WebView2 Runtime
  

2. **Problemas de renderizado:**
   - Verificar resolución de pantalla
   - Ajustar escalado de Windows si es necesario

## Desarrollo

### Configurar entorno de desarrollo

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### Estructura de desarrollo

```bash
# Ejecutar en modo desarrollo
python launcher.py

# Ejecutar solo backend (para pruebas)
cd backend
python simulador_backend_python.py

# Ejecutar tests (si existen)
python -m pytest tests/
```

### Contribuir

1. Fork del proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request


## Contacto

**Autor:** GERARDO ANDRES ZAPATA CABALLERO  
**Email:** gerardozapatacaballer@gmail.com]  
**Proyecto:** Simulador de Planificación de CPU para Sistemas Operativos

## Historial de Versiones

### v1.0.0 (Actual)
- Implementación inicial
- Algoritmos FCFS, SJF, Round Robin, Prioridad
- Interfaz gráfica completa
- Generación de ejecutable standalone



- Interfaz inspirada en herramientas educativas modernas
- Comunidad de Python y Flask por las librerías utilizadas