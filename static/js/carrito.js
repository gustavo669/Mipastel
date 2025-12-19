// Sistema de Carrito para Mi Pastel - VERSIÓN MEJORADA
let cartaNormales = [];
let cartaClientes = [];

const SUCURSAL = document.querySelector('[data-sucursal]')?.getAttribute('data-sucursal') || '';

console.log('SUCURSAL desde navbar:', SUCURSAL);

function obtenerDatosFormulario(tipo) {
    if (tipo === 'normal') {
        const sabor = document.getElementById('saborNormal').value;
        const saborOtro = document.getElementById('saborOtroNormal').value;
        const precioText = document.getElementById('precioUnitarioNormal').textContent
            .replace('Q', '')
            .replace(' (No encontrado)', '')
            .replace(' (Error)', '')
            .replace(' (Manual)', '')
            .trim();

        const esOtro = sabor === 'Otro';
        const datos = {
            sabor: esOtro ? saborOtro : sabor,
            tamano: document.getElementById('tamanoNormal').value,
            cantidad: parseInt(document.getElementById('cantidadNormal').value) || 1,
            fecha_entrega: document.getElementById('fechaEntregaNormal').value,
            precio: parseFloat(precioText) || 0,
            sabor_personalizado: esOtro ? saborOtro : '',
            detalles: '',
            es_otro: esOtro
        };

        console.log('Datos Normal:', datos);
        return datos;
    } else {
        const sabor = document.getElementById('saborCliente').value;
        const saborOtro = document.getElementById('saborOtroCliente').value;
        const precioText = document.getElementById('precioUnitarioCliente').textContent
            .replace('Q', '')
            .replace(' (No encontrado)', '')
            .replace(' (Error)', '')
            .replace(' (Manual)', '')
            .trim();

        const esOtro = sabor === 'Otro';
        const datos = {
            sabor: esOtro ? saborOtro : sabor,
            tamano: document.getElementById('tamanoCliente').value,
            cantidad: parseInt(document.getElementById('cantidadCliente').value) || 1,
            fecha_entrega: document.getElementById('fechaEntregaCliente').value,
            color: document.getElementById('colorCliente').value || '',
            dedicatoria: document.getElementById('dedicatoriaCliente').value || '',
            detalles: document.getElementById('detallesCliente').value || '',
            precio: parseFloat(precioText) || 0,
            sabor_personalizado: esOtro ? saborOtro : '',
            foto: null,
            es_otro: esOtro
        };

        console.log('Datos Cliente:', datos);
        return datos;
    }
}

function validarFormulario(datos, tipo) {
    console.log('Validando:', tipo, datos);

    if (!datos.sabor || !datos.tamano || !datos.cantidad || !datos.fecha_entrega) {
        console.warn('Falta campo requerido');
        alert('Por favor completa todos los campos requeridos');
        return false;
    }

    if (datos.precio <= 0 || isNaN(datos.precio)) {
        console.warn('Precio inválido:', datos.precio);
        alert('El precio no es válido. Verifica que el sabor y tamaño tengan precio configurado.');
        return false;
    }

    return true;
}

function limpiarFormulario(tipo) {
    const fechas = obtenerFechas();

    if (tipo === 'normal') {
        document.getElementById('saborNormal').value = '';
        document.getElementById('tamanoNormal').value = '';
        document.getElementById('cantidadNormal').value = '1';
        document.getElementById('saborOtroNormal').classList.add('d-none');
        document.getElementById('precioOtroNormal').classList.add('d-none');
        document.getElementById('fechaEntregaNormal').value = fechas.manana;
        document.getElementById('precioUnitarioNormal').textContent = 'Q0.00';
        document.getElementById('precioTotalNormal').textContent = 'Q0.00';
    } else {
        document.getElementById('saborCliente').value = '';
        document.getElementById('tamanoCliente').value = '';
        document.getElementById('cantidadCliente').value = '1';
        document.getElementById('colorCliente').value = '';
        document.getElementById('dedicatoriaCliente').value = '';
        document.getElementById('detallesCliente').value = '';
        document.getElementById('saborOtroCliente').classList.add('d-none');
        document.getElementById('precioOtroCliente').classList.add('d-none');
        document.getElementById('fechaEntregaCliente').value = fechas.manana;
        document.getElementById('precioUnitarioCliente').textContent = 'Q0.00';
        document.getElementById('precioTotalCliente').textContent = 'Q0.00';
    }
}

