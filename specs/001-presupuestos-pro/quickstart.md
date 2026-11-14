# Quickstart: comprobar PresupuestosPro v1

**Plan**: [plan.md](./plan.md) | **Spec**: [spec.md](./spec.md)

Guía para comprobar en la app que la feature funciona (constitución, principio IV). El arranque lo hace una persona técnica; los escenarios están escritos para personas no técnicas.

## 1. Arrancar en local (persona técnica)

Requisitos: Docker y Docker Compose.

```bash
docker compose up -d --build
docker compose exec app python -m presupuestos crear-titular --nombre "Laura Gómez" --email laura@ejemplo.es
docker compose exec app pytest          # cálculo, reglas fiscales y control de acceso: deben pasar todos
```

Abrir `https://localhost` (Caddy usa un certificado local; aceptar el aviso del navegador la primera vez). Para probar desde móvil o tableta en la misma red, usar la IP del ordenador. Órdenes de administración en [contracts/cli-administracion.md](./contracts/cli-administracion.md).

## 2. Datos de prueba

| Qué | Valor |
|---|---|
| Titular | laura@ejemplo.es (creada arriba) |
| Asistente | «Pablo», pablo@ejemplo.es, contraseña de 10+ caracteres |
| Perfil | «Laura Gómez Diseño», NIF 12345678Z, C/ Mayor 1, 28013 Madrid, laura@ejemplo.es, 600 000 000, logo PNG < 2 MB |
| Ajustes | IVA 21 %, retención activada 15 %, validez 30 días |
| Catálogo | «Hora de desarrollo», hora, 45,00 € · «Diseño de página web», proyecto, 1.500,00 € · «Sesión de fotos de producto», proyecto, 500,00 € |
| Clientes | «Acme SL» (Empresa, Península, NIF B12345678) · «Peña & Cía» (Empresa, Península, sin NIF) · «Ana Ruiz» (Particular, Península) · «Müller GmbH» (Empresa, Otro país UE, NIF-IVA verificado) · «Globex Inc» (Empresa, Fuera de la UE) · «Tenerife Tech SL» (Empresa, Canarias, con NIF) |
| Líneas base | 10 × «Hora de desarrollo» 45,00 € + 1 × «Mantenimiento» manual 300,00 € |

## 3. Escenarios de validación

Detalle de rutas en [contracts/rutas-http.md](./contracts/rutas-http.md); del PDF en [contracts/pdf-presupuesto.md](./contracts/pdf-presupuesto.md); del archivo exportado en [contracts/archivo-exportacion.md](./contracts/archivo-exportacion.md).

### A. Acceso (HU8)

| # | Pasos | Resultado esperado |
|---|---|---|
| A1 | Abrir la app en una ventana privada | Solo la pantalla de inicio de sesión, ningún dato (FR-034, SC-010) |
| A2 | Escribir a mano en la barra de direcciones `/clientes` o `/exportar` sin sesión | Vuelve a la pantalla de inicio de sesión |
| A3 | Entrar con contraseña incorrecta | «Email o contraseña incorrectos» |
| A4 | Fallar 5 veces seguidas y probar la contraseña correcta | Rechazado; mensaje de esperar. A los 15 minutos entra (FR-038) |
| A5 | Como titular: Cuentas → alta de Pablo | Pablo entra desde otro navegador y ve los mismos datos (FR-035) |
| A6 | Como Pablo, buscar «Cuentas» | No aparece; escribir `/cuentas` a mano → acceso denegado |
| A7 | Con Pablo con la sesión abierta, el titular le da de baja; Pablo pulsa cualquier cosa | Pablo vuelve a inicio de sesión y no puede entrar; sus presupuestos siguen |
| A8 | El titular asigna contraseña nueva a un asistente | La nueva funciona y la anterior no (FR-039) |
| A9 | Mi cuenta → cambiar contraseña con una de 8 caracteres · luego con una de 12 | Rechazo con mensaje · aceptada |
| A10 | Cerrar sesión y pulsar «Atrás» en el navegador | No se ven datos (FR-037) |
| A11 | Dejar la sesión abierta sin usarla 8 horas y pulsar cualquier cosa · (Técnico, atajo) poner la última actividad a hace 9 h | Se pide iniciar sesión de nuevo (FR-037) |
| A12 | Intentar dar de alta un asistente con el email del titular | Rechazo: email ya usado |

