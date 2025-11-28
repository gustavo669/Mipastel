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

    document.getElementById('saborNormal')?.addEventListener('change', () => {
        toggleOtro('saborNormal', 'saborOtroNormal', 'precioOtroNormal');
        actualizarPrecioNormal();
    });
    document.getElementById('tamanoNormal')?.addEventListener('change', actualizarPrecioNormal);
    document.getElementById('cantidadNormal')?.addEventListener('input', actualizarPrecioNormal);
    document.getElementById('precioOtroNormal')?.addEventListener('input', actualizarPrecioNormal);

    document.getElementById('saborCliente')?.addEventListener('change', () => {
        toggleOtro('saborCliente', 'saborOtroCliente', 'precioOtroCliente');
        actualizarPrecioCliente();
    });
    document.getElementById('tamanoCliente')?.addEventListener('change', actualizarPrecioCliente);
    document.getElementById('cantidadCliente')?.addEventListener('input', actualizarPrecioCliente);
    document.getElementById('precioOtroCliente')?.addEventListener('input', actualizarPrecioCliente);

    document.getElementById('formNormal')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        await registrarDirecto('normal');
    });

    document.getElementById('formCliente')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        await registrarDirecto('cliente');
    });

    actualizarPrecioNormal();
    actualizarPrecioCliente();
});

function toggleOtro(selectId, inputId, priceInputId) {
    const select = document.getElementById(selectId);
    const input = document.getElementById(inputId);
    const priceInput = document.getElementById(priceInputId);

    if (select && input) {
        if (select.value === "Otro") {
            input.classList.remove("d-none");
            input.required = true;
            if (priceInput) {
                priceInput.classList.remove("d-none");
                priceInput.required = true;
            }
        } else {
            input.classList.add("d-none");
            input.required = false;
            input.value = "";
            if (priceInput) {
                priceInput.classList.add("d-none");
                priceInput.required = false;
                priceInput.value = "";
            }
        }
    }
}

async function actualizarPrecioNormal() {
    const sabor = document.getElementById("saborNormal")?.value;
    const tamano = document.getElementById("tamanoNormal")?.value;
    const cantidad = parseFloat(document.getElementById("cantidadNormal")?.value) || 1;
    const precioUnitarioEl = document.getElementById("precioUnitarioNormal");
    const precioTotalEl = document.getElementById("precioTotalNormal");
    const precioManualEl = document.getElementById("precioOtroNormal");
    const precioManual = parseFloat(precioManualEl?.value) || 0;

    if (!precioUnitarioEl || !precioTotalEl || !precioManualEl) return;

    if (sabor === "Otro" || tamano === "Otro" || precioManual > 0) {
        const precioUnitario = precioManual > 0 ? precioManual : 0.00;
        precioUnitarioEl.textContent = "Q" + precioUnitario.toFixed(2) + (precioManual > 0 ? " (Manual)" : "");
        precioTotalEl.textContent = "Q" + (precioUnitario * cantidad).toFixed(2);
        precioManualEl.classList.remove("d-none");
        precioManualEl.required = true;
        return;
    }

    if (!sabor || !tamano) {
        precioUnitarioEl.textContent = "Q0.00";
        precioTotalEl.textContent = "Q0.00";
        precioManualEl.classList.add("d-none");
        precioManualEl.required = false;
        return;
    }

    try {
        const resp = await fetch(`/api/obtener-precio?sabor=${encodeURIComponent(sabor)}&tamano=${encodeURIComponent(tamano)}`);
        const data = await resp.json();

        if (data.encontrado && data.precio > 0) {
            precioUnitarioEl.textContent = "Q" + data.precio.toFixed(2);
            precioTotalEl.textContent = "Q" + (data.precio * cantidad).toFixed(2);
            precioManualEl.classList.add("d-none");
            precioManualEl.required = false;
        } else {
            precioUnitarioEl.textContent = "Q0.00 (Manual Requerido)";
            precioTotalEl.textContent = "Q0.00";
            precioManualEl.classList.remove("d-none");
            precioManualEl.required = true;
        }
    } catch (error) {
        console.error("Error al obtener precio normal:", error);
        precioUnitarioEl.textContent = "Q0.00 (Error)";
        precioTotalEl.textContent = "Q0.00";
        precioManualEl.classList.remove("d-none");
        precioManualEl.required = true;
    }
}

async function actualizarPrecioCliente() {
    const sabor = document.getElementById("saborCliente")?.value;
    const tamano = document.getElementById("tamanoCliente")?.value;
    const cantidad = parseFloat(document.getElementById("cantidadCliente")?.value) || 1;
    const precioUnitarioEl = document.getElementById("precioUnitarioCliente");
    const precioTotalEl = document.getElementById("precioTotalCliente");
    const precioManualEl = document.getElementById("precioOtroCliente");
    const precioManual = parseFloat(precioManualEl?.value) || 0;

    if (!precioUnitarioEl || !precioTotalEl || !precioManualEl) return;

    if (sabor === "Otro" || tamano === "Otro" || precioManual > 0) {
        const precioUnitario = precioManual > 0 ? precioManual : 0.00;
        precioUnitarioEl.textContent = "Q" + precioUnitario.toFixed(2) + (precioManual > 0 ? " (Manual)" : "");
        precioTotalEl.textContent = "Q" + (precioUnitario * cantidad).toFixed(2);
        precioManualEl.classList.remove("d-none");
        precioManualEl.required = true;
        return;
    }

    if (!sabor || !tamano) {
        precioUnitarioEl.textContent = "Q0.00";
        precioTotalEl.textContent = "Q0.00";
        precioManualEl.classList.add("d-none");
        precioManualEl.required = false;
        return;
    }

    try {
        const resp = await fetch(`/api/obtener-precio?sabor=${encodeURIComponent(sabor)}&tamano=${encodeURIComponent(tamano)}`);
        const data = await resp.json();

        if (data.encontrado && data.precio > 0) {
            precioUnitarioEl.textContent = "Q" + data.precio.toFixed(2);
            precioTotalEl.textContent = "Q" + (data.precio * cantidad).toFixed(2);
            precioManualEl.classList.add("d-none");
            precioManualEl.required = false;
        } else {
            precioUnitarioEl.textContent = "Q0.00 (Manual Requerido)";
            precioTotalEl.textContent = "Q0.00";
            precioManualEl.classList.remove("d-none");
            precioManualEl.required = true;
        }
    } catch (error) {
        console.error("Error al obtener precio cliente:", error);
        precioUnitarioEl.textContent = "Q0.00 (Error)";
        precioTotalEl.textContent = "Q0.00";
        precioManualEl.classList.remove("d-none");
        precioManualEl.required = true;
    }
}

async function registrarDirecto(tipo) {
    const form = tipo === 'normal' ? document.getElementById('formNormal') : document.getElementById('formCliente');
    const formData = new FormData(form);

    const endpoint = tipo === 'normal' ? '/normales/registrar' : '/clientes/registrar';

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            alert('Pedido registrado correctamente');
            form.reset();
            establecerFechaManana(tipo === 'normal' ? 'fechaEntregaNormal' : 'fechaEntregaCliente');
            if (typeof cargarPedidosRegistrados === 'function') {
                cargarPedidosRegistrados();
            }
        } else {
            const error = await response.json();
            alert('Error: ' + (error.detail || 'No se pudo registrar'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al registrar pedido');
    }
}