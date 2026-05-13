"""
gestor.py
Clase GestorSistema: administra clientes, servicios y reservas.
Actúa como repositorio central en memoria.
"""

from entidades import Cliente
from servicios import Servicio
from reserva import Reserva
from logger import Logger
from excepciones import (
    ErrorClienteDuplicado,
    ErrorClienteNoEncontrado,
    ErrorServicioNoEncontrado,
    ErrorReservaNoEncontrada,
    ErrorOperacionNoPermitida,
    ErrorSistema,
)


class GestorSistema:
    """
    Gestor central del sistema Software FJ.
    Mantiene listas internas de clientes, servicios y reservas.
    """

    def __init__(self):
        self._clientes: dict[str, Cliente] = {}
        self._servicios: dict[str, Servicio] = {}
        self._reservas: dict[str, Reserva] = {}
        self._log = Logger()

    # ─────────────────────────────────────────
    # GESTIÓN DE CLIENTES
    # ─────────────────────────────────────────

    def registrar_cliente(self, cliente: Cliente) -> None:
        """Registra un nuevo cliente en el sistema."""
        try:
            if cliente.id in self._clientes:
                raise ErrorClienteDuplicado(
                    f"Ya existe un cliente con ID '{cliente.id}'."
                )
            if not cliente.validar():
                raise ErrorOperacionNoPermitida(
                    f"El cliente '{cliente.id}' no pasó la validación."
                )
            self._clientes[cliente.id] = cliente
        except ErrorSistema as e:
            self._log.error(f"registrar_cliente → {e}")
            raise
        else:
            self._log.info(f"Cliente registrado: {cliente.describir()}")

    def obtener_cliente(self, id_cliente: str) -> Cliente:
        try:
            if id_cliente not in self._clientes:
                raise ErrorClienteNoEncontrado(
                    f"No se encontró cliente con ID '{id_cliente}'."
                )
            return self._clientes[id_cliente]
        except ErrorSistema as e:
            self._log.error(f"obtener_cliente → {e}")
            raise

    def listar_clientes(self) -> list[Cliente]:
        return list(self._clientes.values())

    # ─────────────────────────────────────────
    # GESTIÓN DE SERVICIOS
    # ─────────────────────────────────────────

    def registrar_servicio(self, servicio: Servicio) -> None:
        try:
            if servicio.id in self._servicios:
                raise ErrorOperacionNoPermitida(
                    f"Ya existe un servicio con ID '{servicio.id}'."
                )
            if not servicio.validar():
                raise ErrorOperacionNoPermitida(
                    f"El servicio '{servicio.id}' no pasó la validación."
                )
            self._servicios[servicio.id] = servicio
        except ErrorSistema as e:
            self._log.error(f"registrar_servicio → {e}")
            raise
        else:
            self._log.info(f"Servicio registrado: {servicio.describir()}")

    def obtener_servicio(self, id_servicio: str) -> Servicio:
        try:
            if id_servicio not in self._servicios:
                raise ErrorServicioNoEncontrado(
                    f"No se encontró servicio con ID '{id_servicio}'."
                )
            return self._servicios[id_servicio]
        except ErrorSistema as e:
            self._log.error(f"obtener_servicio → {e}")
            raise

    def listar_servicios(self) -> list[Servicio]:
        return list(self._servicios.values())

    # ─────────────────────────────────────────
    # GESTIÓN DE RESERVAS
    # ─────────────────────────────────────────

    def crear_reserva(self, reserva: Reserva) -> None:
        try:
            if reserva.id in self._reservas:
                raise ErrorOperacionNoPermitida(
                    f"Ya existe una reserva con ID '{reserva.id}'."
                )
            self._reservas[reserva.id] = reserva
            reserva.cliente.agregar_reserva(reserva.id)
        except ErrorSistema as e:
            self._log.error(f"crear_reserva → {e}")
            raise
        else:
            self._log.info(f"Reserva creada: {reserva.describir()}")

    def confirmar_reserva(self, id_reserva: str) -> float:
        reserva = self._obtener_reserva(id_reserva)
        try:
            costo = reserva.confirmar()
        except ErrorSistema as e:
            self._log.error(f"confirmar_reserva({id_reserva}) → {e}")
            raise
        else:
            self._log.info(
                f"Reserva confirmada: {id_reserva} | Costo: ${costo:,.2f}"
            )
            return costo

    def cancelar_reserva(self, id_reserva: str, motivo: str = "") -> None:
        reserva = self._obtener_reserva(id_reserva)
        try:
            reserva.cancelar(motivo)
        except ErrorSistema as e:
            self._log.error(f"cancelar_reserva({id_reserva}) → {e}")
            raise
        else:
            self._log.info(f"Reserva cancelada: {id_reserva} | Motivo: {motivo}")

    def procesar_reserva(self, id_reserva: str) -> str:
        reserva = self._obtener_reserva(id_reserva)
        try:
            comprobante = reserva.procesar()
        except ErrorSistema as e:
            self._log.error(f"procesar_reserva({id_reserva}) → {e}")
            raise
        else:
            self._log.info(f"Reserva procesada exitosamente: {id_reserva}")
            return comprobante

    def listar_reservas(self) -> list[Reserva]:
        return list(self._reservas.values())

    def _obtener_reserva(self, id_reserva: str) -> Reserva:
        try:
            if id_reserva not in self._reservas:
                raise ErrorReservaNoEncontrada(
                    f"No se encontró reserva con ID '{id_reserva}'."
                )
            return self._reservas[id_reserva]
        except ErrorSistema as e:
            self._log.error(f"_obtener_reserva → {e}")
            raise

    # ─────────────────────────────────────────
    # REPORTE GENERAL
    # ─────────────────────────────────────────

    def reporte_general(self) -> str:
        clientes = len(self._clientes)
        servicios = len(self._servicios)
        reservas = len(self._reservas)
        procesadas = sum(
            1 for r in self._reservas.values() if r.estado == "procesada"
        )
        canceladas = sum(
            1 for r in self._reservas.values() if r.estado == "cancelada"
        )
        ingresos = sum(
            r.costo_total
            for r in self._reservas.values()
            if r.estado == "procesada"
        )
        return (
            f"\n{'*'*55}\n"
            f"  REPORTE GENERAL — Software FJ\n"
            f"{'*'*55}\n"
            f"  Clientes registrados : {clientes}\n"
            f"  Servicios activos    : {servicios}\n"
            f"  Total reservas       : {reservas}\n"
            f"    - Procesadas       : {procesadas}\n"
            f"    - Canceladas       : {canceladas}\n"
            f"    - Otras            : {reservas - procesadas - canceladas}\n"
            f"  Ingresos totales     : ${ingresos:,.2f} COP\n"
            f"{'*'*55}\n"
        )