### B. Configuración (HU3, HU5)

| # | Pasos | Resultado esperado |
|---|---|---|
| B1 | Perfil vacío → Guardar | Mensaje con los campos que faltan: nombre, NIF, dirección, email |
| B2 | Subir logo PNG de 1 MB | Vista previa |
| B3 | Subir logo de 3 MB, un .gif, o un .gif renombrado a .png | Rechazo: «PNG, JPG o SVG, hasta 2 MB» (CL9) |
| B4 | Completar perfil, ajustes y 3 servicios | Aparecen en catálogo y selector de líneas; tiempo < 10 min (SC-005) |

### C. Cálculo en pantalla (HU1)

Todos los cambios se ven sin recargar la página.

| # | Pasos | Resultado esperado |
|---|---|---|
| C0 | Nuevo presupuesto sin cliente, líneas base | 750,00 / 157,50 / −112,50 / 795,00 € y aviso «Totales provisionales: elige un cliente» (FR-044) |
| C1 | Nuevo presupuesto, Acme SL, líneas base | 750,00 / IVA 21 % 157,50 / Retención −112,50 / Total 795,00 € (CA6) |
| C2 | Cambiar a Ana Ruiz | Total 907,50 €; sin fila de retención (CA7) |
| C3 | Cambiar a Müller GmbH | IVA 0,00; sin retención; 750,00 €; «Inversión del sujeto pasivo» (CA8) |
| C4 | Cambiar a Globex Inc | IVA 0,00; 750,00 €; «Operación no sujeta — Art. 69.Uno.1.º Ley 37/1992» (CL3) |
| C5 | Cambiar a Tenerife Tech SL | IVA 0,00; Retención −112,50; Total 637,50 €; sin mención (CL4) |
| C6 | Escribir un texto de mención en Ajustes y volver a C5 | Aparece ese texto |
| C7 | Acme SL, cantidad 10 → 12 | 840,00 / 176,40 / −126,00 / 890,40 € (CA9) |
| C8 | «Diseño de página web» + «Sesión de fotos», Acme SL | 2.000,00 / 420,00 / −300,00 / 2.120,00 € |
| C9 | C8 con retención 7 % · luego con Ana Ruiz | 2.280,00 € · 2.420,00 € |
| C10 | Línea 1,5 × 45,00 € | 67,50 € (CL7) |
| C11 | Cantidad 0, cantidad −1, precio 10,555 | Error; no se acepta (RN10) |
| C12 | Línea de cortesía a 0,00 € | Aceptada; totales sin cambio (CL6) |
| C13 | Mover una línea arriba/abajo y eliminar otra | Orden y totales al instante (RF8) |
| C14 | IVA del presupuesto 10 % con Acme SL (líneas base) | IVA 75,00; Total 712,50 € (CL5) |
| C15 | Añadir «Hora de desarrollo» y cambiar el precio de la línea a 50 € | Catálogo sigue a 45,00 € (CA4) |
| C16 | Línea manual «Licencia anual» 1 × 120,00 € | No aparece en el catálogo (CA5) |
| C17 | Cambiar la fecha de emisión · poner validez anterior a emisión | La validez se mueve · mensaje de error (FR-011) |
| C18 | Con la app abierta, desconectar el wifi y cambiar una cantidad | Aviso «No se ha podido guardar. Comprueba tu conexión.» |

### D. Clientes (HU4)

| # | Pasos | Resultado esperado |
|---|---|---|
| D1 | Con líneas escritas, alta de «Nuevo Cliente SL» desde el presupuesto | Seleccionado, líneas intactas, aparece en Clientes (CA3) |
| D2 | Buscar «acm» o «B123» desde el presupuesto | Aparece Acme SL (RF5) |
| D3 | Cliente con categoría Particular | Solo territorios de España (P3) |
| D4 | Empresa UE sin «NIF-IVA verificado» | IVA 21 %, sin retención ni mención (CL1) |
| D5 | Archivar Acme SL | Fuera del buscador; sus presupuestos lo siguen mostrando (CL11) |
| D6 | Anonimizar Ana Ruiz (usada en un presupuesto) y confirmar | Pasa a «Cliente eliminado» sin NIF, dirección ni email; no sale en el buscador ni se puede editar; su presupuesto sigue en el historial con el mismo total y el PDF queda bloqueado con el motivo (FR-043) |

