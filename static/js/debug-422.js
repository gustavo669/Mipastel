// Debug script para error 422
// Ejecuta esto en la consola del navegador

async function testRegistro() {
    console.log('=== TEST DE REGISTRO ===');

    const formData = new FormData();

    // Datos de prueba
    const datos = {
        sabor: 'Fresas',
        tamano: 'Mediano',
        cantidad: 1,
        sucursal: 'Jutiapa 1',
        fecha_entrega: '2025-12-25',
        precio: 125.00,
        detalles: '',
        sabor_personalizado: '',
        es_otro: false
    };

    // Log de qué se va a enviar
    console.log('Datos a enviar:', datos);
    console.log('FormData entries:');

    for (const [key, value] of Object.entries(datos)) {
        formData.append(key, value);
        console.log(`  ${key}: ${value} (${typeof value})`);
    }

    // Enviar request
    console.log('\nEnviando POST a /normales/registrar...');

    try {
        const resp = await fetch('/normales/registrar', {
            method: 'POST',
            body: formData
        });

        console.log('\n=== RESPUESTA ===');
        console.log('Status:', resp.status, resp.statusText);
        console.log('Headers:', {
            'Content-Type': resp.headers.get('Content-Type'),
            'Content-Length': resp.headers.get('Content-Length')
        });

        const texto = await resp.text();
        console.log('Response text:', texto);

        // Intentar parsear como JSON si es posible
        try {
            const json = JSON.parse(texto);
            console.log('Response JSON:', json);
            if (json.detail) {
                console.error('ERROR DETAIL:', json.detail);
            }
        } catch (e) {
            console.log('(No es JSON válido)');
        }

    } catch (error) {
        console.error('ERROR en fetch:', error);
    }
}

// Ejecuta en la consola:
// testRegistro()
console.log('Script de debug cargado. Ejecuta: testRegistro()');