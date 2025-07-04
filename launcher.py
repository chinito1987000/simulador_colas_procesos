"""
Simulador de Colas de Procesos - Backend Python
Sistema de Planificación de CPU para Sistemas Operativos

Autor: GERARDO ANDRES ZAPATA CABALLERO
Algoritmos implementados: FCFS, SJF, Round Robin, Prioridad
"""
import webview
import threading
import sys
import subprocess
import os
import time
import atexit
import signal
import requests
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('launcher.log'),
        logging.StreamHandler()
    ]
)

class SimuladorLauncher:
    def __init__(self):
        self.backend_process = None
        self.setup_paths()
        self.setup_cleanup()
        
    def setup_paths(self):
        """Configura todas las rutas necesarias"""
        self.current_dir = Path(__file__).parent.absolute()
        
        # Si está empaquetado, usar _MEIPASS
        if getattr(sys, 'frozen', False):
            self.bundle_dir = Path(sys._MEIPASS)
            self.frontend_html = self.bundle_dir / "frontend" / "simulador_conectado.html"
            self.backend_exe = self.bundle_dir / "backend" / "simulador_backend_python.exe"
            self.backend_py = self.bundle_dir / "backend" / "simulador_backend_python.py"
        else:
            self.frontend_html = self.current_dir / "frontend" / "simulador_conectado.html"
            self.backend_exe = self.current_dir / "backend" / "simulador_backend_python.exe"
            self.backend_py = self.current_dir / "backend" / "simulador_backend_python.py"
        
        # Verificar que los archivos existan
        if not self.frontend_html.exists():
            raise FileNotFoundError(f"Frontend no encontrado: {self.frontend_html}")
            
        if not self.backend_py.exists() and not self.backend_exe.exists():
            raise FileNotFoundError("No se encontró el backend (ni .py ni .exe)")
    
    def setup_cleanup(self):
        """Configura la limpieza al cerrar la aplicación"""
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Maneja señales del sistema para cierre limpio"""
        logging.info(f"Recibida señal {signum}, cerrando aplicación...")
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """Limpia recursos y termina procesos"""
        if self.backend_process:
            try:
                logging.info("Terminando proceso backend...")
                self.backend_process.terminate()
                
                # Esperar a que termine, sino forzar
                try:
                    self.backend_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logging.warning("Backend no terminó, forzando cierre...")
                    self.backend_process.kill()
                    
            except Exception as e:
                logging.error(f"Error al terminar backend: {e}")
    
    def iniciar_backend(self):
        """Inicia el proceso backend con diagnóstico completo"""
        try:
            if getattr(sys, 'frozen', False):
                # En ejecutable empaquetado, preferir .exe si existe
                if self.backend_exe.exists():
                    logging.info("Iniciando backend desde ejecutable...")
                    self.backend_process = subprocess.Popen(
                        [str(self.backend_exe)],
                        cwd=str(self.backend_exe.parent),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                else:
                    logging.info("Iniciando backend desde Python (en ejecutable)...")
                    self.backend_process = subprocess.Popen(
                        [sys.executable, str(self.backend_py)],
                        cwd=str(self.backend_py.parent),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
            else:
                # En desarrollo, usar Python
                logging.info("Iniciando backend desde Python...")
                logging.info(f"Ejecutando: {sys.executable} {self.backend_py}")
                logging.info(f"Directorio de trabajo: {self.backend_py.parent}")
                
                # Verificar que Python puede importar los módulos necesarios
                test_cmd = [sys.executable, "-c", "import flask; print('Flask disponible')"]
                try:
                    result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=5)
                    if result.returncode != 0:
                        logging.error(f"Error al importar Flask: {result.stderr}")
                    else:
                        logging.info("Flask disponible para importar")
                except Exception as e:
                    logging.warning(f"No se pudo verificar Flask: {e}")
                
                self.backend_process = subprocess.Popen(
                    [sys.executable, str(self.backend_py)],
                    cwd=str(self.backend_py.parent),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
            logging.info(f"Backend iniciado con PID: {self.backend_process.pid}")
            
            # Verificación temprana
            time.sleep(2)
            if self.backend_process.poll() is not None:
                stdout, stderr = self.backend_process.communicate()
                logging.error(f"Backend terminó inmediatamente con código: {self.backend_process.returncode}")
                if stdout:
                    logging.error(f"STDOUT: {stdout}")
                if stderr:
                    logging.error(f"STDERR: {stderr}")
                return False
            
            return True
            
        except FileNotFoundError as e:
            logging.error(f"Archivo no encontrado: {e}")
            raise
        except Exception as e:
            logging.error(f"Error al iniciar backend: {e}")
            raise
    
    def verificar_backend(self, timeout=30, port=5000):
        """Verifica que el backend esté respondiendo"""
        logging.info(f"Verificando backend en puerto {port}...")
        
        for i in range(timeout):
            try:
                # Verificar si el proceso sigue vivo
                if self.backend_process and self.backend_process.poll() is not None:
                    try:
                        stdout, stderr = self.backend_process.communicate(timeout=1)
                        logging.error(f"Backend terminó con código: {self.backend_process.returncode}")
                        if stdout:
                            logging.error(f"STDOUT: {stdout}")
                        if stderr:
                            logging.error(f"STDERR: {stderr}")
                    except Exception as e:
                        logging.error(f"No se pudo obtener salida del proceso: {e}")
                    
                    logging.error("El proceso backend ha terminado inesperadamente")
                    return False
                
                # Intentar conectar al backend
                response = requests.get(f"http://localhost:{port}/health", timeout=2)
                if response.status_code == 200:
                    logging.info("Backend respondiendo correctamente")
                    return True
                    
            except requests.exceptions.ConnectionError:
                pass
            except requests.exceptions.Timeout:
                pass
            except requests.exceptions.RequestException as e:
                logging.warning(f"Error de conexión: {e}")
            
            if i == 0:
                logging.info("Esperando a que el backend inicie...")
            elif i % 5 == 0:
                logging.info(f"Esperando backend... ({i}/{timeout}s)")
                
            time.sleep(1)
        
        logging.error(f"Backend no respondió después de {timeout} segundos")
        return False
    
    def crear_ventana(self):
        """Crea la ventana principal de la aplicación"""
        try:
            logging.info("Creando ventana principal...")
            
            # Configurar la ventana
            webview.create_window(
                title="Simulador de Planificación de CPU",
                url=str(self.frontend_html.as_uri()),  # Usar as_uri() para URL correcta
                width=1200,
                height=800,
                min_size=(900, 600),
                resizable=True,
                shadow=True,
                on_top=False,
                text_select=False
            )
            
            # Iniciar webview con configuración optimizada
            webview.start(
                gui='edgechromium' if sys.platform == 'win32' else None,
                debug=False,
                http_server=False
            )
            
        except Exception as e:
            logging.error(f"Error al crear ventana: {e}")
            raise
    
    def ejecutar(self):
        """Ejecuta la aplicación completa"""
        try:
            logging.info("=== Iniciando Simulador de Planificación de CPU ===")
            
            # Iniciar backend directamente (no en hilo separado)
            if not self.iniciar_backend():
                logging.error("No se pudo iniciar el backend")
                return False
            
            # Esperar a que el backend esté listo
            if not self.verificar_backend():
                logging.error("Backend no está respondiendo correctamente")
                return False
            
            # Crear y mostrar ventana principal
            self.crear_ventana()
            
            logging.info("Aplicación cerrada correctamente")
            return True
            
        except KeyboardInterrupt:
            logging.info("Aplicación interrumpida por el usuario")
            return False
        except Exception as e:
            logging.error(f"Error crítico: {e}")
            return False
        finally:
            self.cleanup()

def main():
    """Función principal"""
    try:
        launcher = SimuladorLauncher()
        success = launcher.ejecutar()
        sys.exit(0 if success else 1)
        
    except FileNotFoundError as e:
        logging.error(f"Archivo requerido no encontrado: {e}")
        input("Presiona Enter para salir...")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error fatal: {e}")
        input("Presiona Enter para salir...")
        sys.exit(1)

if __name__ == "__main__":
    main()