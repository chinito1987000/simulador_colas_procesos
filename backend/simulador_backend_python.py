#!/usr/bin/env python3
"""
Simulador de Colas de Procesos - Backend Python
Sistema de Planificación de CPU para Sistemas Operativos

Autor: GERARDO ANDRES ZAPATA CABALLERO
Algoritmos implementados: FCFS, SJF, Round Robin, Prioridad
"""

import json
import random
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, asdict
from flask import Flask, jsonify, request, render_template, make_response, render_template_string
from flask_cors import CORS
import threading
import time
import os

# Configuracion logging con UTF-8
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backend.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
@dataclass
class Proceso:
    """Clase que representa un proceso en el sistema"""
    id: int
    nombre: str
    tiempo_llegada: int
    tiempo_ejecucion: int
    tiempo_restante: int
    prioridad: bool
    color: str = "#3498db"
    
    # Campos a calcular durante la simulación
    tiempo_inicio: int = 0
    tiempo_finalizacion: int = 0
    tiempo_espera: int = 0
    tiempo_respuesta: int = 0

@dataclass
class BloqueEjecucion:
    """Representa un bloque de ejecución en el diagrama de Gantt"""
    proceso: str
    inicio: int
    fin: int
    color: str

@dataclass
class ResultadoSimulacion:
    """Resultado completo de una simulación"""
    procesos: List[Proceso]
    ejecucion: List[BloqueEjecucion]
    tiempo_espera_promedio: float
    tiempo_respuesta_promedio: float
    tiempo_total: int
    throughput: float
    algoritmo: str

