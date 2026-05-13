"""
excepciones.py
Módulo de excepciones personalizadas para el Sistema Software FJ.
"""


class ErrorSistema(Exception):
    """Excepción base del sistema."""
    def __init__(self, mensaje: str, codigo: str = "ERR_000"):
        self.mensaje = mensaje
        self.codigo = codigo
        super().__init__(f"[{codigo}] {mensaje}")


class ErrorClienteInvalido(ErrorSistema):
    """Se lanza cuando los datos de un cliente son inválidos."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_CLI_001")


class ErrorClienteDuplicado(ErrorSistema):
    """Se lanza cuando se intenta registrar un cliente ya existente."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_CLI_002")


class ErrorClienteNoEncontrado(ErrorSistema):
    """Se lanza cuando no se encuentra un cliente en el sistema."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_CLI_003")


class ErrorServicioInvalido(ErrorSistema):
    """Se lanza cuando los parámetros de un servicio son inválidos."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_SRV_001")


class ErrorServicioNoDisponible(ErrorSistema):
    """Se lanza cuando un servicio no está disponible."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_SRV_002")


class ErrorServicioNoEncontrado(ErrorSistema):
    """Se lanza cuando no se encuentra un servicio en el sistema."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_SRV_003")


class ErrorReservaInvalida(ErrorSistema):
    """Se lanza cuando los datos de una reserva son inválidos."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_RES_001")


class ErrorReservaNoEncontrada(ErrorSistema):
    """Se lanza cuando no se encuentra una reserva."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_RES_002")


class ErrorOperacionNoPermitida(ErrorSistema):
    """Se lanza cuando se intenta realizar una operación no permitida."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_OPE_001")


class ErrorCalculo(ErrorSistema):
    """Se lanza cuando hay un error en cálculos de costos."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_CAL_001")


class ErrorParametroFaltante(ErrorSistema):
    """Se lanza cuando falta un parámetro obligatorio."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_PAR_001")
