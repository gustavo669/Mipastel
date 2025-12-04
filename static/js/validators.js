class FormValidator {
    static validarPedidoNormal(datos) {
        const errores = [];

        if (!datos.sabor || datos.sabor.trim() === '') {
            errores.push('Sabor requerido');
        }

        if (!datos.tamano || datos.tamano.trim() === '') {
            errores.push('Tamaño requerido');
        }

        if (!datos.cantidad || datos.cantidad < 1) {
            errores.push('Cantidad debe ser mayor a 0');
        }

        if (!datos.precio || datos.precio <= 0) {
            errores.push('Precio debe ser mayor a 0');
        }

        if (!datos.sucursal || datos.sucursal.trim() === '') {
            errores.push('Sucursal requerida');
        }

        if (!datos.fecha_entrega) {
            errores.push('Fecha de entrega requerida');
        } else {
            const fechaEntrega = new Date(datos.fecha_entrega);
            const hoy = new Date();
            hoy.setHours(0, 0, 0, 0);

            if (fechaEntrega < hoy) {
                errores.push('La fecha de entrega no puede ser anterior a hoy');
            }
        }

        return { valido: errores.length === 0, errores };
    }

    static validarPedidoCliente(datos) {
        const resultado = this.validarPedidoNormal(datos);

        if (datos.dedicatoria && datos.dedicatoria.length > 500) {
            resultado.errores.push('Dedicatoria muy larga (máximo 500 caracteres)');
            resultado.valido = false;
        }

        if (datos.detalles && datos.detalles.length > 500) {
            resultado.errores.push('Detalles muy largos (máximo 500 caracteres)');
            resultado.valido = false;
        }

        return resultado;
    }

    static sanitizarInput(texto) {
        if (!texto) return texto;

        const caracteresProhibidos = ['<', '>', '"', "'", ';', '--', '/*', '*/'];
        let textoLimpio = texto;

        for (const char of caracteresProhibidos) {
            if (textoLimpio.includes(char)) {
                return null;
            }
        }

        return textoLimpio.trim();
    }

    static mostrarErrores(errores, contenedorId = 'errores-validacion') {
        const contenedor = document.getElementById(contenedorId);
        if (!contenedor) return;

        if (errores.length === 0) {
            contenedor.innerHTML = '';
            contenedor.style.display = 'none';
            return;
        }

        const html = `
            <div class="alert alert-danger">
                <strong>Errores de validación:</strong>
                <ul>
                    ${errores.map(error => `<li>${error}</li>`).join('')}
                </ul>
            </div>
        `;

        contenedor.innerHTML = html;
        contenedor.style.display = 'block';
    }
}