class SimuladorColas:
    """Simulador principal de colas de procesos"""
    
    def __init__(self):
        self.colores = [
            '#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6',
            '#1abc9c', '#34495e', '#e67e22', '#95a5a6', '#16a085'
        ]
    
    def fcfs(self, procesos: List[Proceso]) -> ResultadoSimulacion:
        """First Come First Served - El primero en llegar es el primero en ser atendido"""
        procesos_copia = [Proceso(**asdict(p)) for p in procesos]
        procesos_copia.sort(key=lambda x: x.tiempo_llegada)
        
        tiempo_actual = 0
        ejecucion = []
        
        for proceso in procesos_copia:
            tiempo_inicio = max(tiempo_actual, proceso.tiempo_llegada)
            tiempo_finalizacion = tiempo_inicio + proceso.tiempo_ejecucion
            tiempo_espera = tiempo_inicio - proceso.tiempo_llegada
            tiempo_respuesta = tiempo_espera
            
            proceso.tiempo_inicio = tiempo_inicio
            proceso.tiempo_finalizacion = tiempo_finalizacion
            proceso.tiempo_espera = tiempo_espera
            proceso.tiempo_respuesta = tiempo_respuesta
            
            ejecucion.append(BloqueEjecucion(
                proceso=proceso.nombre,
                inicio=tiempo_inicio,
                fin=tiempo_finalizacion,
                color=proceso.color
            ))
            
            tiempo_actual = tiempo_finalizacion
        
        return self._calcular_estadisticas(procesos_copia, ejecucion, "FCFS")
    
    def sjf(self, procesos: List[Proceso]) -> ResultadoSimulacion:
        """Shortest Job First - El trabajo más corto primero"""
        procesos_copia = [Proceso(**asdict(p)) for p in procesos]
        tiempo_actual = 0
        pendientes = procesos_copia.copy()
        completados = []
        ejecucion = []
        
        while pendientes:
            # Filtra procesos disponibles
            disponibles = [p for p in pendientes if p.tiempo_llegada <= tiempo_actual]
            
            if not disponibles:
                tiempo_actual = min(p.tiempo_llegada for p in pendientes)
                continue
            
            # Selecciona el proceso más corto
            proceso = min(disponibles, key=lambda x: x.tiempo_ejecucion)
            
            tiempo_inicio = tiempo_actual
            tiempo_finalizacion = tiempo_inicio + proceso.tiempo_ejecucion
            tiempo_espera = tiempo_inicio - proceso.tiempo_llegada
            tiempo_respuesta = tiempo_espera
            
            proceso.tiempo_inicio = tiempo_inicio
            proceso.tiempo_finalizacion = tiempo_finalizacion
            proceso.tiempo_espera = tiempo_espera
            proceso.tiempo_respuesta = tiempo_respuesta
            
            ejecucion.append(BloqueEjecucion(
                proceso=proceso.nombre,
                inicio=tiempo_inicio,
                fin=tiempo_finalizacion,
                color=proceso.color
            ))
            
            tiempo_actual = tiempo_finalizacion
            pendientes.remove(proceso)
            completados.append(proceso)
        
        return self._calcular_estadisticas(completados, ejecucion, "SJF")
    
    def round_robin(self, procesos: List[Proceso], quantum: int = 3) -> ResultadoSimulacion:
        """Round Robin - Asignación circular con quantum de tiempo"""
        procesos_copia = [Proceso(**asdict(p)) for p in procesos]
        procesos_copia.sort(key=lambda x: x.tiempo_llegada)
        
        tiempo_actual = 0
        cola = []
        ejecucion = []
        completados = []
        tiempos_respuesta = {}  # Para rastrear primer ejecución
        
        i = 0
        while i < len(procesos_copia) or cola:
            # Agregar procesos que han llegado
            while i < len(procesos_copia) and procesos_copia[i].tiempo_llegada <= tiempo_actual:
                cola.append(procesos_copia[i])
                i += 1
            
            if not cola:
                tiempo_actual = procesos_copia[i].tiempo_llegada
                continue
            
            proceso = cola.pop(0)
            
            # Registra tiempo de respuesta en primera ejecución
            if proceso.nombre not in tiempos_respuesta:
                tiempos_respuesta[proceso.nombre] = tiempo_actual - proceso.tiempo_llegada
            
            tiempo_ejecucion_actual = min(quantum, proceso.tiempo_restante)
            tiempo_inicio = tiempo_actual
            tiempo_fin = tiempo_actual + tiempo_ejecucion_actual
            
            ejecucion.append(BloqueEjecucion(
                proceso=proceso.nombre,
                inicio=tiempo_inicio,
                fin=tiempo_fin,
                color=proceso.color
            ))
            
            proceso.tiempo_restante -= tiempo_ejecucion_actual
            tiempo_actual = tiempo_fin
            
            # Agrega procesos que llegaron durante la ejecución
            while i < len(procesos_copia) and procesos_copia[i].tiempo_llegada <= tiempo_actual:
                cola.append(procesos_copia[i])
                i += 1
            
            if proceso.tiempo_restante > 0:
                cola.append(proceso)
            else:
                proceso.tiempo_finalizacion = tiempo_actual
                proceso.tiempo_espera = proceso.tiempo_finalizacion - proceso.tiempo_llegada - proceso.tiempo_ejecucion
                proceso.tiempo_respuesta = tiempos_respuesta[proceso.nombre]
                completados.append(proceso)
        
        return self._calcular_estadisticas(completados, ejecucion, "Round Robin")
    
    def prioridad(self, procesos: List[Proceso]) -> ResultadoSimulacion:
        """Planificación por prioridad - Alta prioridad primero"""
        procesos_copia = [Proceso(**asdict(p)) for p in procesos]
        tiempo_actual = 0
        pendientes = procesos_copia.copy()
        completados = []
        ejecucion = []
        
        while pendientes:
            # Filtra procesos disponibles
            disponibles = [p for p in pendientes if p.tiempo_llegada <= tiempo_actual]
            
            if not disponibles:
                tiempo_actual = min(p.tiempo_llegada for p in pendientes)
                continue
            
            # Selecciona por prioridad (alta prioridad primero, luego por llegada)
            proceso = max(disponibles, key=lambda x: (x.prioridad, -x.tiempo_llegada))
            
            tiempo_inicio = tiempo_actual
            tiempo_finalizacion = tiempo_inicio + proceso.tiempo_ejecucion
            tiempo_espera = tiempo_inicio - proceso.tiempo_llegada
            tiempo_respuesta = tiempo_espera
            
            proceso.tiempo_inicio = tiempo_inicio
            proceso.tiempo_finalizacion = tiempo_finalizacion
            proceso.tiempo_espera = tiempo_espera
            proceso.tiempo_respuesta = tiempo_respuesta
            
            ejecucion.append(BloqueEjecucion(
                proceso=proceso.nombre,
                inicio=tiempo_inicio,
                fin=tiempo_finalizacion,
                color=proceso.color
            ))
            
            tiempo_actual = tiempo_finalizacion
            pendientes.remove(proceso)
            completados.append(proceso)
        
        return self._calcular_estadisticas(completados, ejecucion, "Prioridad")
    
    def _calcular_estadisticas(self, procesos: List[Proceso], ejecucion: List[BloqueEjecucion], algoritmo: str) -> ResultadoSimulacion:
        """Calcula las estadísticas finales de la simulación"""
        tiempo_espera_promedio = sum(p.tiempo_espera for p in procesos) / len(procesos)
        tiempo_respuesta_promedio = sum(p.tiempo_respuesta for p in procesos) / len(procesos)
        tiempo_total = max(p.tiempo_finalizacion for p in procesos)
        throughput = len(procesos) / tiempo_total if tiempo_total > 0 else 0
        
        return ResultadoSimulacion(
            procesos=procesos,
            ejecucion=ejecucion,
            tiempo_espera_promedio=tiempo_espera_promedio,
            tiempo_respuesta_promedio=tiempo_respuesta_promedio,
            tiempo_total=tiempo_total,
            throughput=throughput,
            algoritmo=algoritmo
        )
    
    def generar_procesos_aleatorios(self, cantidad: int = 5) -> List[Proceso]:
        """Genera procesos aleatorios para pruebas"""
        procesos = []
        for i in range(cantidad):
            proceso = Proceso(
                id=i + 1,
                nombre=f"P{i + 1}",
                tiempo_llegada=random.randint(0, 10),
                tiempo_ejecucion=random.randint(1, 10),
                tiempo_restante=0,
                prioridad=random.choice([True, False]),
                color=self.colores[i % len(self.colores)]
            )
            proceso.tiempo_restante = proceso.tiempo_ejecucion
            procesos.append(proceso)
        return procesos

