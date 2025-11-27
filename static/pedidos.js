async function cargarPedidosRegistrados() {
    const hoy = new Date().toISOString().split('T')[0];

    try {
        const [respNormales, respClientes] = await Promise.all([
            fetch(`/admin/normales?fecha=${hoy}`),
            fetch(`/admin/clientes?fecha=${hoy}`)
        ]);

        const dataNormales = await respNormales.json();
        const dataClientes = await respClientes.json();

        mostrarTablaRegistrados(dataNormales.normales, 'normal');
        mostrarTablaRegistrados(dataClientes.clientes, 'cliente');

    } catch (error) {
        console.error('Error al cargar pedidos:', error);
    }
}

function mostrarTablaRegistrados(pedidos, tipo) {
    const contenedor = tipo === 'normal' ?
        document.getElementById('tablaRegistradosNormales') :
        document.getElementById('tablaRegistradosClientes');

    if (!pedidos || pedidos.length === 0) {
        contenedor.innerHTML = '<p class="text-muted">No hay pedidos registrados hoy</p>';
        return;
    }

    let tabla = `
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Sabor</th>
                        <th>Tamaño</th>
                        <th>Cantidad</th>
                        <th>Precio</th>
                        <th>Total</th>
                        <th>Fecha Entrega</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
    `;

    pedidos.forEach(pedido => {
        const total = pedido.precio * pedido.cantidad;
        tabla += `
            <tr>
                <td>${pedido.id}</td>
                <td>${pedido.sabor}</td>
                <td>${pedido.tamano}</td>
                <td>${pedido.cantidad}</td>
                <td>Q${pedido.precio.toFixed(2)}</td>
                <td><strong>Q${total.toFixed(2)}</strong></td>
                <td>${pedido.fecha_entrega || 'N/A'}</td>
                <td>
                    <button class="btn btn-sm btn-edit" onclick="editarPedidoRegistrado(${pedido.id}, '${tipo}')">Editar</button>
                    <button class="btn btn-sm btn-delete" onclick="eliminarPedidoRegistrado(${pedido.id}, '${tipo}')">Eliminar</button>
                </td>
            </tr>
        `;
    });

    tabla += `
                </tbody>
            </table>
        </div>
    `;

    contenedor.innerHTML = tabla;
}

async function editarPedidoRegistrado(id, tipo) {
    try {
        const endpoint = tipo === 'normal' ?
            `/admin/normales/${id}` :
            `/admin/clientes/${id}`;

        const response = await fetch(endpoint);
        const data = await response.json();
        const pedido = data.pedido;

        const nuevoSabor = prompt('Nuevo sabor:', pedido.sabor);
        if (!nuevoSabor) return;

        const nuevoTamano = prompt('Nuevo tamaño:', pedido.tamano);
        if (!nuevoTamano) return;

        const nuevaCantidad = prompt('Nueva cantidad:', pedido.cantidad);
        if (!nuevaCantidad) return;

        const nuevoPrecio = prompt('Nuevo precio unitario:', pedido.precio);
        if (!nuevoPrecio) return;

        const actualizacion = {
            sabor: nuevoSabor,
            tamano: nuevoTamano,
            cantidad: parseInt(nuevaCantidad),
            precio: parseFloat(nuevoPrecio),
            sucursal: pedido.sucursal,
            fecha_entrega: pedido.fecha_entrega
        };

        const updateResponse = await fetch(endpoint, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(actualizacion)
        });

        if (updateResponse.ok) {
            alert('Pedido actualizado correctamente');
            cargarPedidosRegistrados();
        } else {
            alert('Error al actualizar pedido');
        }

    } catch (error) {
        console.error('Error:', error);
        alert('Error al editar pedido');
    }
}

async function eliminarPedidoRegistrado(id, tipo) {
    if (!confirm('¿Seguro que deseas eliminar este pedido?')) {
        return;
    }

    try {
        const endpoint = tipo === 'normal' ?
            `/admin/normales/${id}` :
            `/admin/clientes/${id}`;

        const response = await fetch(endpoint, {
            method: 'DELETE'
        });

        if (response.ok) {
            alert('Pedido eliminado correctamente');
            cargarPedidosRegistrados();
        } else {
            alert('Error al eliminar pedido');
        }

    } catch (error) {
        console.error('Error:', error);
        alert('Error al eliminar pedido');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    cargarPedidosRegistrados();

    setInterval(cargarPedidosRegistrados, 60000);
});