function obtenerFechas() {
    const hoy = new Date();
    const manana = new Date(hoy);
    manana.setDate(manana.getDate() + 1);

    const formatoFecha = (fecha) => fecha.toISOString().split('T')[0];

    return {
        hoy: formatoFecha(hoy),
        manana: formatoFecha(manana)
    };
}

function agregarAlCarrito(tipo) {
    console.log('=== Agregar al carrito:', tipo);
    const datos = obtenerDatosFormulario(tipo);

    if (!validarFormulario(datos, tipo)) return;

    if (tipo === 'normal') {
        cartaNormales.push(datos);
        console.log('Carrito normales:', cartaNormales);
    } else {
        cartaClientes.push(datos);
        console.log('Carrito clientes:', cartaClientes);
    }

    actualizarVista();
    limpiarFormulario(tipo);

    const tab = new bootstrap.Tab(document.querySelector('[data-bs-target="#pedidos"]'));
    tab.show();
}

function eliminarDeLista(tipo, index) {
    if (tipo === 'normal') {
        cartaNormales.splice(index, 1);
    } else {
        cartaClientes.splice(index, 1);
    }
    actualizarVista();
}

function limpiarLista() {
    if (!confirm('¿Limpiar toda la lista?')) return;
    cartaNormales = [];
    cartaClientes = [];
    actualizarVista();
}

function actualizarVista() {
    const total = cartaNormales.length + cartaClientes.length;
    const badge = document.getElementById('cartBadge');
    badge.textContent = total;
    badge.style.display = total > 0 ? 'inline' : 'none';

    document.getElementById('countNormalesLista').textContent = cartaNormales.length;
    document.getElementById('countClientesLista').textContent = cartaClientes.length;

    const listaNorm = document.getElementById('listaNormales');
    const listaCli = document.getElementById('listaClientes');

    listaNorm.innerHTML = cartaNormales.length === 0
        ? '<p class="text-muted">No hay pedidos de tienda</p>'
        : '';

    cartaNormales.forEach((p, i) => {
        listaNorm.innerHTML += `
            <div class="cart-item">
                <div class="d-flex justify-content-between">
                    <div>
                        <strong>${p.sabor}</strong> - ${p.tamano} x${p.cantidad}
                        <br><small>Entrega: ${p.fecha_entrega} | Total: Q${(p.precio * p.cantidad).toFixed(2)}</small>
                    </div>
                    <button class="btn btn-sm btn-danger" onclick="eliminarDeLista('normal', ${i})">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        `;
    });

    listaCli.innerHTML = cartaClientes.length === 0
        ? '<p class="text-muted">No hay pedidos de clientes</p>'
        : '';

    cartaClientes.forEach((p, i) => {
        listaCli.innerHTML += `
            <div class="cart-item">
                <div class="d-flex justify-content-between">
                    <div>
                        <strong>${p.sabor}</strong> - ${p.tamano} x${p.cantidad}
                        <br><small>Entrega: ${p.fecha_entrega} | Total: Q${(p.precio * p.cantidad).toFixed(2)}</small>
                        ${p.dedicatoria ? '<br><small>Dedicatoria: ' + p.dedicatoria + '</small>' : ''}
                    </div>
                    <button class="btn btn-sm btn-danger" onclick="eliminarDeLista('cliente', ${i})">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        `;
    });
}