# Inicializa Flask y CORS correctamente
def obtener_ruta_absoluta(relativa):
    """Permite que Flask encuentre recursos dentro del .exe de PyInstaller"""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relativa)

# Intentar configurar template_folder, pero no fallar si no existe
try:
    template_folder = obtener_ruta_absoluta("templates")
    if not os.path.exists(template_folder):
        template_folder = None
except:
    template_folder = None

#static_folder = obtener_ruta_absoluta("static") para css y js no incluye al estar todo en el HTML

app = Flask(__name__, template_folder=template_folder)

#app = Flask(__name__)
CORS(app)

# Crear instancia del simulador
simulador = SimuladorColas()

@app.route('/health')
def health():
    """Endpoint de verificación de salud"""
    return jsonify({'status': 'ok', 'message': 'Backend funcionando correctamente'})

@app.route('/')
def home():
    return render_template("simulador_conectado.html")

@app.route('/index')
def index():
    """Documentación API"""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Simulador de Colas de Procesos</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .method { color: #2ecc71; font-weight: bold; }
            .url { color: #3498db; font-family: monospace; }
        </style>
    </head>
    <body>
        <h1>🖥️ API Simulador de Colas de Procesos</h1>
        <p>Backend Python para simulación de algoritmos de planificación de CPU</p>
        
        <h2>Endpoints Disponibles:</h2>
        
        <div class="endpoint">
            <span class="method">POST</span> <span class="url">/simular</span>
            <p>Simula la ejecución de procesos con el algoritmo especificado.</p>
            <p><strong>Body:</strong> {"procesos": [...], "algoritmo": "FCFS|SJF|RR|PRIORITY", "quantum": 3}</p>
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> <span class="url">/generar_aleatorios/{cantidad}</span>
            <p>Genera procesos aleatorios para pruebas.</p>
        </div>
        
        <div class="endpoint">
            <span class="method">POST</span> <span class="url">/comparar</span>
            <p>Compara todos los algoritmos con los mismos procesos.</p>
            <p><strong>Body:</strong> {"procesos": [...], "quantum": 3}</p>
        </div>
        
        <h2>Ejemplo de Proceso:</h2>
        <pre>{
  "id": 1,
  "nombre": "P1",
  "tiempo_llegada": 0,
  "tiempo_ejecucion": 5,
  "tiempo_restante": 5,
  "prioridad": false,
  "color": "#3498db"
}</pre>
    </body>
    </html>
    """)

#@app.route('/simular', methods=['POST', 'OPTIONS'])
@app.route('/simular', methods=['POST'])
def simular():
    """Endpoint para simular procesos"""
    try:
        data = request.get_json()
        procesos_data = data.get('procesos', [])
        algoritmo = data.get('algoritmo', 'FCFS')
        quantum = data.get('quantum', 3)
        
        print(f" Recibida solicitud de simulación: {algoritmo}")
        print(f" Procesos recibidos: {len(procesos_data)}")
        
        # Convertir datos a objetos Proceso
        procesos = []
        for p_data in procesos_data:
            proceso = Proceso(**p_data)
            procesos.append(proceso)
        
        # Ejecutar simulación
        if algoritmo == 'FCFS':
            resultado = simulador.fcfs(procesos)
        elif algoritmo == 'SJF':
            resultado = simulador.sjf(procesos)
        elif algoritmo == 'RR':
            resultado = simulador.round_robin(procesos, quantum)
        elif algoritmo == 'PRIORITY':
            resultado = simulador.prioridad(procesos)
        else:
            return jsonify({'error': 'Algoritmo no válido'}), 400
        
        print(f" Simulación {algoritmo} completada exitosamente")
        
        # Convertir resultado a diccionario para JSON
        return jsonify({
            'procesos': [asdict(p) for p in resultado.procesos],
            'ejecucion': [asdict(b) for b in resultado.ejecucion],
            'estadisticas': {
                'tiempo_espera_promedio': resultado.tiempo_espera_promedio,
                'tiempo_respuesta_promedio': resultado.tiempo_respuesta_promedio,
                'tiempo_total': resultado.tiempo_total,
                'throughput': resultado.throughput,
                'algoritmo': resultado.algoritmo
            }
        })
        
    except Exception as e:
        print(f" Error en simulación: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/generar_aleatorios/<int:cantidad>', methods=['GET', 'OPTIONS'])
def generar_aleatorios(cantidad):
    """Genera procesos aleatorios"""
    try:
        print(f" Solicitud para generar {cantidad} procesos aleatorios")
        
        if cantidad > 20:
            return jsonify({'error': 'Máximo 20 procesos'}), 400
            
        procesos = simulador.generar_procesos_aleatorios(cantidad)
        
        print(f" Generados {len(procesos)} procesos aleatorios")
        
        return jsonify([asdict(p) for p in procesos])
        
    except Exception as e:
        print(f" Error generando procesos: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/comparar', methods=['POST'])
def comparar():
    """Compara todos los algoritmos con los mismos procesos"""
    try:
        data = request.get_json()
        procesos_data = data.get('procesos', [])
        quantum = data.get('quantum', 3)
        
        print(f" Solicitud de comparación con {len(procesos_data)} procesos")
        
        # Convertir datos a objetos Proceso
        procesos = []
        for p_data in procesos_data:
            proceso = Proceso(**p_data)
            procesos.append(proceso)
        
        # Ejecutar todos los algoritmos
        resultados = {}
        resultados['FCFS'] = simulador.fcfs(procesos)
        resultados['SJF'] = simulador.sjf(procesos)
        resultados['RR'] = simulador.round_robin(procesos, quantum)
        resultados['PRIORITY'] = simulador.prioridad(procesos)
        
        print(" Comparación completada para todos los algoritmos")
        
        # Convertir a JSON
        comparacion = {}
        for alg, resultado in resultados.items():
            comparacion[alg] = {
                'tiempo_espera_promedio': resultado.tiempo_espera_promedio,
                'tiempo_respuesta_promedio': resultado.tiempo_respuesta_promedio,
                'tiempo_total': resultado.tiempo_total,
                'throughput': resultado.throughput,
                'ejecucion': [asdict(b) for b in resultado.ejecucion]
            }
        
        return jsonify(comparacion)
        
    except Exception as e:
        print(f" Error en comparación: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    response = make_response(jsonify({'error': 'Endpoint no encontrado'}), 404)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.errorhandler(500)
def internal_error(error):
    response = make_response(jsonify({'error': 'Error interno del servidor'}), 500)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

def main():
    """Función principal para pruebas en consola"""
    print("Simulador de Colas de Procesos - Prueba en Consola")
    print("=" * 60)
    
    # Crear simulador
    sim = SimuladorColas()
    
    # Generar procesos de ejemplo
    procesos = [
        Proceso(1, "P1", 0, 5, 5, False, "#3498db"),
        Proceso(2, "P2", 1, 3, 3, True, "#e74c3c"),
        Proceso(3, "P3", 2, 8, 8, False, "#2ecc71"),
        Proceso(4, "P4", 3, 6, 6, False, "#f39c12")
    ]
    
    print(f"Procesos de entrada: {len(procesos)}")
    for p in procesos:
        prioridad_str = "ALTA" if p.prioridad else "NORMAL"
        print(f"  {p.nombre}: Llegada={p.tiempo_llegada}, Ejecución={p.tiempo_ejecucion}, Prioridad={prioridad_str}")
    
    print("\n" + "=" * 60)
    
    # Probar cada algoritmo
    algoritmos = [
        ("FCFS", sim.fcfs),
        ("SJF", sim.sjf),
        ("Round Robin", lambda p: sim.round_robin(p, 3)),
        ("Prioridad", sim.prioridad)
    ]
    
    for nombre, funcion in algoritmos:
        print(f"\n {nombre}")
        print("-" * 40)
        
        resultado = funcion(procesos.copy())
        
        print(f"Tiempo espera promedio: {resultado.tiempo_espera_promedio:.2f}")
        print(f"Tiempo respuesta promedio: {resultado.tiempo_respuesta_promedio:.2f}")
        print(f"Tiempo total: {resultado.tiempo_total}")
        print(f"Throughput: {resultado.throughput:.2f} proc/seg")
        
        print("Orden de ejecución:")
        for bloque in resultado.ejecucion:
            print(f"  {bloque.proceso}: {bloque.inicio}-{bloque.fin}")

if __name__ == '__main__':
    
    
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # Ejecuta pruebas en consola
        main()
    else:
        # Ejecuta servidor web
        print(" Iniciando servidor Flask...")
        print(" API disponible en: http://localhost:5000")
        print(" Frontend HTML puede conectarse a esta API")
        print(" Documentación en: http://localhost:5000/index")
        print("=" * 50)
        #app.run(debug=True, host='0.0.0.0', port=5000)
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
