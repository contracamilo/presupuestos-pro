"""Validaciones de negocio: perfil obligatorio, requisitos de descarga y cliente (FR-001, FR-007, FR-023)."""

CAMPOS_PERFIL = [("nombre", "nombre"), ("nif", "NIF"), ("direccion", "dirección"), ("email", "email")]
TERRITORIOS = ("peninsula", "canarias", "ue", "fuera_ue")
TERRITORIOS_ESPANA = ("peninsula", "canarias")
CATEGORIAS = ("empresa", "particular")


def _vacio(valor) -> bool:
    return not (valor or "").strip()


def faltan_perfil(perfil) -> list[str]:
    """Nombres de los campos obligatorios que faltan, en español."""
    return [etiqueta for campo, etiqueta in CAMPOS_PERFIL if _vacio(perfil.get(campo) if perfil else "")]


def requisitos_descarga(perfil_efectivo, cliente, lineas) -> list[str]:
    """Mensajes de contracts/pdf-presupuesto.md. Lista vacía = se puede descargar."""
    fallos = []
    for etiqueta in faltan_perfil(perfil_efectivo):
        fallos.append(f"Completa tu perfil: falta el {etiqueta}." if etiqueta != "dirección"
                      else "Completa tu perfil: falta la dirección.")
    if cliente is None:
        fallos.append("Selecciona un cliente.")
    elif cliente["anonimizado"]:
        fallos.append("El cliente de este presupuesto fue eliminado: no se puede descargar.")
    elif (cliente["categoria"] == "empresa" and cliente["territorio"] in TERRITORIOS_ESPANA
          and _vacio(cliente["nif"])):
        fallos.append(f"Completa el NIF del cliente {cliente['nombre']}.")
    if not lineas:
        fallos.append("Añade al menos una línea.")
    return fallos


def validar_cliente(datos) -> list[str]:
    errores = []
    if _vacio(datos.get("nombre")):
        errores.append("El nombre o razón social es obligatorio.")
    categoria = datos.get("categoria")
    territorio = datos.get("territorio")
    if categoria not in CATEGORIAS:
        errores.append("Elige una categoría: Empresa/autónomo o Particular.")
    if territorio not in TERRITORIOS:
        errores.append("Elige un territorio.")
    if categoria == "particular" and territorio in TERRITORIOS and territorio not in TERRITORIOS_ESPANA:
        errores.append("Un cliente particular solo puede estar en España.")
    if datos.get("nif_iva_verificado") and territorio != "ue":
        errores.append("«NIF-IVA verificado» solo se puede marcar para clientes de otro país UE.")
    return errores