### E. PDF (HU2)

| # | Pasos | Resultado esperado |
|---|---|---|
| E1 | Descargar C1 | `PRE-AAAA-NNN_Acme-SL.pdf`; cabecera con logo y datos; importes iguales a la pantalla (CA1, CA12) |
| E2 | Quitar el NIF del perfil y descargar un presupuesto nunca descargado | No se genera; «falta el NIF» (CA2) |
| E3 | Presupuesto sin cliente / sin líneas | No se genera; indica qué falta (CA13) |
| E4 | Cliente «Peña & Cía» sin NIF | No se genera; pide el NIF del cliente (CL13). Tras añadirlo: `…_Pena-Cia.pdf` |
| E5 | Emisión 13/11/2026, validez 30 días | «Válido hasta el 13/12/2026» (CA11) |
| E6 | Presupuesto con 40 líneas | Varias páginas, cabecera repetida, totales al final (CL8) |
| E7 | Con notas | Las notas aparecen (RF10) |
| E8 | Descargar E1, cambiar dirección del perfil y retención a 7 %, volver a descargar E1 | Dirección antigua y 15 % (CL12, CL15) |
| E9 | Tras E8, cambiar la dirección de Acme SL y descargar E1 | Dirección nueva del cliente (FR-018) |
| E10 | Crear un presupuesto nuevo tras E8 | Dirección nueva del perfil y 7 % |

### F. Numeración e historial (HU6, HU7)

| # | Pasos | Resultado esperado |
|---|---|---|
| F1 | Crear dos presupuestos seguidos | Números consecutivos (CA10) |
| F2 | Borrar el último (confirmando) y crear otro | Recibe el siguiente; el borrado no se reutiliza |
| F3 | Titular y Pablo, en equipos distintos, pulsan «Nuevo presupuesto» a la vez | Números distintos y consecutivos (FR-033) |
| F4 | Titular y Pablo editan el mismo cliente y guardan | Queda la versión guardada en último lugar |
| F5 | Historial | Orden por fecha de emisión descendente con número, cliente, fecha y total |
| F6 | Buscar «015» y «Acme» | Solo coincidencias; reabrir uno en < 30 s (SC-006) |
| F7 | Reabrir un presupuesto descargado y cambiar una línea | Mismo número; la siguiente descarga refleja el cambio |
| F8 | (Técnico) Arrancar con la fecha del sistema en 2027 | Primer presupuesto `PRE-2027-001` (CL10) |

### G. Datos a salvo (HU9)

| # | Pasos | Resultado esperado |
|---|---|---|
| G1 | Borrar todos los datos del navegador y volver a entrar | Todo sigue igual (SC-004) |
| G2 | Entrar desde otro equipo y desde el móvil | Mismos datos (CL14) |
| G3 | Exportar | Un único `.json` con todo, logo y numeración incluidos; sin cuentas ni contraseñas (FR-029) |
| G4 | (Técnico) Ejecutar la orden `copia` y la subida con rclone. Después, crear en la app un presupuesto nuevo. Borrar la copia local, descargar la copia **desde el almacenamiento externo** y restaurarla siguiendo los pasos de restauración | La app muestra los datos tal como estaban al hacer la copia; el presupuesto creado después no está (FR-041, FR-042, SC-011) |

### H. Dispositivos y rendimiento (FR-031, SC-001, SC-009)

| # | Pasos | Resultado esperado |
|---|---|---|
| H1 | Con todo configurado, crear y descargar un presupuesto de 3 líneas | < 5 minutos (SC-001) |
| H2 | Repetir H1 en móvil (360 px), tableta y ordenador | Sin desplazamiento horizontal; mismos importes (SC-009) |
| H3 | Recorrer todas las pantallas a 360 px, incluidas inicio de sesión y Cuentas | Todas usables |
