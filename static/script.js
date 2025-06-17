const mensaje = document.getElementById('mensaje');

function mostrarMensaje(texto, tipo = 'ok') {
  mensaje.textContent = texto;
  mensaje.className = tipo;
}

async function enviarFormulario(formId, endpoint) {
  const form = document.getElementById(formId);
  const formData = new FormData(form);
  const data = {};

  formData.forEach((value, key) => {
    if (!isNaN(value) && value.trim() !== "") {
      data[key] = Number(value);
    } else {
      data[key] = value;
    }
  });

  try {
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    const json = await res.json();

    if (!res.ok) {
      mostrarMensaje(json.error || 'Error desconocido', 'error');
    } else {
      mostrarMensaje(json.mensaje || 'Operación exitosa', 'ok');
      form.reset();
    }
  } catch (error) {
    mostrarMensaje('Error de conexión con el servidor', 'error');
  }
}

document.getElementById('ventaForm').addEventListener('submit', e => {
  e.preventDefault();
  enviarFormulario('ventaForm', '/venta');
});

document.getElementById('compraForm').addEventListener('submit', e => {
  e.preventDefault();
  enviarFormulario('compraForm', '/compra');
});

async function consultarVentas() {
  const res = await fetch('/ventas');
  const ventas = await res.json();
  let html = '<h2>Ventas Registradas</h2><ul>';
  ventas.forEach(v => {
    html += `<li>${v.fecha} - <strong>${v.producto}</strong> (${v.tipo_producto}) - ${v.cantidad} x $${v.precio.toFixed(2)} - Comentario: ${v.comentario || 'N/A'}</li>`;
  });
  html += '</ul>';
  document.getElementById('resultados').innerHTML = html;
}

async function consultarCompras() {
  const res = await fetch('/compras');
  const compras = await res.json();
  let html = '<h2>Compras Registradas</h2><ul>';
  compras.forEach(c => {
    html += `<li>${c.fecha} - <strong>${c.producto}</strong> - ${c.cantidad} ${c.unidad} - $${c.costo_unitario.toFixed(2)} - Proveedor: ${c.proveedor || 'N/A'}</li>`;
  });
  html += '</ul>';
  document.getElementById('resultados').innerHTML = html;
}

async function consultarInventario() {
  const res = await fetch('/inventario');
  const inventario = await res.json();
  let html = '<h2>Inventario Actual</h2><ul>';
  inventario.forEach(i => {
    html += `<li><strong>${i.producto}</strong> - ${i.cantidad} ${i.unidad}</li>`;
  });
  html += '</ul>';
  document.getElementById('resultados').innerHTML = html;
}
