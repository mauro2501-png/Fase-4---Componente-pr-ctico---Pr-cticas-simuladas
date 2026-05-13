"""
servicios.py
Clase abstracta Servicio y tres clases derivadas:
  - ReservaSala
  - AlquilerEquipo
  - AsesoriaEspecializada
Con polimorfismo, métodos sobrescritos y métodos sobrecargados
para el cálculo de costos.
"""

from abc import abstractmethod
from entidades import EntidadSistema
from excepciones import (
    ErrorServicioInvalido,
    ErrorServicioNoDisponible,
    ErrorCalculo,
    ErrorParametroFaltante,
)


# ─────────────────────────────────────────────
# CLASE ABSTRACTA SERVICIO
# ─────────────────────────────────────────────

class Servicio(EntidadSistema):
    """
    Clase abstracta que representa un servicio ofrecido por Software FJ.
    Todas las subclases deben implementar calcular_costo, describir y validar.
    """

    IMPUESTO_BASE = 0.19  # IVA 19 %

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        precio_base: float,
        disponible: bool = True,
    ):
        super().__init__(id_servicio)
        self.nombre = nombre
        self.precio_base = precio_base
        self._disponible = disponible

    # ── Propiedades ──────────────────────────────

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not valor or not str(valor).strip():
            raise ErrorServicioInvalido("El nombre del servicio no puede estar vacío.")
        self._nombre = valor.strip()

    @property
    def precio_base(self) -> float:
        return self._precio_base

    @precio_base.setter
    def precio_base(self, valor: float):
        try:
            valor = float(valor)
        except (TypeError, ValueError):
            raise ErrorServicioInvalido(
                f"El precio base '{valor}' no es un número válido."
            )
        if valor <= 0:
            raise ErrorServicioInvalido(
                f"El precio base debe ser mayor a 0. Se recibió: {valor}."
            )
        self._precio_base = valor

    @property
    def disponible(self) -> bool:
        return self._disponible

    def activar(self):
        self._disponible = True

    def desactivar(self):
        self._disponible = False

    # ── Métodos abstractos ───────────────────────

    @abstractmethod
    def calcular_costo(self, duracion_horas: float, **kwargs) -> float:
        """Calcula el costo total del servicio."""
        pass

    @abstractmethod
    def describir(self) -> str:
        pass

    @abstractmethod
    def validar(self) -> bool:
        pass

    # ── Método de utilidad ───────────────────────

    def _verificar_disponibilidad(self):
        if not self._disponible:
            raise ErrorServicioNoDisponible(
                f"El servicio '{self._nombre}' [{self._id}] no está disponible."
            )

    def _aplicar_impuesto(self, monto: float, tasa: float = None) -> float:
        tasa = tasa if tasa is not None else self.IMPUESTO_BASE
        try:
            return round(monto * (1 + tasa), 2)
        except Exception as e:
            raise ErrorCalculo(
                f"Error al aplicar impuesto sobre {monto}: {e}"
            ) from e

    def _aplicar_descuento(self, monto: float, descuento: float) -> float:
        if not (0.0 <= descuento <= 1.0):
            raise ErrorCalculo(
                f"El descuento {descuento} debe estar entre 0.0 y 1.0."
            )
        return round(monto * (1 - descuento), 2)

    def __str__(self) -> str:
        estado = "Disponible" if self._disponible else "No disponible"
        return f"{self._nombre} [{self._id}] — ${self._precio_base:,.0f}/hr — {estado}"


# ─────────────────────────────────────────────
# SERVICIO 1: RESERVA DE SALA
# ─────────────────────────────────────────────

