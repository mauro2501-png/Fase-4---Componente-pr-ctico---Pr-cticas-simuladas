"""
reserva.py
Clase Reserva que integra Cliente, Servicio, duración y estado.
Implementa confirmación, cancelación y procesamiento con manejo
robusto de excepciones.
"""

from datetime import datetime
from entidades import Cliente
from servicios import Servicio
from excepciones import (
    ErrorReservaInvalida,
    ErrorOperacionNoPermitida,
    ErrorCalculo,
    ErrorParametroFaltante,
)


class Reserva:
    """
    Representa una reserva de servicio para un cliente.
    Estados posibles: pendiente → confirmada → procesada / cancelada
    """

    ESTADOS_VALIDOS = {"pendiente", "confirmada", "procesada", "cancelada"}

    def __init__(
        self,
        id_reserva: str,
        cliente: Cliente,
        servicio: Servicio,
        duracion_horas: float,
        **kwargs_servicio,
    ):
        self._id = self._validar_id(id_reserva)
        self._cliente = self._validar_cliente(cliente)
        self._servicio = self._validar_servicio(servicio)
        self._duracion_horas = self._validar_duracion(duracion_horas)
        self._kwargs_servicio = kwargs_servicio  # parámetros extra al servicio
        self._estado = "pendiente"
        self._costo_total: float = 0.0
        self._fecha_creacion: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._fecha_procesamiento: str = ""
        self._notas: str = ""

    # ── Validaciones internas ────────────────────

    @staticmethod
    def _validar_id(id_reserva: str) -> str:
        if not id_reserva or not str(id_reserva).strip():
            raise ErrorParametroFaltante("El ID de reserva no puede estar vacío.")
        return str(id_reserva).strip()

    @staticmethod
    def _validar_cliente(cliente) -> Cliente:
        if not isinstance(cliente, Cliente):
            raise ErrorReservaInvalida(
                f"Se esperaba un objeto Cliente, se recibió: {type(cliente).__name__}."
            )
        if not cliente.validar():
            raise ErrorReservaInvalida(
                f"El cliente '{cliente}' no tiene datos válidos."
            )
        return cliente

    @staticmethod
    def _validar_servicio(servicio) -> Servicio:
        if not isinstance(servicio, Servicio):
            raise ErrorReservaInvalida(
                f"Se esperaba un objeto Servicio, se recibió: {type(servicio).__name__}."
            )
        if not servicio.validar():
            raise ErrorReservaInvalida(
                f"El servicio '{servicio}' no tiene datos válidos."
            )
        return servicio

    @staticmethod
    def _validar_duracion(duracion: float) -> float:
        try:
            duracion = float(duracion)
        except (TypeError, ValueError):
            raise ErrorReservaInvalida(
                f"La duración '{duracion}' no es un número válido."
            )
        if duracion <= 0:
            raise ErrorReservaInvalida(
                f"La duración debe ser mayor a 0 horas. Se recibió: {duracion}."
            )
        if duracion > 24:
            raise ErrorReservaInvalida(
                f"La duración máxima por reserva es 24 horas. Se recibió: {duracion}."
            )
        return duracion

    # ── Propiedades de solo lectura ──────────────

    @property
    def id(self) -> str:
        return self._id

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def servicio(self) -> Servicio:
        return self._servicio

    @property
    def duracion_horas(self) -> float:
        return self._duracion_horas

    @property
    def estado(self) -> str:
        return self._estado

    @property
    def costo_total(self) -> float:
        return self._costo_total

    @property
    def fecha_creacion(self) -> str:
        return self._fecha_creacion

    @property
    def notas(self) -> str:
        return self._notas

    @notas.setter
    def notas(self, valor: str):
        self._notas = str(valor)

    # ── Operaciones principales ──────────────────

    def confirmar(self) -> float:
        """
        Confirma la reserva: calcula el costo y cambia estado a 'confirmada'.
        Retorna el costo total calculado.
        Usa try/except/else para manejar errores del servicio.
        """
        if self._estado != "pendiente":
            raise ErrorOperacionNoPermitida(
                f"Solo se puede confirmar una reserva en estado 'pendiente'. "
                f"Estado actual: '{self._estado}'."
            )
        try:
            descuento = self._cliente.descuento_por_tipo()
            self._costo_total = self._servicio.calcular_costo(
                self._duracion_horas,
                descuento=descuento,
                **self._kwargs_servicio,
            )
        except ErrorCalculo as e:
            raise ErrorReservaInvalida(
                f"No se pudo calcular el costo para la reserva '{self._id}'."
            ) from e
        else:
            self._estado = "confirmada"
            return self._costo_total

    def cancelar(self, motivo: str = "Sin motivo especificado") -> None:
        """
        Cancela la reserva si no ha sido procesada.
        Usa try/except/finally para garantizar limpieza.
        """
        try:
            if self._estado == "procesada":
                raise ErrorOperacionNoPermitida(
                    f"No se puede cancelar la reserva '{self._id}': ya fue procesada."
                )
            if self._estado == "cancelada":
                raise ErrorOperacionNoPermitida(
                    f"La reserva '{self._id}' ya está cancelada."
                )
        except ErrorOperacionNoPermitida:
            raise
        finally:
            # Este bloque siempre se ejecuta; útil para auditoría
            pass

        self._estado = "cancelada"
        self._notas = f"Cancelada: {motivo}"
        self._cliente.remover_reserva(self._id)

    def procesar(self) -> str:
        """
        Procesa la reserva confirmada.
        Usa try/except/else/finally para control completo.
        """
        resumen = ""
        try:
            if self._estado != "confirmada":
                raise ErrorOperacionNoPermitida(
                    f"Solo se puede procesar una reserva 'confirmada'. "
                    f"Estado actual: '{self._estado}'."
                )
            self._estado = "procesada"
            self._fecha_procesamiento = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        except ErrorOperacionNoPermitida:
            raise
        except Exception as e:
            raise ErrorReservaInvalida(
                f"Error inesperado al procesar la reserva '{self._id}'."
            ) from e
        else:
            resumen = self._generar_resumen()
        finally:
            # Siempre registramos intento de procesamiento
            pass
        return resumen

    def _generar_resumen(self) -> str:
        return (
            f"\n{'='*55}\n"
            f"  COMPROBANTE DE RESERVA — Software FJ\n"
            f"{'='*55}\n"
            f"  ID Reserva   : {self._id}\n"
            f"  Cliente      : {self._cliente.nombre} ({self._cliente.id})\n"
            f"  Servicio     : {self._servicio.nombre}\n"
            f"  Duración     : {self._duracion_horas} hora(s)\n"
            f"  Costo Total  : ${self._costo_total:,.2f} COP\n"
            f"  Estado       : {self._estado.upper()}\n"
            f"  Creada       : {self._fecha_creacion}\n"
            f"  Procesada    : {self._fecha_procesamiento}\n"
            f"{'='*55}\n"
        )

    def describir(self) -> str:
        return (
            f"Reserva [{self._id}] | Cliente: {self._cliente.nombre} | "
            f"Servicio: {self._servicio.nombre} | "
            f"Duración: {self._duracion_horas}h | "
            f"Estado: {self._estado.upper()} | "
            f"Costo: ${self._costo_total:,.2f}"
        )

    def __str__(self) -> str:
        return (
            f"Reserva {self._id} — {self._cliente.nombre} → "
            f"{self._servicio.nombre} [{self._estado}]"
        )
