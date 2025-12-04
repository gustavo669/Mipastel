async function registrarDirecto(tipo) {
    const datos = obtenerDatosFormulario(tipo);

    if (!validarFormulario(datos, tipo)) return;

    const formData = new FormData();
    formData.append('sabor', datos.sabor);
    formData.append('tamano', datos.tamano);
    formData.append('cantidad', datos.cantidad);
    formData.append('precio', datos.precio);
    formData.append('sucursal', SUCURSAL);
    formData.append('fecha_entrega', datos.fecha_entrega);
    formData.append('sabor_personalizado', datos.sabor_personalizado || '');

    if (tipo === 'cliente') {
        formData.append('color', datos.color || '');
        formData.append('dedicatoria', datos.dedicatoria || '');
        formData.append('detalles', datos.detalles || '');

        const fotoInput = document.getElementById('fotoCliente');
        if (fotoInput.files.length > 0) {
            formData.append('foto', fotoInput.files[0]);
        }
    } else {
        formData.append('detalles', '');
    }

    const endpoint = tipo === 'normal' ? '/normales/registrar' : '/clientes/registrar';

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            limpiarFormulario(tipo);
            window.location.href = '/static/exito.html';
        } else {
            const error = await response.json();
            let errorMsg = 'No se pudo registrar el pedido';

            if (error.detail) {
                if (Array.isArray(error.detail)) {
                    errorMsg = error.detail.map(e => {
                        if (typeof e === 'object' && e.msg) {
                            return e.msg;
                        }
                        return String(e);
                    }).join(', ');
                } else if (typeof error.detail === 'object') {
                    errorMsg = JSON.stringify(error.detail);
                } else {
                    errorMsg = String(error.detail);
                }
            }

            alert('Error: ' + errorMsg);
            console.error('Error completo:', error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al registrar pedido: ' + error.message);
    }
}
