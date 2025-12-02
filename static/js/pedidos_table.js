// JavaScript para cargar y manejar tablas de pedidos registrados - ACTUALIZADO

// Función principal para cargar pedidos registrados
async function cargarPedidosRegistrados(fecha = null) {
    if (!fecha) {
        // Usar fecha de inicio si existe, sino usar hoy
        const fechaInput = document.getElementById('fechaInicio');
        fecha = fechaInput ? fechaInput.value : new Date().toISOString().split('T')[0];
    }

    try {
        // Cargar pedidos normales
        await cargarPedidosNormales(fecha);

        // Cargar pedidos de clientes
        await cargarPedidosClientes(fecha);
    } catch (error) {
        console.error('Error cargando pedidos:', error);
        alert('Error al cargar los pedidos');
    }
}

// Cargar pedidos normales (tienda) - CON TODAS LAS COLUMNAS
async function cargarPedidosNormales(fecha) {
    try {
        const resp = await fetch(`/api/pedidos/normales?fecha=${fecha}`);
        const data = await resp.json();

        const tbody = document.getElementById('tablaNormalesRegistrados');

        if (!data.pedidos || data.pedidos.length === 0) {
            tbody.innerHTML = '<tr><td colspan="11" class="text-center text-muted">No hay pedidos para esta fecha</td></tr>';
            return;
        }

        tbody.innerHTML = '';

        data.pedidos.forEach(pedido => {
            const row = document.createElement('tr');
            const editable = pedido.editable;
            const estadoBadge = editable
                ? '<span class="badge bg-success">Editable</span>'
                : '<span class="badge bg-secondary">Bloqueado</span>';

            row.innerHTML = `
                <td class="text-center">${pedido.id || ''}</td>
                <td>${pedido.sabor || ''}</td>
                <td>${pedido.tamano || ''}</td>
                <td class="text-end">Q${(pedido.precio || 0).toFixed(2)}</td>
                <td class="text-center">${pedido.cantidad || 0}</td>
                <td class="text-end"><strong>Q${(pedido.total || 0).toFixed(2)}</strong></td>
                <td class="text-center"><span class="badge bg-primary">${pedido.sucursal || ''}</span></td>
                <td class="text-center">${formatearFechaSolo(pedido.fecha_entrega)}</td>
                <td class="text-center">${formatearFechaHora(pedido.fecha)}</td>
                <td class="text-center">${estadoBadge}</td>
                <td class="text-center">
                    ${editable ? `
                        <button class="btn btn-sm btn-primary me-1" onclick="editarPedidoNormal(${pedido.id})" title="Editar">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="eliminarPedidoNormal(${pedido.id})" title="Eliminar">
                            <i class="fas fa-trash"></i>
                        </button>
                    ` : '<span class="text-muted">-</span>'}
                </td>
            `;

            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error cargando pedidos normales:', error);
        const tbody = document.getElementById('tablaNormalesRegistrados');
        tbody.innerHTML = '<tr><td colspan="11" class="text-center text-danger">Error al cargar pedidos</td></tr>';
    }
}

// Cargar pedidos de clientes - CON TODAS LAS COLUMNAS
async function cargarPedidosClientes(fecha) {
    try {
        const resp = await fetch(`/api/pedidos/clientes?fecha=${fecha}`);
        const data = await resp.json();

        const tbody = document.getElementById('tablaClientesRegistrados');

        if (!data.pedidos || data.pedidos.length === 0) {
            tbody.innerHTML = '<tr><td colspan="14" class="text-center text-muted">No hay pedidos para esta fecha</td></tr>';
            return;
        }

        tbody.innerHTML = '';

        data.pedidos.forEach(pedido => {
            const row = document.createElement('tr');
            const editable = pedido.editable;
            const estadoBadge = editable
                ? '<span class="badge bg-success">Editable</span>'
                : '<span class="badge bg-secondary">Bloqueado</span>';

            row.innerHTML = `
                <td class="text-center">${pedido.id || ''}</td>
                <td class="text-center">
                    ${pedido.color ? `
                        <span class="badge-color" style="background-color: ${pedido.color}; color: #000; padding: 5px 10px; border-radius: 8px; font-weight: 600;">
                            ${pedido.color}
                        </span>
                    ` : '<span class="text-muted">-</span>'}
                </td>
                <td>${pedido.sabor || ''}</td>
                <td>${pedido.tamano || ''}</td>
                <td class="text-center">${pedido.cantidad || 0}</td>
                <td class="text-end">Q${(pedido.precio || 0).toFixed(2)}</td>
                <td class="text-end"><strong>Q${(pedido.total || 0).toFixed(2)}</strong></td>
                <td class="text-center"><span class="badge bg-primary">${pedido.sucursal || ''}</span></td>
                <td class="text-center">${formatearFechaHora(pedido.fecha)}</td>
                <td class="text-center">${formatearFechaSolo(pedido.fecha_entrega)}</td>
                <td class="text-truncate" style="max-width: 150px;" title="${pedido.dedicatoria || ''}">${pedido.dedicatoria || '-'}</td>
                <td class="text-truncate" style="max-width: 150px;" title="${pedido.detalles || ''}">${pedido.detalles || '-'}</td>
                <td class="text-center">${estadoBadge}</td>
                <td class="text-center">
                    ${editable ? `
                        <button class="btn btn-sm btn-primary me-1" onclick="editarPedidoCliente(${pedido.id})" title="Editar">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="eliminarPedidoCliente(${pedido.id})" title="Eliminar">
                            <i class="fas fa-trash"></i>
                        </button>
                    ` : '<span class="text-muted">-</span>'}
                </td>
            `;

            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error cargando pedidos clientes:', error);
        const tbody = document.getElementById('tablaClientesRegistrados');
        tbody.innerHTML = '<tr><td colspan="14" class="text-center text-danger">Error al cargar pedidos</td></tr>';
    }
}

// Funciones auxiliares para formatear fechas
function formatearFechaSolo(fecha) {
    if (!fecha) return '-';
    try {
        const f = new Date(fecha);
        const dia = String(f.getDate()).padStart(2, '0');
        const mes = String(f.getMonth() + 1).padStart(2, '0');
        const anio = f.getFullYear();
        return `${dia}/${mes}/${anio}`;
    } catch {
        return '-';
    }
}

function formatearFechaHora(fecha) {
    if (!fecha) return '-';
    try {
        const f = new Date(fecha);
        const dia = String(f.getDate()).padStart(2, '0');
        const mes = String(f.getMonth() + 1).padStart(2, '0');
        const anio = f.getFullYear();
        const hora = String(f.getHours()).padStart(2, '0');
        const min = String(f.getMinutes()).padStart(2, '0');
        return `${dia}/${mes}/${anio} ${hora}:${min}`;
    } catch {
        return '-';
    }
}

// Editar pedido normal
async function editarPedidoNormal(id) {
    try {
        const fecha = document.getElementById('fechaInicio')?.value || new Date().toISOString().split('T')[0];
        const resp = await fetch(`/api/pedidos/normales?fecha=${fecha}`);
        const data = await resp.json();
        const pedido = data.pedidos.find(p => p.id === id);

        if (!pedido) {
            alert('Pedido no encontrado');
            return;
        }

        document.getElementById('editIdNormal').value = pedido.id;
        document.getElementById('editSaborNormal').value = pedido.sabor || '';
        document.getElementById('editTamanoNormal').value = pedido.tamano || '';
        document.getElementById('editCantidadNormal').value = pedido.cantidad || 1;
        document.getElementById('editFechaNormal').value = pedido.fecha_entrega || '';
        document.getElementById('editDetallesNormal').value = pedido.detalles || '';

        const hoy = new Date().toISOString().split('T')[0];
        document.getElementById('editFechaNormal').min = hoy;

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
    const detalles = document.getElementById('editDetallesNormal').value;

    if (!cantidad || !fecha_entrega) {
        alert('Por favor completa todos los campos requeridos');
        return;
    }

    if (parseInt(cantidad) < 1) {
        alert('La cantidad debe ser mayor a 0');
        return;
    }

    try {
        const formData = new FormData();
        formData.append('cantidad', cantidad);
        formData.append('fecha_entrega', fecha_entrega);
        formData.append('detalles', detalles);

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
        const fecha = document.getElementById('fechaInicio')?.value || new Date().toISOString().split('T')[0];
        const resp = await fetch(`/api/pedidos/clientes?fecha=${fecha}`);
        const data = await resp.json();
        const pedido = data.pedidos.find(p => p.id === id);

        if (!pedido) {
            alert('Pedido no encontrado');
            return;
        }

        document.getElementById('editIdCliente').value = pedido.id;
        document.getElementById('editSaborCliente').value = pedido.sabor || '';
        document.getElementById('editTamanoCliente').value = pedido.tamano || '';
        document.getElementById('editCantidadCliente').value = pedido.cantidad || 1;
        document.getElementById('editFechaCliente').value = pedido.fecha_entrega || '';
        document.getElementById('editColorCliente').value = pedido.color || '';
        document.getElementById('editDedicatoriaCliente').value = pedido.dedicatoria || '';
        document.getElementById('editDetallesCliente').value = pedido.detalles || '';

        const hoy = new Date().toISOString().split('T')[0];
        document.getElementById('editFechaCliente').min = hoy;

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

    if (parseInt(cantidad) < 1) {
        alert('La cantidad debe ser mayor a 0');
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
            alert('Pedido actualizado correctamente');
            bootstrap.Modal.getInstance(document.getElementById('modalEditarCliente')).hide();
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

// Eliminar pedido normal
async function eliminarPedidoNormal(id) {
    if (!confirm('¿Estás seguro de que deseas eliminar este pedido?\n\nEsta acción no se puede deshacer.')) {
        return;
    }

    try {
        const resp = await fetch(`/api/pedidos/normal/${id}`, {
            method: 'DELETE'
        });

        if (resp.ok) {
            alert('Pedido eliminado correctamente');
            cargarPedidosRegistrados();
        } else {
            const error = await resp.json();
            alert('Error: ' + (error.detail || 'No se pudo eliminar'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al eliminar el pedido');
    }
}

// Eliminar pedido cliente
async function eliminarPedidoCliente(id) {
    if (!confirm('¿Estás seguro de que deseas eliminar este pedido?\n\nEsta acción no se puede deshacer.')) {
        return;
    }

    try {
        const resp = await fetch(`/api/pedidos/cliente/${id}`, {
            method: 'DELETE'
        });

        if (resp.ok) {
            alert('Pedido eliminado correctamente');
            cargarPedidosRegistrados();
        } else {
            const error = await resp.json();
            alert('Error: ' + (error.detail || 'No se pudo eliminar'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al eliminar el pedido');
    }
}

// Inicializar cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    const fechaInicio = document.getElementById('fechaInicio');
    if (fechaInicio && !fechaInicio.value) {
        fechaInicio.value = new Date().toISOString().split('T')[0];
    }

    const fechaFin = document.getElementById('fechaFin');
    if (fechaFin && !fechaFin.value) {
        fechaFin.value = new Date().toISOString().split('T')[0];
    }

    // Cargar pedidos al iniciar (solo si estamos en la pestaña de registrados)
    const tabRegistrados = document.querySelector('[data-bs-target="#registrados"]');
    if (tabRegistrados) {
        tabRegistrados.addEventListener('shown.bs.tab', function() {
            cargarPedidosRegistrados();
        });
    }
});