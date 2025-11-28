let carritoNormales = JSON.parse(localStorage.getItem('carritoNormales') || '[]');
let carritoClientes = JSON.parse(localStorage.getItem('carritoClientes') || '[]');

function actualizarBadge() {
    const total = carritoNormales.length + carritoClientes.length;
    const badge = document.getElementById('cartBadge');
    if (total > 0) {
        badge.textContent = total;
        badge.style.display = 'block';
    } else {
        badge.style.display = 'none';
    }
}

function agregarAlCarrito(tipo) {
    const form = tipo === 'normal' ? document.getElementById('formNormal') : document.getElementById('formCliente');
    const formData = new FormData(form);

    const pedido = {
        id: Date.now(),
        tipo: tipo,
        sabor: formData.get('sabor'),
        sabor_personalizado: formData.get('sabor_personalizado'),
        tamano: formData.get('tamano'),
        cantidad: parseInt(formData.get('cantidad')),
        precio: obtenerPrecioActual(tipo),
        sucursal: formData.get('sucursal'),
        fecha_entrega: formData.get('fecha_entrega'),
        detalles: formData.get('detalles') || '',
        color: formData.get('color') || '',
        dedicatoria: formData.get('dedicatoria') || ''
    };

    if (tipo === 'normal') {
        carritoNormales.push(pedido);
        localStorage.setItem('carritoNormales', JSON.stringify(carritoNormales));
    } else {
        carritoClientes.push(pedido);
        localStorage.setItem('carritoClientes', JSON.stringify(carritoClientes));
    }

    actualizarBadge();
    mostrarCarrito();
    form.reset();

    const tab = new bootstrap.Tab(document.getElementById('pedidos-tab'));
    tab.show();

    alert('Pedido agregado a la lista');
}

function obtenerPrecioActual(tipo) {
    if (tipo === 'normal') {
        const precioText = document.getElementById('precioUnitarioNormal').textContent;
        return parseFloat(precioText.replace('Q', '').replace('(Manual)', '').trim());
    } else {
        const precioText = document.getElementById('precioUnitarioCliente').textContent;
        return parseFloat(precioText.replace('Q', '').replace('(Manual)', '').trim());
    }
}

function mostrarCarrito() {
    const listaNormales = document.getElementById('listaNormales');
    const listaClientes = document.getElementById('listaClientes');

    listaNormales.innerHTML = '';
    listaClientes.innerHTML = '';

    if (carritoNormales.length === 0) {
        listaNormales.innerHTML = '<p class="text-muted">No hay pedidos de tienda en la lista</p>';
    } else {
        carritoNormales.forEach((pedido, index) => {
            listaNormales.innerHTML += crearItemCarrito(pedido, index, 'normal');
        });
    }

    if (carritoClientes.length === 0) {
        listaClientes.innerHTML = '<p class="text-muted">No hay pedidos de clientes en la lista</p>';
    } else {
        carritoClientes.forEach((pedido, index) => {
            listaClientes.innerHTML += crearItemCarrito(pedido, index, 'cliente');
        });
    }

    actualizarBadge();
}

function crearItemCarrito(pedido, index, tipo) {
    const saborFinal = pedido.sabor_personalizado || pedido.sabor;
    const total = pedido.precio * pedido.cantidad;

    return `
        <div class="cart-item mb-2">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <strong>${saborFinal}</strong> - ${pedido.tamano} x${pedido.cantidad}
                    <br>
                    <small>Precio: Q${pedido.precio.toFixed(2)} | Total: Q${total.toFixed(2)}</small>
                    <br>
                    <small>Entrega: ${pedido.fecha_entrega || 'No especificada'}</small>
                </div>
                <div class="btn-group">
                    <button class="btn btn-sm btn-edit" onclick="editarCarrito(${index}, '${tipo}')">Editar</button>
                    <button class="btn btn-sm btn-delete" onclick="eliminarCarrito(${index}, '${tipo}')">Eliminar</button>
                </div>
            </div>
        </div>
    `;
}