async function registrarTodos() {
    console.log('=== INICIANDO REGISTRO DE TODOS LOS PEDIDOS ===');
    console.log('Normales a registrar:', cartaNormales.length);
    console.log('Clientes a registrar:', cartaClientes.length);
    console.log('Sucursal:', SUCURSAL);

    if (cartaNormales.length === 0 && cartaClientes.length === 0) {
        alert('No hay pedidos en la lista');
        return;
    }

    if (!confirm('¿Registrar todos los pedidos?')) {
        return;
    }

    let exitosos = 0;
    let fallidos = 0;
    const errores = [];

    try {
        // Registrar pedidos normales
        for (let i = 0; i < cartaNormales.length; i++) {
            const pedido = cartaNormales[i];
            console.log(`Registrando pedido normal ${i + 1}:`, pedido);

            const formData = new FormData();
            formData.append('sabor', pedido.sabor);
            formData.append('tamano', pedido.tamano);
            formData.append('cantidad', pedido.cantidad);
            formData.append('sucursal', SUCURSAL);
            formData.append('fecha_entrega', pedido.fecha_entrega);
            formData.append('detalles', pedido.detalles || '');
            formData.append('sabor_personalizado', pedido.sabor_personalizado || '');
            formData.append('precio', pedido.precio);
            formData.append('es_otro', pedido.es_otro || false);

            try {
                const resp = await fetch('/normales/registrar', {
                    method: 'POST',
                    body: formData
                });

                console.log(`Respuesta normal ${i + 1}:`, resp.status, resp.statusText);

                if (resp.ok) {
                    exitosos++;
                    console.log(`✓ Pedido normal ${i + 1} registrado exitosamente`);
                } else {
                    const errorText = await resp.text();
                    console.error(`✗ Error en pedido normal ${i + 1}:`, resp.status);
                    console.error('Response:', errorText);
                    errores.push(`Normal ${i + 1}: ${resp.status}`);
                    fallidos++;
                }
            } catch (e) {
                console.error(`✗ Excepción en pedido normal ${i + 1}:`, e);
                errores.push(`Normal ${i + 1}: ${e.message}`);
                fallidos++;
            }
        }

        // Registrar pedidos de clientes
        for (let i = 0; i < cartaClientes.length; i++) {
            const pedido = cartaClientes[i];
            console.log(`Registrando pedido cliente ${i + 1}:`, pedido);

            const formData = new FormData();
            formData.append('sabor', pedido.sabor);
            formData.append('tamano', pedido.tamano);
            formData.append('cantidad', pedido.cantidad);
            formData.append('sucursal', SUCURSAL);
            formData.append('fecha_entrega', pedido.fecha_entrega);
            formData.append('color', pedido.color || '');
            formData.append('dedicatoria', pedido.dedicatoria || '');
            formData.append('detalles', pedido.detalles || '');
            formData.append('sabor_personalizado', pedido.sabor_personalizado || '');
            formData.append('precio', pedido.precio);
            formData.append('es_otro', pedido.es_otro || false);

            try {
                const resp = await fetch('/clientes/registrar', {
                    method: 'POST',
                    body: formData
                });

                console.log(`Respuesta cliente ${i + 1}:`, resp.status, resp.statusText);

                if (resp.ok) {
                    exitosos++;
                    console.log(`✓ Pedido cliente ${i + 1} registrado exitosamente`);
                } else {
                    const errorText = await resp.text();
                    console.error(`✗ Error en pedido cliente ${i + 1}:`, resp.status);
                    console.error('Response:', errorText);
                    errores.push(`Cliente ${i + 1}: ${resp.status}`);
                    fallidos++;
                }
            } catch (e) {
                console.error(`✗ Excepción en pedido cliente ${i + 1}:`, e);
                errores.push(`Cliente ${i + 1}: ${e.message}`);
                fallidos++;
            }
        }

        console.log('=== RESUMEN DE REGISTRO ===');
        console.log('Exitosos:', exitosos);
        console.log('Fallidos:', fallidos);

        if (exitosos > 0) {
            alert(`✓ ${exitosos} pedido(s) registrado(s) exitosamente`);
            cartaNormales = [];
            cartaClientes = [];
            actualizarVista();
            cargarPedidosRegistrados();
            const tab = new bootstrap.Tab(document.querySelector('[data-bs-target="#registrados"]'));
            tab.show();
        } else {
            alert(`✗ Error: No se registraron pedidos.\n\nDetalles: ${errores.join(', ')}`);
        }

    } catch (error) {
        console.error('Error general:', error);
        alert('Error al registrar pedidos: ' + error.message);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('=== Inicializando carrito ===');
    const fechas = obtenerFechas();

    const dateInputs = ['fechaEntregaNormal', 'fechaEntregaCliente'];
    dateInputs.forEach(id => {
        const input = document.getElementById(id);
        if (input) {
            input.value = fechas.manana;
            input.min = fechas.manana;
        }
    });

    actualizarVista();
    console.log('Carrito inicializado');
});