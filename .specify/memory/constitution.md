# PresupuestosPro Constitution

## Core Principles

### I. Simplicidad ante todo

- Ante dos soluciones válidas, DEBE elegirse siempre la más simple.
- Esta es la versión 1: NO DEBE añadirse complejidad anticipada (capas, configuraciones
  o soporte para casos futuros que la spec no pide).
- Motivo: menos piezas significan menos errores y una revisión más fácil para cualquiera.

### II. Idioma y mercado

- Todo el producto (interfaz, mensajes, textos de ayuda y el PDF generado) DEBE estar en
  español de España.
- Todos los importes DEBEN mostrarse en euros (€) con formato español, por ejemplo
  1.234,56 €.

### III. Cero alcance fantasma

- NO DEBE implementarse ninguna funcionalidad que no esté escrita en la spec.
- Si surge una idea nueva, DEBE registrarse como propuesta y NO DEBE construirse hasta que
  se incluya en la spec.
- Motivo: evitar que el producto crezca sin control y que cada entrega sea difícil de
  verificar.

### IV. Verificable sin leer código

- Cada criterio de éxito de la spec DEBE poder comprobarse usando la app: pasos escritos
  y un resultado observable.
- Un criterio que solo pueda comprobarse leyendo código NO es válido.
- Los tests automáticos pueden existir como apoyo, pero NO sustituyen la comprobación en
  la app.

### V. Datos del usuario con respeto

- La app DEBE pedir solo los datos imprescindibles para generar un presupuesto en PDF.
- NO DEBEN introducirse claves, contraseñas, tokens ni secretos en el código ni en el
  repositorio. Se guardan fuera del código, en configuración local no versionada.

## Alcance y propuestas

- La spec es la única fuente de lo que se construye.
- Toda tarea y todo cambio DEBE poder enlazarse con un punto concreto de la spec.
- Las ideas nuevas DEBEN ir a una lista de propuestas separada. No entran en la versión
  actual.

## Verificación de cada entrega

- Antes de dar por terminada una entrega, DEBE comprobarse cada criterio de éxito en la app.
- Cada entrega DEBE revisarse contra los principios I a V.
- Los pasos de verificación DEBEN poder seguirlos personas no técnicas.
- Excepción: las operaciones de administración del servidor (instalación, copias de
  seguridad y restauración) y las comprobaciones que dependen del reloj del sistema
  (caducidad de sesión, cambio de año en la numeración) las verifica el administrador
  técnico siguiendo la guía escrita. Su resultado DEBE poder observarse en la app y DEBEN
  marcarse como «(Técnico)» en la guía de verificación.

## Governance

- Esta constitución prevalece sobre cualquier otra práctica del proyecto.
- Las enmiendas DEBEN proponerse por escrito, aprobarlas el responsable del producto y
  registrar la nueva versión y fecha en este documento.
- Versionado semántico:
  - MAJOR: se elimina o cambia un principio de forma incompatible con la versión anterior.
  - MINOR: se añade un principio o sección, o se amplía una regla de forma material.
  - PATCH: se corrigen redacción, erratas o aclaraciones sin cambiar el sentido.
- Cumplimiento: cada spec, plan y entrega DEBE revisarse contra estos principios. Toda
  excepción DEBE justificarse por escrito.

**Version**: 1.1.0 | **Ratified**: 2026-11-13 | **Last Amended**: 2026-11-14
