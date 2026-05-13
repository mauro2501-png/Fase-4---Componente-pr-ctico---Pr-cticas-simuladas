"""
logger.py
Módulo de registro de eventos y errores para el Sistema Software FJ.
"""

import os
from datetime import datetime


class Logger:
    """
    Clase encargada de registrar todos los eventos y errores del sistema
    en un archivo de logs con marca de tiempo.
    """

    _instancia = None  # Patrón Singleton

    def __new__(cls, archivo_log: str = "software_fj.log"):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._inicializar(archivo_log)
        return cls._instancia

    def _inicializar(self, archivo_log: str):
        self._archivo = archivo_log
        self._registrar_encabezado()

    def _timestamp(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _registrar_encabezado(self):
        try:
            with open(self._archivo, "a", encoding="utf-8") as f:
                f.write("\n" + "=" * 60 + "\n")
                f.write(f"  SESIÓN INICIADA: {self._timestamp()}\n")
                f.write("  Sistema Software FJ — Gestión de Reservas\n")
                f.write("=" * 60 + "\n")
        except OSError as e:
            print(f"[LOGGER] No se pudo escribir encabezado: {e}")

    def _escribir(self, nivel: str, mensaje: str):
        linea = f"[{self._timestamp()}] [{nivel}] {mensaje}\n"
        try:
            with open(self._archivo, "a", encoding="utf-8") as f:
                f.write(linea)
        except OSError as e:
            print(f"[LOGGER] Error al escribir en log: {e}")
        # También imprimir en consola para visibilidad
        print(linea, end="")

    def info(self, mensaje: str):
        """Registra un evento informativo."""
        self._escribir("INFO ", mensaje)

    def advertencia(self, mensaje: str):
        """Registra una advertencia."""
        self._escribir("ADVERTENCIA", mensaje)

    def error(self, mensaje: str):
        """Registra un error."""
        self._escribir("ERROR", mensaje)

    def critico(self, mensaje: str):
        """Registra un error crítico."""
        self._escribir("CRITICO", mensaje)

    def separador(self, titulo: str = ""):
        """Escribe un separador visual en el log."""
        linea = f"\n--- {titulo} ---\n" if titulo else "\n" + "-" * 40 + "\n"
        try:
            with open(self._archivo, "a", encoding="utf-8") as f:
                f.write(linea)
        except OSError:
            pass
        print(linea, end="")
