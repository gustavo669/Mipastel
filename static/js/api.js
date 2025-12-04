class MiPastelAPI {
    static BASE_URL = '/api';

    static async obtenerPrecio(sabor, tamano) {
        const response = await fetch(
            `${this.BASE_URL}/obtener-precio?sabor=${encodeURIComponent(sabor)}&tamano=${encodeURIComponent(tamano)}`
        );
        return response.json();
    }

    static async registrarPedidoNormal(datos) {
        const formData = new FormData();
        Object.entries(datos).forEach(([key, value]) => {
            if (value !== null && value !== undefined) {
                formData.append(key, value);
            }
        });

        const response = await fetch('/normales/registrar', {
            method: 'POST',
            body: formData
        });
        return response.json();
    }

    static async registrarPedidoCliente(datos) {
        const formData = new FormData();
        Object.entries(datos).forEach(([key, value]) => {
            if (value !== null && value !== undefined) {
                formData.append(key, value);
            }
        });

        const response = await fetch('/clientes/registrar', {
            method: 'POST',
            body: formData
        });
        return response.json();
    }

    static async cargarPedidosRegistrados(fechaInicio, fechaFin, sucursal = null) {
        let url = `${this.BASE_URL}/pedidos?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`;
        if (sucursal && sucursal !== 'Todas') {
            url += `&sucursal=${encodeURIComponent(sucursal)}`;
        }
        const response = await fetch(url);
        return response.json();
    }

    static async eliminarPedido(tipo, id) {
        const endpoint = tipo === 'normal' ? '/admin/normales' : '/admin/clientes';
        const response = await fetch(`${endpoint}/${id}`, {
            method: 'DELETE'
        });
        return response.json();
    }

    static async actualizarPedido(tipo, id, datos) {
        const endpoint = tipo === 'normal' ? '/admin/normales' : '/admin/clientes';
        const formData = new FormData();
        Object.entries(datos).forEach(([key, value]) => {
            if (value !== null && value !== undefined) {
                formData.append(key, value);
            }
        });

        const response = await fetch(`${endpoint}/${id}`, {
            method: 'PUT',
            body: formData
        });
        return response.json();
    }
}
