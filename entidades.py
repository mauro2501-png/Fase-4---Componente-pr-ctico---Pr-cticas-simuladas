"""
entidades.py
Clase abstracta base EntidadSistema y clase Cliente con
encapsulación y validaciones robustas.
"""

import re
from abc import ABC, abstractmethod
from excepciones import (
    ErrorClienteInvalido,
    ErrorParametroFaltante,
)


# ─────────────────────────────────────────────
# CLASE ABSTRACTA BASE
# ─────────────────────────────────────────────

class EntidadSistema(ABC):
    """
    Clase abstracta que representa cualquier entidad gestionada
    por el sistema Software FJ.
    """

    def __init__(self, identificador: str):
        if not identificador or not str(identificador).strip():
            raise ErrorParametroFaltante(
                "El identificador de la entidad no puede estar vacío."
            )
        self._id = str(identificador).strip()

    @property
    def id(self) -> str:
        return self._id

    @abstractmethod
    def describir(self) -> str:
        """Retorna una descripción completa de la entidad."""
        pass

    @abstractmethod
    def validar(self) -> bool:
        """Valida la integridad de los datos de la entidad."""
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self._id})"


# ─────────────────────────────────────────────
# CLASE CLIENTE
# ─────────────────────────────────────────────

class Cliente(EntidadSistema):
    """
    Representa un cliente registrado en el sistema.
    Implementa encapsulación total y validaciones estrictas.
    """

    def __init__(
        self,
        id_cliente: str,
        nombre: str,
        correo: str,
        telefono: str,
        tipo: str = "regular",
    ):
        super().__init__(id_cliente)
        # Usamos setters para aprovechar las validaciones
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono
        self.tipo = tipo
        self._reservas_activas: list = []

    # ── Propiedades con validación ──────────────

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not valor or not str(valor).strip():
            raise ErrorClienteInvalido("El nombre del cliente no puede estar vacío.")
        if len(valor.strip()) < 3:
            raise ErrorClienteInvalido(
                f"El nombre '{valor}' es demasiado corto (mínimo 3 caracteres)."
            )
        self._nombre = valor.strip()

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str):
        if not valor or not str(valor).strip():
            raise ErrorClienteInvalido("El correo del cliente no puede estar vacío.")
        patron = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
        if not re.match(patron, valor.strip()):
            raise ErrorClienteInvalido(
                f"El correo '{valor}' no tiene un formato válido."
            )
        self._correo = valor.strip().lower()

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str):
        if not valor or not str(valor).strip():
            raise ErrorClienteInvalido("El teléfono del cliente no puede estar vacío.")
        limpio = re.sub(r"[\s\-\+\(\)]", "", valor)
        if not limpio.isdigit() or len(limpio) < 7:
            raise ErrorClienteInvalido(
                f"El teléfono '{valor}' no es válido (mínimo 7 dígitos numéricos)."
            )
        self._telefono = valor.strip()

    @property
    def tipo(self) -> str:
        return self._tipo

    @tipo.setter
    def tipo(self, valor: str):
        tipos_validos = {"regular", "vip", "corporativo"}
        if valor.lower() not in tipos_validos:
            raise ErrorClienteInvalido(
                f"Tipo de cliente '{valor}' no válido. Opciones: {tipos_validos}."
            )
        self._tipo = valor.lower()

    @property
    def reservas_activas(self) -> list:
        return list(self._reservas_activas)

    # ── Métodos ─────────────────────────────────

    def agregar_reserva(self, id_reserva: str):
        """Registra una reserva activa para este cliente."""
        if id_reserva not in self._reservas_activas:
            self._reservas_activas.append(id_reserva)

    def remover_reserva(self, id_reserva: str):
        """Elimina una reserva del cliente."""
        if id_reserva in self._reservas_activas:
            self._reservas_activas.remove(id_reserva)

    def descuento_por_tipo(self) -> float:
        """Retorna el porcentaje de descuento según el tipo de cliente."""
        descuentos = {"regular": 0.0, "vip": 0.10, "corporativo": 0.15}
        return descuentos.get(self._tipo, 0.0)

    def describir(self) -> str:
        return (
            f"Cliente [{self._id}] | Nombre: {self._nombre} | "
            f"Correo: {self._correo} | Teléfono: {self._telefono} | "
            f"Tipo: {self._tipo.upper()} | "
            f"Reservas activas: {len(self._reservas_activas)}"
        )

    def validar(self) -> bool:
        """Verifica que todos los datos esenciales del cliente estén presentes."""
        return bool(self._id and self._nombre and self._correo and self._telefono)

    def __str__(self) -> str:
        return f"{self._nombre} ({self._id})"
