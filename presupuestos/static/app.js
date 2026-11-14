// PresupuestosPro — comportamiento mínimo en el navegador. Sin dependencias ni JS en línea (CSP).
(function () {
  "use strict";

  // Aviso si un cambio no llega al servidor (D13).
  function aviso(mostrar) {
    var el = document.getElementById("aviso-conexion");
    if (el) el.hidden = !mostrar;
  }
  document.addEventListener("htmx:sendError", function () { aviso(true); });
  document.addEventListener("htmx:responseError", function (e) {
    var estado = e.detail.xhr ? e.detail.xhr.status : 0;
    if (estado === 0 || estado >= 500) aviso(true);
  });
  document.addEventListener("htmx:afterRequest", function (e) {
    if (e.detail.successful) aviso(false);
  });

  // ------------------------------------------------------------ menú lateral (FR-101 a FR-104, R1)
  // Por debajo de 1024 px el menú se abre con el botón ☰; por encima está siempre visible (CSS).

  function botonMenu() { return document.querySelector(".boton-menu"); }
  function fondoMenu() { return document.querySelector(".menu-fondo"); }
  function menuAbierto() { return document.body.classList.contains("menu-abierto"); }

  function abrirMenu() {
    var boton = botonMenu();
    if (!boton) return;
    document.body.classList.add("menu-abierto");
    var fondo = fondoMenu();
    if (fondo) fondo.hidden = false;
    boton.setAttribute("aria-expanded", "true");
    boton.setAttribute("aria-label", "Cerrar menú");
    var primero = document.querySelector("#menu-lateral a");
    if (primero) primero.focus();
  }

  function cerrarMenu(devolverFoco) {
    var boton = botonMenu();
    if (!boton) return;
    document.body.classList.remove("menu-abierto");
    var fondo = fondoMenu();
    if (fondo) fondo.hidden = true;
    boton.setAttribute("aria-expanded", "false");
    boton.setAttribute("aria-label", "Abrir menú");
    if (devolverFoco) boton.focus();
  }

  document.addEventListener("click", function (e) {
    if (!botonMenu() || !e.target.closest) return;
    if (e.target.closest(".boton-menu")) {
      if (menuAbierto()) cerrarMenu(true); else abrirMenu();
    } else if (e.target.closest(".menu-fondo")) {
      cerrarMenu(true);
    } else if (e.target.closest("#menu-lateral a")) {
      cerrarMenu(false);
    }
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && menuAbierto()) cerrarMenu(true);
  });

  // ------------------------------------------------------------ no salir con guardados pendientes (R3)
  // En la pantalla de presupuesto, «Volver al historial» y los enlaces del menú esperan a que terminen
  // los guardados en curso. Si alguno falla (sin conexión, error del servidor o dato no válido), no se sale.

  var pendientes = 0;
  var destino = null;

  function peticionFallida(detalle) {
    var estado = detalle && detalle.xhr ? detalle.xhr.status : 0;
    return estado === 0 || estado >= 400;
  }

  document.addEventListener("htmx:beforeRequest", function () { pendientes += 1; });
  document.addEventListener("htmx:afterRequest", function (e) {
    pendientes = Math.max(0, pendientes - 1);
    if (destino !== null && peticionFallida(e.detail)) destino = null;
    if (destino !== null && pendientes === 0) {
      var url = destino;
      destino = null;
      window.location.href = url;
    }
  });

  document.addEventListener("click", function (e) {
    if (!e.target.closest || !document.querySelector(".boton-volver")) return;
    var enlace = e.target.closest(".boton-volver, #menu-lateral a");
    if (!enlace || pendientes === 0) return;
    if (e.button !== 0 || e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return;
    e.preventDefault();
    destino = enlace.getAttribute("href");
  });

  // ------------------------------------------------------------ formulario de cliente
  // Particular solo en España; «NIF-IVA verificado» solo para Otro país UE (P3).
  // Tipo de documento y país según categoría y territorio (FR-112 a FR-114, R7, R8).
  // El servidor lo vuelve a comprobar.

  function ajustarTipoDocumento(form, clave) {
    var tipo = form.querySelector("select[name=tipo_documento]");
    if (!tipo) return;
    var preseleccion = "";
    Array.prototype.forEach.call(tipo.options, function (op) {
      if (!op.value) return; // «Sin indicar» siempre disponible
      var permitido = (op.getAttribute("data-permitido-en") || "").split(" ").indexOf(clave) !== -1;
      op.disabled = !permitido;
      op.hidden = !permitido;
      if ((op.getAttribute("data-preseleccion-en") || "").split(" ").indexOf(clave) !== -1) {
        preseleccion = op.value;
      }
    });
    var actual = tipo.options[tipo.selectedIndex];
    if (!actual || !actual.value || actual.disabled) tipo.value = preseleccion;
  }

  function ajustarPais(form, territorio) {
    var pais = form.querySelector("select.selector-pais");
    if (!pais) return;
    var fijo = form.querySelector("input.pais-fijo");
    var espana = territorio === "peninsula" || territorio === "canarias";

    if (espana) {
      pais.value = "España";
      pais.disabled = true;
      // Un select desactivado no se envía: el valor va en un campo oculto.
      if (!fijo) {
        fijo = document.createElement("input");
        fijo.type = "hidden";
        fijo.name = "pais";
        fijo.className = "pais-fijo";
        pais.parentNode.insertBefore(fijo, pais.nextSibling);
      }
      fijo.value = "España";
      return;
    }

    if (fijo) fijo.parentNode.removeChild(fijo);
    pais.disabled = false;
    var seleccionado = pais.options[pais.selectedIndex];
    Array.prototype.forEach.call(pais.options, function (op) {
      var permitido;
      if (op.classList.contains("pais-revisar")) {
        permitido = op === seleccionado; // valor de v1: visible mientras siga seleccionado
      } else if (!op.value) {
        permitido = true; // «Elige un país»
      } else if (territorio === "ue") {
        permitido = op.hasAttribute("data-ue") && op.value !== "España";
      } else {
        permitido = !op.hasAttribute("data-ue");
      }
      op.disabled = !permitido;
      op.hidden = !permitido;
    });
    if (seleccionado && seleccionado.disabled) pais.value = "";
  }

  function ajustarCliente(form) {
    var categoria = form.querySelector("[name=categoria]");
    var territorio = form.querySelector("[name=territorio]");
    var casilla = form.querySelector(".campo-verificado");
    if (!categoria || !territorio) return;
    var particular = categoria.value === "particular";
    Array.prototype.forEach.call(territorio.options, function (op) {
      var fuera = op.value === "ue" || op.value === "fuera_ue";
      op.disabled = particular && fuera;
      op.hidden = particular && fuera;
    });
    if (particular && (territorio.value === "ue" || territorio.value === "fuera_ue")) {
      territorio.value = "peninsula";
    }
    if (casilla) {
      var ue = territorio.value === "ue";
      casilla.hidden = !ue;
      if (!ue) {
        var input = casilla.querySelector("input");
        if (input) input.checked = false;
      }
    }
    ajustarTipoDocumento(form, categoria.value + ":" + territorio.value);
    ajustarPais(form, territorio.value);
  }
  function prepararFormularios(raiz) {
    (raiz || document).querySelectorAll("form.form-cliente").forEach(ajustarCliente);
  }
  document.addEventListener("change", function (e) {
    var form = e.target.closest && e.target.closest("form.form-cliente");
    if (form && (e.target.name === "categoria" || e.target.name === "territorio")) ajustarCliente(form);
  });
  document.addEventListener("DOMContentLoaded", function () { prepararFormularios(); });
  document.addEventListener("htmx:afterSettle", function (e) { prepararFormularios(e.target); });
})();
