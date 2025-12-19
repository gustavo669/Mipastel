function obtenerFechaManana() {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const year = tomorrow.getFullYear();
    const month = String(tomorrow.getMonth() + 1).padStart(2, '0');
    const day = String(tomorrow.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

function establecerFechaManana(inputId) {
    const input = document.getElementById(inputId);
    if (input) {
        input.value = obtenerFechaManana();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    establecerFechaManana('fechaEntregaNormal');
    establecerFechaManana('fechaEntregaCliente');

    // NORMALES
    document.getElementById('saborNormal')?.addEventListener('change', () => {
        toggleOtro('saborNormal', 'saborOtroNormal', 'precioOtroNormal');
        actualizarPrecioNormal();
    });
    document.getElementById('tamanoNormal')?.addEventListener('change', actualizarPrecioNormal);
    document.getElementById('cantidadNormal')?.addEventListener('input', actualizarPrecioNormal);
    document.getElementById('precioOtroNormal')?.addEventListener('input', actualizarPrecioNormal);

    // CLIENTES
    document.getElementById('saborCliente')?.addEventListener('change', () => {
        toggleOtro('saborCliente', 'saborOtroCliente', 'precioOtroCliente');
        actualizarPrecioCliente();
    });
    document.getElementById('tamanoCliente')?.addEventListener('change', actualizarPrecioCliente);
    document.getElementById('cantidadCliente')?.addEventListener('input', actualizarPrecioCliente);
    document.getElementById('precioOtroCliente')?.addEventListener('input', actualizarPrecioCliente);

    actualizarPrecioNormal();
    actualizarPrecioCliente();
});

/**
 * Toggle para mostrar/ocultar campos "Otro"
 * SOLO muestra precio manual si es "Otro"
 */
function toggleOtro(selectId, inputId, priceInputId) {
    const select = document.getElementById(selectId);
    const input = document.getElementById(inputId);
    const priceInput = document.getElementById(priceInputId);

    if (select && input) {
        if (select.value === "Otro") {
            // Mostrar campo de sabor personalizado
            input.classList.remove("d-none");
            input.required = true;

            // MOSTRAR PRECIO MANUAL SOLO SI ES "OTRO"
            if (priceInput) {
                priceInput.classList.remove("d-none");
                priceInput.required = true;
            }
        } else {
            // Ocultar campos
            input.classList.add("d-none");
            input.required = false;
            input.value = "";

            // OCULTAR PRECIO MANUAL SI NO ES "OTRO"
            if (priceInput) {
                priceInput.classList.add("d-none");
                priceInput.required = false;
                priceInput.value = "";
            }
        }
    }
}

/**
 * Actualiza precio para pedidos normales
 */
async function actualizarPrecioNormal() {
    const sabor = document.getElementById("saborNormal")?.value;
    const tamano = document.getElementById("tamanoNormal")?.value;
    const cantidad = parseFloat(document.getElementById("cantidadNormal")?.value) || 1;
    const precioUnitarioEl = document.getElementById("precioUnitarioNormal");
    const precioTotalEl = document.getElementById("precioTotalNormal");
    const precioManualEl = document.getElementById("precioOtroNormal");

    if (!precioUnitarioEl || !precioTotalEl) return;

    // Si es "Otro" y tiene precio manual
    if (sabor === "Otro" && precioManualEl && !precioManualEl.classList.contains('d-none')) {
        const precioManual = parseFloat(precioManualEl.value) || 0;

        if (precioManual > 0) {
            precioUnitarioEl.textContent = "Q" + precioManual.toFixed(2) + " (Manual)";
            precioTotalEl.textContent = "Q" + (precioManual * cantidad).toFixed(2);
            return;
        } else {
            // Sin precio manual aún
            precioUnitarioEl.textContent = "Q0.00 (Ingresa precio)";
            precioTotalEl.textContent = "Q0.00";
            return;
        }
    }

    // Si no es "Otro" o el campo está oculto, obtener precio de BD
    if (!sabor || !tamano || sabor === "Otro") {
        precioUnitarioEl.textContent = "Q0.00";
        precioTotalEl.textContent = "Q0.00";
        return;
    }

    try {
        const resp = await fetch(`/api/obtener-precio?sabor=${encodeURIComponent(sabor)}&tamano=${encodeURIComponent(tamano)}`);
        const data = await resp.json();

        if (data.encontrado && data.precio > 0) {
            precioUnitarioEl.textContent = "Q" + data.precio.toFixed(2);
            precioTotalEl.textContent = "Q" + (data.precio * cantidad).toFixed(2);
        } else {
            precioUnitarioEl.textContent = "Q0.00 (No encontrado)";
            precioTotalEl.textContent = "Q0.00";
        }
    } catch (error) {
        console.error("Error al obtener precio normal:", error);
        precioUnitarioEl.textContent = "Q0.00 (Error)";
        precioTotalEl.textContent = "Q0.00";
    }
}

/**
 * Actualiza precio para pedidos de clientes
 */
async function actualizarPrecioCliente() {
    const sabor = document.getElementById("saborCliente")?.value;
    const tamano = document.getElementById("tamanoCliente")?.value;
    const cantidad = parseFloat(document.getElementById("cantidadCliente")?.value) || 1;
    const precioUnitarioEl = document.getElementById("precioUnitarioCliente");
    const precioTotalEl = document.getElementById("precioTotalCliente");
    const precioManualEl = document.getElementById("precioOtroCliente");

    if (!precioUnitarioEl || !precioTotalEl) return;

    // Si es "Otro" y tiene precio manual
    if (sabor === "Otro" && precioManualEl && !precioManualEl.classList.contains('d-none')) {
        const precioManual = parseFloat(precioManualEl.value) || 0;

        if (precioManual > 0) {
            precioUnitarioEl.textContent = "Q" + precioManual.toFixed(2) + " (Manual)";
            precioTotalEl.textContent = "Q" + (precioManual * cantidad).toFixed(2);
            return;
        } else {
            // Sin precio manual aún
            precioUnitarioEl.textContent = "Q0.00 (Ingresa precio)";
            precioTotalEl.textContent = "Q0.00";
            return;
        }
    }

    // Si no es "Otro" o el campo está oculto, obtener precio de BD
    if (!sabor || !tamano || sabor === "Otro") {
        precioUnitarioEl.textContent = "Q0.00";
        precioTotalEl.textContent = "Q0.00";
        return;
    }

    try {
        const resp = await fetch(`/api/obtener-precio?sabor=${encodeURIComponent(sabor)}&tamano=${encodeURIComponent(tamano)}`);
        const data = await resp.json();

        if (data.encontrado && data.precio > 0) {
            precioUnitarioEl.textContent = "Q" + data.precio.toFixed(2);
            precioTotalEl.textContent = "Q" + (data.precio * cantidad).toFixed(2);
        } else {
            precioUnitarioEl.textContent = "Q0.00 (No encontrado)";
            precioTotalEl.textContent = "Q0.00";
        }
    } catch (error) {
        console.error("Error al obtener precio cliente:", error);
        precioUnitarioEl.textContent = "Q0.00 (Error)";
        precioTotalEl.textContent = "Q0.00";
    }
}