function editarCarrito(index, tipo) {
    const carrito = tipo === 'normal' ? carritoNormales : carritoClientes;
    const pedido = carrito[index];

    const form = tipo === 'normal' ? document.getElementById('formNormal') : document.getElementById('formCliente');

    form.querySelector('[name="sabor"]').value = pedido.sabor;
    form.querySelector('[name="tamano"]').value = pedido.tamano;
    form.querySelector('[name="cantidad"]').value = pedido.cantidad;
    form.querySelector('[name="fecha_entrega"]').value = pedido.fecha_entrega;

    if (form.querySelector('[name="detalles"]')) {
        form.querySelector('[name="detalles"]').value = pedido.detalles;
    }
    if (form.querySelector('[name="color"]')) {
        form.querySelector('[name="color"]').value = pedido.color;
    }
    if (form.querySelector('[name="dedicatoria"]')) {
        form.querySelector('[name="dedicatoria"]').value = pedido.dedicatoria;
    }

    eliminarCarrito(index, tipo);

    const tab = new bootstrap.Tab(document.getElementById(tipo === 'normal' ? 'normales-tab' : 'clientes-tab'));
    tab.show();
}

function eliminarCarrito(index, tipo) {
    if (tipo === 'normal') {
        carritoNormales.splice(index, 1);
        localStorage.setItem('carritoNormales', JSON.stringify(carritoNormales));
    } else {
        carritoClientes.splice(index, 1);
        localStorage.setItem('carritoClientes', JSON.stringify(carritoClientes));
    }

    mostrarCarrito();
}

function limpiarCarrito() {
    if (confirm('¿Seguro que deseas limpiar toda la lista?')) {
        carritoNormales = [];
        carritoClientes = [];
        localStorage.removeItem('carritoNormales');
        localStorage.removeItem('carritoClientes');
        mostrarCarrito();
    }
}

async function registrarTodosYGenerarPDF() {
    if (carritoNormales.length === 0 && carritoClientes.length === 0) {
        alert('No hay pedidos en la lista');
        return;
    }

    if (!confirm('¿Registrar todos los pedidos y generar PDF?\n\nNOTA: Los pedidos de clientes se registrarán sin fotos. Si necesitas agregar fotos, regístralos individualmente.')) {
        return;
    }

    try {
        for (const pedido of carritoNormales) {
            const formData = new FormData();
            formData.append('sabor', pedido.sabor);
            formData.append('tamano', pedido.tamano);
            formData.append('cantidad', pedido.cantidad);
            formData.append('sucursal', pedido.sucursal);
            formData.append('fecha_entrega', pedido.fecha_entrega);
            formData.append('detalles', pedido.detalles);
            formData.append('sabor_personalizado', pedido.sabor_personalizado || '');
            formData.append('es_otro', pedido.sabor_personalizado ? 'true' : 'false');

            await fetch('/normales/registrar', {
                method: 'POST',
                body: formData
            });
        }

        for (const pedido of carritoClientes) {
            const formData = new FormData();
            formData.append('sabor', pedido.sabor);
            formData.append('tamano', pedido.tamano);
            formData.append('cantidad', pedido.cantidad);
            formData.append('sucursal', pedido.sucursal);
            formData.append('fecha_entrega', pedido.fecha_entrega);
            formData.append('color', pedido.color);
            formData.append('dedicatoria', pedido.dedicatoria);
            formData.append('detalles', pedido.detalles);
            formData.append('sabor_personalizado', pedido.sabor_personalizado || '');

            await fetch('/clientes/registrar', {
                method: 'POST',
                body: formData
            });
        }

        const hoy = new Date().toISOString().split('T')[0];
        window.open(`/reportes/pdf?fecha=${hoy}`, '_blank');

        limpiarCarrito();
        if (typeof cargarPedidosRegistrados === 'function') {
            cargarPedidosRegistrados();
        }

        alert('Todos los pedidos registrados exitosamente');

    } catch (error) {
        console.error('Error:', error);
        alert('Error al registrar pedidos');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    mostrarCarrito();
    actualizarBadge();
});