class ReservaSala(Servicio):
    """
    Servicio de reserva de salas de reunión o conferencia.
    El costo depende de la capacidad y duración.
    """

    COSTO_POR_PERSONA_HORA = 5_000  # pesos adicionales por persona por hora

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        precio_base: float,
        capacidad_maxima: int,
        tiene_proyector: bool = False,
        disponible: bool = True,
    ):
        super().__init__(id_servicio, nombre, precio_base, disponible)
        self.capacidad_maxima = capacidad_maxima
        self._tiene_proyector = tiene_proyector

    @property
    def capacidad_maxima(self) -> int:
        return self._capacidad_maxima

    @capacidad_maxima.setter
    def capacidad_maxima(self, valor: int):
        try:
            valor = int(valor)
        except (TypeError, ValueError):
            raise ErrorServicioInvalido(
                f"La capacidad '{valor}' no es un entero válido."
            )
        if valor < 1:
            raise ErrorServicioInvalido(
                f"La capacidad máxima debe ser al menos 1. Se recibió: {valor}."
            )
        self._capacidad_maxima = valor

    def calcular_costo(
        self,
        duracion_horas: float,
        num_personas: int = 1,
        con_impuesto: bool = True,
        descuento: float = 0.0,
    ) -> float:
        """
        Calcula el costo de la reserva de sala.
        Parámetros opcionales: num_personas, con_impuesto, descuento.
        """
        self._verificar_disponibilidad()
        try:
            duracion_horas = float(duracion_horas)
            num_personas = int(num_personas)
        except (TypeError, ValueError) as e:
            raise ErrorCalculo(
                f"Parámetros de cálculo inválidos para ReservaSala: {e}"
            ) from e

        if duracion_horas <= 0:
            raise ErrorCalculo("La duración debe ser mayor a 0 horas.")
        if num_personas < 1:
            raise ErrorCalculo("El número de personas debe ser al menos 1.")
        if num_personas > self._capacidad_maxima:
            raise ErrorCalculo(
                f"Número de personas ({num_personas}) supera la capacidad "
                f"máxima ({self._capacidad_maxima})."
            )

        costo = (
            self._precio_base * duracion_horas
            + self.COSTO_POR_PERSONA_HORA * num_personas * duracion_horas
        )
        if self._tiene_proyector:
            costo += 20_000  # cargo fijo por uso de proyector

        costo = self._aplicar_descuento(costo, descuento)
        if con_impuesto:
            costo = self._aplicar_impuesto(costo)
        return round(costo, 2)

    def describir(self) -> str:
        proyector = "con proyector" if self._tiene_proyector else "sin proyector"
        return (
            f"[SALA] {self._nombre} | ID: {self._id} | "
            f"Precio base: ${self._precio_base:,.0f}/hr | "
            f"Capacidad: {self._capacidad_maxima} personas | {proyector} | "
            f"Estado: {'Disponible' if self._disponible else 'No disponible'}"
        )

    def validar(self) -> bool:
        return (
            bool(self._id and self._nombre)
            and self._precio_base > 0
            and self._capacidad_maxima >= 1
        )


# ─────────────────────────────────────────────
# SERVICIO 2: ALQUILER DE EQUIPO
# ─────────────────────────────────────────────

class AlquilerEquipo(Servicio):
    """
    Servicio de alquiler de equipos tecnológicos.
    El costo incluye tarifa base más cargo por unidades adicionales.
    """

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        precio_base: float,
        tipo_equipo: str,
        unidades_disponibles: int,
        disponible: bool = True,
    ):
        super().__init__(id_servicio, nombre, precio_base, disponible)
        self.tipo_equipo = tipo_equipo
        self.unidades_disponibles = unidades_disponibles

    @property
    def tipo_equipo(self) -> str:
        return self._tipo_equipo

    @tipo_equipo.setter
    def tipo_equipo(self, valor: str):
        tipos = {"laptop", "proyector", "tablet", "camara", "servidor", "otro"}
        if not valor or valor.lower() not in tipos:
            raise ErrorServicioInvalido(
                f"Tipo de equipo '{valor}' no reconocido. Opciones: {tipos}."
            )
        self._tipo_equipo = valor.lower()

    @property
    def unidades_disponibles(self) -> int:
        return self._unidades_disponibles

    @unidades_disponibles.setter
    def unidades_disponibles(self, valor: int):
        try:
            valor = int(valor)
        except (TypeError, ValueError):
            raise ErrorServicioInvalido(
                f"Las unidades disponibles '{valor}' no son un entero válido."
            )
        if valor < 0:
            raise ErrorServicioInvalido("Las unidades disponibles no pueden ser negativas.")
        self._unidades_disponibles = valor

    def calcular_costo(
        self,
        duracion_horas: float,
        unidades: int = 1,
        con_impuesto: bool = True,
        descuento: float = 0.0,
        seguro: bool = False,
    ) -> float:
        """
        Calcula el costo del alquiler.
        Parámetros opcionales: unidades, con_impuesto, descuento, seguro.
        """
        self._verificar_disponibilidad()
        try:
            duracion_horas = float(duracion_horas)
            unidades = int(unidades)
        except (TypeError, ValueError) as e:
            raise ErrorCalculo(
                f"Parámetros inválidos para AlquilerEquipo: {e}"
            ) from e

        if duracion_horas <= 0:
            raise ErrorCalculo("La duración debe ser mayor a 0 horas.")
        if unidades < 1:
            raise ErrorCalculo("Se debe alquilar al menos 1 unidad.")
        if unidades > self._unidades_disponibles:
            raise ErrorCalculo(
                f"No hay suficientes unidades. Solicitadas: {unidades}, "
                f"disponibles: {self._unidades_disponibles}."
            )

        costo = self._precio_base * duracion_horas * unidades
        if seguro:
            costo += costo * 0.05  # 5 % de seguro sobre el total

        costo = self._aplicar_descuento(costo, descuento)
        if con_impuesto:
            costo = self._aplicar_impuesto(costo)
        return round(costo, 2)

    def describir(self) -> str:
        return (
            f"[EQUIPO] {self._nombre} | ID: {self._id} | "
            f"Tipo: {self._tipo_equipo.upper()} | "
            f"Precio base: ${self._precio_base:,.0f}/hr/unidad | "
            f"Unidades disponibles: {self._unidades_disponibles} | "
            f"Estado: {'Disponible' if self._disponible else 'No disponible'}"
        )

    def validar(self) -> bool:
        return (
            bool(self._id and self._nombre and self._tipo_equipo)
            and self._precio_base > 0
            and self._unidades_disponibles >= 0
        )


