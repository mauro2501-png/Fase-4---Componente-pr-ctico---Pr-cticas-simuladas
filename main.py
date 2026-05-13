"""
main.py
Programa principal del Sistema Integral de Gestión de Clientes,
Servicios y Reservas — Software FJ.

Demuestra al menos 10 operaciones completas (válidas e inválidas),
manejo avanzado de excepciones (try/except, try/except/else,
try/except/finally, encadenamiento) y registro en archivo de logs.
"""

import sys
import os

# Asegurar que los módulos locales se encuentren
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from entidades import Cliente
from servicios import ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from reserva import Reserva
from gestor import GestorSistema
from logger import Logger
from excepciones import (
    ErrorSistema,
    ErrorClienteInvalido,
    ErrorClienteDuplicado,
    ErrorServicioInvalido,
    ErrorServicioNoDisponible,
    ErrorReservaInvalida,
    ErrorOperacionNoPermitida,
)


# ─────────────────────────────────────────────────────────
# UTILIDADES DE PRESENTACIÓN
# ─────────────────────────────────────────────────────────

def titulo(texto: str):
    print(f"\n{'─'*55}")
    print(f"  {texto}")
    print(f"{'─'*55}")


def ok(texto: str):
    print(f"  ✔  {texto}")


def fallo(texto: str):
    print(f"  ✘  {texto}")


# ─────────────────────────────────────────────────────────
# PROGRAMA PRINCIPAL
# ─────────────────────────────────────────────────────────

