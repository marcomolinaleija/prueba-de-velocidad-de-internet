# Prueba de velocidad de internet.
# Este archivo está cubierto por la Licencia Pública General GNU
# Consulte el archivo license para obtener más detalles.
# Copyright (C) 2024 Marco Leija <marcomolinaleija@hotmail.com>

import os
import sys
import time
import threading

import globalPluginHandler
import scriptHandler
import api
import ui
import tones

# Definir el directorio de la librería y agregarlo al sys.path
lib_dir = os.path.join(os.path.dirname(__file__), "lib")
if lib_dir not in sys.path:
	sys.path.insert(0, lib_dir)

# Importar la librería speedtest después de agregar la carpeta lib al sys.path
try:
	from speedtest import Speedtest
except ImportError:
	Speedtest = None
	ui.message("No se pudo importar la librería de prueba de velocidad. Asegúrate de que está instalada correctamente en la carpeta 'lib'.")

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self):
		super(GlobalPlugin, self).__init__()
		# Inicializar estado de prueba
		self.progress = 0
		self.test_running = False

	@scriptHandler.script(
		description="Comienza la prueba de velocidad de internet.",
		gesture=None,
		category="prueba de velocidad de internet"
	)
	def script_test_speed(self, gesture):
		if self.test_running:
			ui.message("La prueba de velocidad ya está en progreso. Espera a que finalice para comenzar una nueva prueba.")
			return

		# Marcar que la prueba ha comenzado
		self.progress = 25
		self.test_running = True
		ui.message("Comenzando la prueba de velocidad de internet...")
		tones.beep(400, 100)

		# Iniciar el hilo para reproducir el sonido continuamente
		threading.Thread(target=self.play_continuous_sound, daemon=True).start()
		# Crear y lanzar un hilo para la prueba de velocidad
		threading.Thread(target=self.run_speedtest, daemon=True).start()

	def play_continuous_sound(self):
		"""Método que reproduce un sonido mediante tones de NVDA cada 2 segundos, mientras la prueba esté en progreso."""
		while self.progress < 100:
			frequency = 400 + (self.progress * 4)
			tones.beep(frequency, 100)
			# Esperar un segundo entre cada tono.
			time.sleep(1)

	def run_speedtest(self):
		"""Método que realiza la prueba de velocidad."""
		# Si la librería speedtest no se importó correctamente o no se encontró.
		if Speedtest is None:
			ui.message("La librería de prueba de velocidad no está disponible. No se puede realizar la prueba.")
			self.progress = 0
			self.test_running = False
			return

		try:
			# Se crea una instancia de Speedtest y se obtiene el mejor servidor.
			st = Speedtest()
			ui.message("Obteniendo el mejor servidor disponible.")
			self.progress = 25
			st.get_best_server()

			# Obtener la velocidad de descarga.
			ui.message("Iniciando la prueba de descarga...")
			self.progress = 50
			download_speed_mbps = st.download() / 1_000_000  # Convertir a Mbps
			ui.message(f"Velocidad de descarga: {download_speed_mbps:.2f} Mbps")

			# Obtener la velocidad de subida.
			ui.message("Iniciando la prueba de subida...")
			self.progress = 75
			upload_speed_mbps = st.upload() / 1_000_000  # Convertir a Mbps
			
			ui.message(f"Velocidad de subida: {upload_speed_mbps:.2f} Mbps")
			ui.message("Resultados copiados al portapapeles")
			api.copyToClip(f"Velocidad de descarga: {download_speed_mbps:.2f} Mbps. Velocidad de subida: {upload_speed_mbps:.2f} Mbps.")

		except Exception as e:
			ui.message(f"Un error inesperado ocurrió: {e}")

		finally:
			self.progress = 100
			tones.beep(1000, 100)  # Reproducir el tono final
			ui.message("La prueba de velocidad ha finalizado.")
			self.test_running = False

		# Limpieza de sys.path
		if lib_dir in sys.path:
			sys.path.remove(lib_dir)