# ─────────────────────────────────────────────
# SERVICIO 3: ASESORÍA ESPECIALIZADA
# ─────────────────────────────────────────────

class AsesoriaEspecializada(Servicio):
    """
    Servicio de asesoría profesional por un experto calificado.
    El costo varía según el nivel del asesor y la urgencia.
    """

    NIVELES_VALIDOS = {"junior": 1.0, "senior": 1.5, "experto": 2.0}

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        precio_base: float,
        area: str,
        nivel_asesor: str = "junior",
        disponible: bool = True,
    ):
        super().__init__(id_servicio, nombre, precio_base, disponible)
        self.area = area
        self.nivel_asesor = nivel_asesor

    @property
    def area(self) -> str:
        return self._area

    @area.setter
    def area(self, valor: str):
        if not valor or not str(valor).strip():
            raise ErrorServicioInvalido(
                "El área de asesoría no puede estar vacía."
            )
        self._area = valor.strip()

    @property
    def nivel_asesor(self) -> str:
        return self._nivel_asesor

    @nivel_asesor.setter
    def nivel_asesor(self, valor: str):
        if valor.lower() not in self.NIVELES_VALIDOS:
            raise ErrorServicioInvalido(
                f"Nivel '{valor}' no válido. Opciones: {list(self.NIVELES_VALIDOS)}."
            )
        self._nivel_asesor = valor.lower()

    def calcular_costo(
        self,
        duracion_horas: float,
        urgente: bool = False,
        con_impuesto: bool = True,
        descuento: float = 0.0,
    ) -> float:
        """
        Calcula el costo de la asesoría.
        Parámetros opcionales: urgente, con_impuesto, descuento.
        """
        self._verificar_disponibilidad()
        try:
            duracion_horas = float(duracion_horas)
        except (TypeError, ValueError) as e:
            raise ErrorCalculo(
                f"Parámetros inválidos para AsesoriaEspecializada: {e}"
            ) from e

        if duracion_horas <= 0:
            raise ErrorCalculo("La duración debe ser mayor a 0 horas.")

        multiplicador = self.NIVELES_VALIDOS[self._nivel_asesor]
        costo = self._precio_base * duracion_horas * multiplicador

        if urgente:
            costo *= 1.30  # recargo del 30 % por urgencia

        costo = self._aplicar_descuento(costo, descuento)
        if con_impuesto:
            costo = self._aplicar_impuesto(costo)
        return round(costo, 2)

    def describir(self) -> str:
        return (
            f"[ASESORIA] {self._nombre} | ID: {self._id} | "
            f"Área: {self._area} | Nivel: {self._nivel_asesor.upper()} | "
            f"Precio base: ${self._precio_base:,.0f}/hr | "
            f"Estado: {'Disponible' if self._disponible else 'No disponible'}"
        )

    def validar(self) -> bool:
        return (
            bool(self._id and self._nombre and self._area)
            and self._precio_base > 0
            and self._nivel_asesor in self.NIVELES_VALIDOS
        )
