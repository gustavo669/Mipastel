// JavaScript para cargar y manejar tablas de pedidos registrados

// Función principal para cargar pedidos registrados
async function cargarPedidosRegistrados(fecha = null) {
    if (!fecha) {
        fecha = document.getElementById('fechaBusqueda')?.value || new Date().toISOString().split('T')[0];
    }


    try {
        // Cargar pedidos normales
        await cargarPedidosNormales(hoy);

        // Cargar pedidos de clientes
        await cargarPedidosClientes(hoy);
    } catch (error) {
        console.error('Error cargando pedidos:', error);
        alert('Error al cargar los pedidos');
    }
}

// Cargar pedidos normales (tienda)
async function cargarPedidosNormales(fecha) {
    try {
        const resp = await fetch(`/api/pedidos/normales?fecha=${fecha}`);
        const data = await resp.json();

        const tbody = document.getElementById('tablaNormalesRegistrados');

        if (!data.pedidos || data.pedidos.length === 0) {
            tbody.innerHTML = '<tr><td colspan="10" class="text-center">No hay pedidos para hoy</td></tr>';
            return;
        }

        tbody.innerHTML = '';

        data.pedidos.forEach(pedido => {
            const row = document.createElement('tr');
            const editable = pedido.editable;
            const estadoBadge = editable
                ? '<span class="badge badge-editable">Editable</span>'
                : '<span class="badge badge-locked">Bloqueado</span>';

            row.innerHTML = `
                <td>${pedido.id || ''}</td>
                <td>${pedido.sabor || ''}</td>
                <td>${pedido.tamano || ''}</td>
                <td>${pedido.cantidad || 0}</td>
                <td>Q${(pedido.precio || 0).toFixed(2)}</td>
                <td>Q${(pedido.total || 0).toFixed(2)}</td>
                <td>${pedido.fecha_entrega || ''}</td>
                <td>${pedido.detalles || '-'}</td>
                <td>${estadoBadge}</td>
                <td>
                    ${editable ? `
                        <button class="btn btn-sm btn-sm-custom btn-primary me-1" onclick="editarPedidoNormal(${pedido.id})" title="Editar">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-sm-custom btn-danger" onclick="eliminarPedidoNormal(${pedido.id})" title="Eliminar">
                            <i class="fas fa-trash"></i>
                        </button>
                    ` : '-'}
                </td>
            `;

            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error cargando pedidos normales:', error);
        const tbody = document.getElementById('tablaNormalesRegistrados');
        tbody.innerHTML = '<tr><td colspan="10" class="text-center text-danger">Error al cargar</td></tr>';
    }
}

// Cargar pedidos de clientes
async function cargarPedidosClientes(fecha) {
    try {
        const resp = await fetch(`/api/pedidos/clientes?fecha=${fecha}`);
        const data = await resp.json();

        const tbody = document.getElementById('tablaClientesRegistrados');

        if (!data.pedidos || data.pedidos.length === 0) {
            tbody.innerHTML = '<tr><td colspan="12" class="text-center">No hay pedidos para hoy</td></tr>';
            return;
        }

        tbody.innerHTML = '';

        data.pedidos.forEach(pedido => {
            const row = document.createElement('tr');
            const editable = pedido.editable;
            const estadoBadge = editable
                ? '<span class="badge badge-editable">Editable</span>'
                : '<span class="badge badge-locked">Bloqueado</span>';

            row.innerHTML = `
                <td>${pedido.id || ''}</td>
                <td>${pedido.sabor || ''}</td>
                <td>${pedido.tamano || ''}</td>
                <td>${pedido.cantidad || 0}</td>
                <td>Q${(pedido.precio || 0).toFixed(2)}</td>
                <td>Q${(pedido.total || 0).toFixed(2)}</td>
                <td>${pedido.fecha_entrega || ''}</td>
                <td>${pedido.color || '-'}</td>
                <td>${pedido.dedicatoria || '-'}</td>
                <td>${pedido.detalles || '-'}</td>
                <td>${estadoBadge}</td>
                <td>
                    ${editable ? `
                        <button class="btn btn-sm btn-sm-custom btn-primary me-1" onclick="editarPedidoCliente(${pedido.id})" title="Editar">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-sm-custom btn-danger" onclick="eliminarPedidoCliente(${pedido.id})" title="Eliminar">
                            <i class="fas fa-trash"></i>
                        </button>
                    ` : '-'}
                </td>
            `;

            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error cargando pedidos clientes:', error);
        const tbody = document.getElementById('tablaClientesRegistrados');
        tbody.innerHTML = '<tr><td colspan="12" class="text-center text-danger">Error al cargar</td></tr>';
    }
}

// Editar pedido normal
async function editarPedidoNormal(id) {
    try {
        // Fetch pedido data
        const resp = await fetch(`/api/pedidos/normales?fecha=${new Date().toISOString().split('T')[0]}`);
        const data = await resp.json();
        const pedido = data.pedidos.find(p => p.id === id);

        if (!pedido) {
            alert('Pedido no encontrado');
            return;
        }

        // Populate modal
        document.getElementById('editIdNormal').value = pedido.id;
        document.getElementById('editSaborNormal').value = pedido.sabor || '';
        document.getElementById('editTamanoNormal').value = pedido.tamano || '';
        document.getElementById('editCantidadNormal').value = pedido.cantidad || 1;
        document.getElementById('editFechaNormal').value = pedido.fecha_entrega || '';

        // Set minimum date to today
        const hoy = new Date().toISOString().split('T')[0];
        document.getElementById('editFechaNormal').min = hoy;

        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('modalEditarNormal'));
        modal.show();
    } catch (error) {
        console.error('Error:', error);
        alert('Error al cargar el pedido');
    }
}

// Guardar edición de pedido normal
async function guardarEdicionNormal() {
    const id = document.getElementById('editIdNormal').value;
    const cantidad = document.getElementById('editCantidadNormal').value;
    const fecha_entrega = document.getElementById('editFechaNormal').value;

    if (!cantidad || !fecha_entrega) {
        alert('Por favor completa todos los campos');
        return;
    }

    try {
        const formData = new FormData();
        formData.append('cantidad', cantidad);
        formData.append('fecha_entrega', fecha_entrega);

        const resp = await fetch(`/api/pedidos/normal/${id}`, {
            method: 'PUT',
            body: formData
        });

        if (resp.ok) {
            alert('Pedido actualizado correctamente');
            bootstrap.Modal.getInstance(document.getElementById('modalEditarNormal')).hide();
            cargarPedidosRegistrados();
        } else {
            const error = await resp.json();
            alert('Error: ' + (error.detail || 'No se pudo actualizar'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al actualizar el pedido');
    }
}

// Editar pedido cliente
async function editarPedidoCliente(id) {
    try {
        // Fetch pedido data
        const resp = await fetch(`/api/pedidos/clientes?fecha=${new Date().toISOString().split('T')[0]}`);
        const data = await resp.json();
        const pedido = data.pedidos.find(p => p.id === id);

        if (!pedido) {
            alert('Pedido no encontrado');
            return;
        }

        // Populate modal
        document.getElementById('editIdCliente').value = pedido.id;
        document.getElementById('editSaborCliente').value = pedido.sabor || '';
        document.getElementById('editTamanoCliente').value = pedido.tamano || '';
        document.getElementById('editCantidadCliente').value = pedido.cantidad || 1;
        document.getElementById('editFechaCliente').value = pedido.fecha_entrega || '';
        document.getElementById('editColorCliente').value = pedido.color || '';
        document.getElementById('editDedicatoriaCliente').value = pedido.dedicatoria || '';
        document.getElementById('editDetallesCliente').value = pedido.detalles || '';

        // Set minimum date to today
        const hoy = new Date().toISOString().split('T')[0];
        document.getElementById('editFechaCliente').min = hoy;

        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('modalEditarCliente'));
        modal.show();
    } catch (error) {
        console.error('Error:', error);
        alert('Error al cargar el pedido');
    }
}

// Guardar edición de pedido cliente
async function guardarEdicionCliente() {
    const id = document.getElementById('editIdCliente').value;
    const cantidad = document.getElementById('editCantidadCliente').value;
    const fecha_entrega = document.getElementById('editFechaCliente').value;
    const color = document.getElementById('editColorCliente').value;
    const dedicatoria = document.getElementById('editDedicatoriaCliente').value;
    const detalles = document.getElementById('editDetallesCliente').value;

    if (!cantidad || !fecha_entrega) {
        alert('Por favor completa los campos requeridos');
        return;
    }

    try {
        const formData = new FormData();
        formData.append('cantidad', cantidad);
        formData.append('fecha_entrega', fecha_entrega);
        if (color) formData.append('color', color);
        if (dedicatoria) formData.append('dedicatoria', dedicatoria);
        if (detalles) formData.append('detalles', detalles);

        const resp = await fetch(`/api/pedidos/cliente/${id}`, {
            method: 'PUT',
            body: formData
        });

        if (resp.ok) {
            alert('✅ Pedido actualizado correctamente');
            bootstrap.Modal.getInstance(document.getElementById('modalEditarCliente')).hide();
            cargarPedidosRegistrados();
        } else {
            const error = await resp.json();
            alert('❌ Error: ' + (error.detail || 'No se pudo actualizar'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('❌ Error al actualizar el pedido');
    }
}

// Eliminar pedido normal
async function eliminarPedidoNormal(id) {
    if (!confirm('�Est�s seguro de que deseas eliminar este pedido?\\n\\nEsta acci�n no se puede deshacer.')) {
        return;
    }
    try {
        const resp = await fetch`/api/pedidos/normal/${id}`, { method: 'DELETE' });
        if (resp.ok) {
            alert(' Pedido eliminado correctamente');
            cargarPedidosRegistrados();
        } else {
            const error = await resp.json();
            alert(' Error: ' + (error.detail || 'No se pudo eliminar'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert(' Error al eliminar el pedido');
    }
}

// Eliminar pedido cliente
async function eliminarPedidoCliente(id) {
    if (!confirm('�Est�s seguro de que deseas eliminar este pedido?\\n\\nEsta acci�n no se puede deshacer.')) {
        return;
    }
    try {
        const resp = await fetch`/api/pedidos/cliente/${id}`, { method: 'DELETE' });
        if (resp.ok) {
            alert(' Pedido eliminado correctamente');
            cargarPedidosRegistrados();
        } else {
            const error = await resp.json();
            alert(' Error: ' + (error.detail || 'No se pudo eliminar'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert(' Error al eliminar el pedido');
    }
}