def main():
    log = Logger("software_fj.log")
    gestor = GestorSistema()

    log.separador("INICIO DEL SISTEMA SOFTWARE FJ")
    print("\n" + "=" * 55)
    print("   SISTEMA INTEGRAL SOFTWARE FJ")
    print("   Gestión de Clientes, Servicios y Reservas")
    print("=" * 55)

    # ══════════════════════════════════════════════════════
    # BLOQUE 1 — REGISTRO DE CLIENTES (válidos e inválidos)
    # ══════════════════════════════════════════════════════
    titulo("OPERACIÓN 1 — Registro de clientes válidos")

    clientes_data = [
        ("C001", "Ana Gómez",      "ana.gomez@email.com",   "3001234567", "vip"),
        ("C002", "Luis Martínez",  "luis.m@empresa.co",     "3109876543", "corporativo"),
        ("C003", "Sara Pineda",    "sara.p@correo.com",     "3205551234", "regular"),
    ]

    for datos in clientes_data:
        try:
            cliente = Cliente(*datos)
            gestor.registrar_cliente(cliente)
            ok(f"Cliente registrado: {cliente}")
        except ErrorSistema as e:
            fallo(f"No se registró cliente: {e}")

    # ──────────────────────────────────────────────────────
    titulo("OPERACIÓN 2 — Registro de clientes inválidos (errores controlados)")

    casos_invalidos = [
        # Correo malformado
        ("C004", "Pedro Ruiz", "correo_invalido", "3001111111", "regular",
         "correo inválido"),
        # Nombre muy corto
        ("C005", "Jo",         "jo@mail.com",     "3002222222", "regular",
         "nombre demasiado corto"),
        # Tipo de cliente no reconocido
        ("C006", "María López", "maria@mail.com", "3003333333", "platinum",
         "tipo de cliente inválido"),
        # Teléfono inválido
        ("C007", "Carlos V.",  "carlos@mail.com", "abc",        "regular",
         "teléfono inválido"),
    ]

    for id_, nombre, correo, tel, tipo, descripcion in casos_invalidos:
        try:
            cliente = Cliente(id_, nombre, correo, tel, tipo)
            gestor.registrar_cliente(cliente)
            fallo(f"Debió fallar ({descripcion}) — se registró igual")
        except ErrorClienteInvalido as e:
            ok(f"Error capturado correctamente ({descripcion}): {e}")
        except ErrorSistema as e:
            ok(f"Error de sistema capturado ({descripcion}): {e}")

    # ──────────────────────────────────────────────────────
    titulo("OPERACIÓN 3 — Registro duplicado de cliente")

    try:
        duplicado = Cliente("C001", "Ana Gómez Copia", "ana2@mail.com", "3001234567", "regular")
        gestor.registrar_cliente(duplicado)
        fallo("Debió fallar al registrar ID duplicado")
    except ErrorClienteDuplicado as e:
        ok(f"Duplicado detectado: {e}")

    # ══════════════════════════════════════════════════════
    # BLOQUE 2 — REGISTRO DE SERVICIOS (válidos e inválidos)
    # ══════════════════════════════════════════════════════
    titulo("OPERACIÓN 4 — Registro de servicios válidos")

    try:
        sala_a = ReservaSala(
            "SRV001", "Sala Ejecutiva A", 80_000,
            capacidad_maxima=10, tiene_proyector=True
        )
        equipo_laptop = AlquilerEquipo(
            "SRV002", "Alquiler de Laptops", 25_000,
            tipo_equipo="laptop", unidades_disponibles=5
        )
        asesoria_tech = AsesoriaEspecializada(
            "SRV003", "Asesoría en Arquitectura de Software", 120_000,
            area="Tecnología", nivel_asesor="experto"
        )
        sala_b = ReservaSala(
            "SRV004", "Sala de Capacitación B", 60_000,
            capacidad_maxima=20, tiene_proyector=False
        )

        for srv in [sala_a, equipo_laptop, asesoria_tech, sala_b]:
            gestor.registrar_servicio(srv)
            ok(f"Servicio registrado: {srv}")

    except ErrorSistema as e:
        fallo(f"Error registrando servicio: {e}")

    # ──────────────────────────────────────────────────────
    titulo("OPERACIÓN 5 — Registro de servicios inválidos")

    servicios_invalidos = [
        # Precio base negativo
        lambda: ReservaSala("SRV_X1", "Sala Inválida", -5000, capacidad_maxima=5),
        # Capacidad 0
        lambda: ReservaSala("SRV_X2", "Sala Sin Cap.", 50000, capacidad_maxima=0),
        # Tipo equipo no reconocido
        lambda: AlquilerEquipo("SRV_X3", "Equipo Raro", 30000,
                               tipo_equipo="dron", unidades_disponibles=2),
        # Nivel asesor inválido
        lambda: AsesoriaEspecializada("SRV_X4", "Asesoría Bad", 80000,
                                      area="TI", nivel_asesor="maestro"),
    ]

    descripciones = [
        "precio negativo",
        "capacidad 0",
        "tipo equipo inválido",
        "nivel asesor inválido",
    ]

    for creador, desc in zip(servicios_invalidos, descripciones):
        try:
            srv = creador()
            gestor.registrar_servicio(srv)
            fallo(f"Debió fallar ({desc})")
        except ErrorServicioInvalido as e:
            ok(f"Error capturado ({desc}): {e}")
        except ErrorSistema as e:
            ok(f"Error sistema ({desc}): {e}")

    # ══════════════════════════════════════════════════════
    # BLOQUE 3 — CREACIÓN Y GESTIÓN DE RESERVAS
    # ══════════════════════════════════════════════════════
    titulo("OPERACIÓN 6 — Creación y confirmación de reservas exitosas")

    try:
        # Reserva 1: VIP reserva sala con proyector (10 % descuento automático)
        cli_ana  = gestor.obtener_cliente("C001")
        srv_sala = gestor.obtener_servicio("SRV001")
        r1 = Reserva("RES001", cli_ana, srv_sala, 3.0, num_personas=5)
        gestor.crear_reserva(r1)
        costo1 = gestor.confirmar_reserva("RES001")
        ok(f"Reserva RES001 confirmada | Costo: ${costo1:,.2f} COP")

        # Reserva 2: Corporativo alquila laptops con seguro
        cli_luis    = gestor.obtener_cliente("C002")
        srv_laptops = gestor.obtener_servicio("SRV002")
        r2 = Reserva("RES002", cli_luis, srv_laptops, 8.0, unidades=3, seguro=True)
        gestor.crear_reserva(r2)
        costo2 = gestor.confirmar_reserva("RES002")
        ok(f"Reserva RES002 confirmada | Costo: ${costo2:,.2f} COP")

        # Reserva 3: Regular solicita asesoría urgente
        cli_sara     = gestor.obtener_cliente("C003")
        srv_asesoria = gestor.obtener_servicio("SRV003")
        r3 = Reserva("RES003", cli_sara, srv_asesoria, 2.0, urgente=True)
        gestor.crear_reserva(r3)
        costo3 = gestor.confirmar_reserva("RES003")
        ok(f"Reserva RES003 confirmada | Costo: ${costo3:,.2f} COP")

    except ErrorSistema as e:
        fallo(f"Error en reservas exitosas: {e}")

    # ──────────────────────────────────────────────────────
    titulo("OPERACIÓN 7 — Reservas con parámetros inválidos (errores controlados)")

    # 7a: Duración negativa
    try:
        cli_ana  = gestor.obtener_cliente("C001")
        srv_sala = gestor.obtener_servicio("SRV001")
        r_bad = Reserva("RES_BAD1", cli_ana, srv_sala, -2.0)
        fallo("Debió fallar con duración negativa")
    except ErrorReservaInvalida as e:
        ok(f"Duración inválida capturada: {e}")

    # 7b: Más personas que la capacidad máxima de la sala
    try:
        cli_sara = gestor.obtener_cliente("C003")
        srv_sala = gestor.obtener_servicio("SRV001")  # capacidad 10
        r_bad2 = Reserva("RES_BAD2", cli_sara, srv_sala, 2.0, num_personas=15)
        gestor.crear_reserva(r_bad2)
        gestor.confirmar_reserva("RES_BAD2")
        fallo("Debió fallar por exceso de personas")
    except (ErrorReservaInvalida, ErrorSistema) as e:
        ok(f"Exceso de personas capturado: {e}")

    # 7c: Servicio no disponible
    try:
        srv_sala_b = gestor.obtener_servicio("SRV004")
        srv_sala_b.desactivar()  # desactivamos manualmente
        cli_luis = gestor.obtener_cliente("C002")
        r_bad3 = Reserva("RES_BAD3", cli_luis, srv_sala_b, 1.0)
        gestor.crear_reserva(r_bad3)
        gestor.confirmar_reserva("RES_BAD3")
        fallo("Debió fallar por servicio no disponible")
    except ErrorServicioNoDisponible as e:
        ok(f"Servicio no disponible capturado: {e}")
    except ErrorSistema as e:
        ok(f"Error sistema capturado: {e}")
    finally:
        # Reactivamos el servicio en cualquier caso
        gestor.obtener_servicio("SRV004").activar()

    # ──────────────────────────────────────────────────────
    titulo("OPERACIÓN 8 — Procesamiento de reservas confirmadas")

    for id_res in ["RES001", "RES002", "RES003"]:
        try:
            comprobante = gestor.procesar_reserva(id_res)
            print(comprobante)
        except ErrorSistema as e:
            fallo(f"Error al procesar {id_res}: {e}")

    # ──────────────────────────────────────────────────────
    titulo("OPERACIÓN 9 — Cancelación de reservas")

    # Nueva reserva para cancelar
    try:
        cli_ana  = gestor.obtener_cliente("C001")
        srv_sala = gestor.obtener_servicio("SRV001")
        r_cancel = Reserva("RES004", cli_ana, srv_sala, 1.0, num_personas=2)
        gestor.crear_reserva(r_cancel)
        gestor.confirmar_reserva("RES004")
        gestor.cancelar_reserva("RES004", motivo="Cliente solicitó cambio de fecha")
        ok(f"Reserva RES004 cancelada correctamente")
    except ErrorSistema as e:
        fallo(f"Error al cancelar: {e}")

    # Intentar cancelar una ya procesada (debe fallar)
    try:
        gestor.cancelar_reserva("RES001", motivo="Intento inválido")
        fallo("Debió fallar al cancelar reserva procesada")
    except ErrorOperacionNoPermitida as e:
        ok(f"Cancelación inválida capturada: {e}")

    # ──────────────────────────────────────────────────────
    titulo("OPERACIÓN 10 — Encadenamiento de excepciones")

    try:
        try:
            # Intentamos crear una reserva con un objeto que no es Cliente
            r_chain = Reserva("RES_CHAIN", "no_soy_cliente", srv_sala, 2.0)
        except ErrorReservaInvalida as origen:
            raise ErrorOperacionNoPermitida(
                "Operación rechazada por datos de reserva corruptos."
            ) from origen
    except ErrorOperacionNoPermitida as final:
        ok(f"Encadenamiento capturado: {final}")
        ok(f"  ↳ Causa original: {final.__cause__}")

    # ──────────────────────────────────────────────────────
    titulo("OPERACIÓN 11 — Cálculo de costos con variantes (métodos sobrecargados)")

    try:
        srv_sala = gestor.obtener_servicio("SRV001")

        # Variante 1: sin impuesto ni descuento
        c1 = srv_sala.calcular_costo(2.0, num_personas=3, con_impuesto=False, descuento=0.0)
        ok(f"Costo sin impuesto, sin descuento (2h, 3 personas): ${c1:,.2f}")

        # Variante 2: con impuesto, sin descuento
        c2 = srv_sala.calcular_costo(2.0, num_personas=3, con_impuesto=True, descuento=0.0)
        ok(f"Costo con IVA, sin descuento (2h, 3 personas)       : ${c2:,.2f}")

        # Variante 3: con impuesto y descuento VIP (10 %)
        c3 = srv_sala.calcular_costo(2.0, num_personas=3, con_impuesto=True, descuento=0.10)
        ok(f"Costo con IVA + 10% descuento (2h, 3 personas)      : ${c3:,.2f}")

        # Variante 4: con impuesto y descuento corporativo (15 %)
        c4 = srv_sala.calcular_costo(2.0, num_personas=3, con_impuesto=True, descuento=0.15)
        ok(f"Costo con IVA + 15% descuento (2h, 3 personas)      : ${c4:,.2f}")

    except ErrorSistema as e:
        fallo(f"Error en cálculo: {e}")

    # ══════════════════════════════════════════════════════
    # REPORTE FINAL
    # ══════════════════════════════════════════════════════
    titulo("REPORTE FINAL DEL SISTEMA")

    print("\nClientes registrados:")
    for c in gestor.listar_clientes():
        print(f"  • {c.describir()}")

    print("\nServicios registrados:")
    for s in gestor.listar_servicios():
        print(f"  • {s.describir()}")

    print("\nReservas registradas:")
    for r in gestor.listar_reservas():
        print(f"  • {r.describir()}")

    print(gestor.reporte_general())

    log.separador("FIN DEL SISTEMA SOFTWARE FJ")
    print(f"\n  Log guardado en: software_fj.log")
    print("  Sistema finalizado correctamente.\n")


if __name__ == "__main__":
    main()
