/**
 * ECODREN - Control de Tienda, Filtros, Modales y Carrito
 */

// 1. ESTADO Y GESTIÓN DEL CARRITO
let carrito = JSON.parse(localStorage.getItem('ecodren_cart')) || [];

window.guardarYActualizarCarrito = function () {
    localStorage.setItem('ecodren_cart', JSON.stringify(carrito));

    const cartCountEl = document.getElementById('cartCount');
    const cartItemsContainer = document.getElementById('cartItems');
    const cartFooter = document.getElementById('cartFooter');
    const cartTotalEl = document.getElementById('cartTotal');

    const totalCount = carrito.reduce((acc, item) => acc + item.cantidad, 0);
    if (cartCountEl) {
        cartCountEl.textContent = totalCount;
        cartCountEl.setAttribute('data-count', totalCount);
    }
    if (totalCount > 0){
        cartCountEl.style.display = 'flex';
        cartCountEl.style.transform = 'scale(1.3)';
        setTimeout(() => {
            cartCountEl.style.transform = 'scale(1)';
        }, 200); 
    } else {
        cartCountEl.style.display ='none';
    }

    if (!cartItemsContainer) return;

    if (carrito.length === 0) {
        cartItemsContainer.innerHTML = `
            <div class="cart-empty" style="text-align:center; padding: 2rem 1rem;">
                <span class="cart-empty-icon" style="font-size:2.5rem; display:block; margin-bottom:.5rem;">🛒</span>
                <p style="font-weight:600; margin-bottom:.25rem; color:#0a1a0f;">Tu carrito está vacío</p>
                <p style="font-size:.85rem; color:#6b7280;">Agrega productos desde la tienda</p>
            </div>`;
        if (cartFooter) cartFooter.style.display = 'none';
    } else {
        let html = '';
        let total = 0;

        carrito.forEach(item => {
            const subtotal = item.precio * item.cantidad;
            total += subtotal;

            const imgHtml = item.imagen 
                ? `<img src="${item.imagen}" style="width:48px; height:48px; object-fit:contain; border-radius:6px; margin-right:0.8rem; background:#f8fafc; border:1px solid #e2e8f0;">`
                : `<div style="width:48px; height:48px; background:#f1f5f9; display:flex; align-items:center; justify-content:center; border-radius:6px; margin-right:0.8rem; font-size:1.2rem; color:#1a6b3c;">🔩</div>`;

            html += `
                <div class="cart-item-row" style="display:flex; align-items:center; justify-content:space-between; margin-bottom:0.8rem; padding-bottom:0.8rem; border-bottom:1px solid #f1f5f9;">
                    <div style="display:flex; align-items:center; flex:1; min-width:0;">
                        ${imgHtml}
                        <div style="flex:1; min-width:0; padding-right:0.5rem;">
                            <strong style="font-size:0.85rem; display:block; line-height:1.2; margin-bottom:0.2rem; color:#0a1a0f; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${item.nombre}</strong>
                            <span style="font-size:0.78rem; color:#6b7280;">
                                ${item.cantidad} x ${item.precio > 0 ? '$' + item.precio.toLocaleString('es-MX') + ' MXN' : 'Cotización'}
                            </span>
                        </div>
                    </div>
                    <div style="display:flex; align-items:center; gap:0.6rem;">
                        <strong style="font-weight:700; font-size:0.88rem; color:#0a1a0f;">
                            ${item.precio > 0 ? '$' + subtotal.toLocaleString('es-MX') : '-'}
                        </strong>
                        <button onclick="window.eliminarDelCarrito('${item.id}')" style="background:none; border:none; color:#ef4444; font-size:1.2rem; cursor:pointer; padding:0 0.2rem;" title="Eliminar">&times;</button>
                    </div>
                </div>`;
        });

        cartItemsContainer.innerHTML = html;
        if (cartTotalEl) cartTotalEl.textContent = `$${total.toLocaleString('es-MX')} MXN`;
        if (cartFooter) cartFooter.style.display = 'block';
    }
};

window.agregarAlCarrito = function (id, nombre, precio, imagen) {
    const precioLimpio = String(precio).replace(/[^0-9.-]+/g, "");
    const precioNum = parseFloat(precioLimpio) || 0;
    const itemId = String(id);

    const itemExistente = carrito.find(item => item.id === itemId);

    if (itemExistente) {
        itemExistente.cantidad += 1;
    } else {
        carrito.push({
            id: itemId,
            nombre: nombre,
            precio: precioNum,
            imagen: imagen || '',
            cantidad: 1
        });
    }

    window.guardarYActualizarCarrito();
    window.mostrarNotificacion(`¡${nombre} agregado al carrito!`);
};

window.eliminarDelCarrito = function (id) {
    carrito = carrito.filter(item => item.id !== String(id));
    window.guardarYActualizarCarrito();
};

// 2. SISTEMA DE NOTIFICACIONES (TOAST NATIVO)
window.mostrarNotificacion = function(mensaje) {
    let toast = document.getElementById('ecoToast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'ecoToast';
        document.body.appendChild(toast);
    }

    toast.innerHTML = `<i class="fas fa-check-circle"></i> <span>${mensaje}</span>`;
    toast.classList.add('show');

    setTimeout(() => {
        toast.classList.remove('show');
    }, 2500);
};

// 3. MODAL DE DETALLE DEL PRODUCTO (RECIBE 9 PARÁMETROS EN ORDEN EXACTO)
window.abrirModalDetalle = function (id, nombre, categoria, precio, stock, descripcion, imagenUrl, sku, especificaciones) {
    const modalName = document.getElementById('modalName');
    const modalCat = document.getElementById('modalCat');
    const modalDesc = document.getElementById('modalDesc');
    const modalPrice = document.getElementById('modalPrice');
    const modalStock = document.getElementById('modalStock');
    const modalSpecs = document.getElementById('modalSpecs');
    const imgContainer = document.getElementById('modalImg');
    const btnAddModal = document.getElementById('modalAddCart');
    const modalOverlay = document.getElementById('productModalOverlay');
    const modalQty = document.getElementById('modalQty');

    if (modalQty) modalQty.textContent = '1';
    if (modalName) modalName.textContent = nombre;
    if (modalCat) modalCat.textContent = categoria;
    if (modalDesc) modalDesc.textContent = descripcion || 'Refacción original Ecodren de alto desempeño para sistemas de desazolve industrial.';
    
    // Inyección de Especificaciones Reales
    if (modalSpecs) {
        let specsHtml = '';
        if (sku) {
            specsHtml += `<div class="spec-row"><strong>SKU / Código:</strong> <span>${sku}</span></div>`;
        }
        if (especificaciones && especificaciones.trim() !== '') {
            specsHtml += `<div class="spec-row"><strong>Especificaciones técnicas:</strong> <p>${especificaciones}</p></div>`;
        } else {
            specsHtml += `<div class="spec-row"><strong>Garantía:</strong> <span>Cobertura directa de fábrica Ecodren México</span></div>`;
        }
        modalSpecs.innerHTML = specsHtml;
    }

    const precioLimpio = String(precio).replace(/[^0-9.-]+/g, "");
    const precioNum = parseFloat(precioLimpio) || 0;
    if (modalPrice) modalPrice.textContent = precioNum > 0 ? `$${precioNum.toLocaleString('es-MX')} MXN` : 'Cotizar precio';

    const stockNum = parseInt(stock) || 0;
    if (modalStock) {
        modalStock.textContent = stockNum > 0 ? `En stock (${stockNum} disponibles)` : 'Agotado';
        modalStock.className = `modal-stock-badge ${stockNum > 0 ? 'in-stock' : 'out-stock'}`;
    }

    if (imgContainer) {
        if (imagenUrl && imagenUrl !== '') {
            imgContainer.innerHTML = `<img src="${imagenUrl}" alt="${nombre}">`;
        } else {
            imgContainer.innerHTML = `
                <div class="product-card-placeholder">
                    <i class="fas fa-gears"></i>
                    <span>${sku || 'ECODREN'}</span>
                </div>`;
        }
    }

    if (btnAddModal) {
        btnAddModal.onclick = function () {
            const qty = parseInt(document.getElementById('modalQty')?.textContent) || 1;
            for (let i = 0; i < qty; i++) {
                window.agregarAlCarrito(id, nombre, precio, imagenUrl);
            }
            window.cerrarModalDetalle();
        };
    }

    if (modalOverlay) {
        modalOverlay.classList.add('open');
    }
};

window.cerrarModalDetalle = function () {
    const modalOverlay = document.getElementById('productModalOverlay');
    if (modalOverlay) {
        modalOverlay.classList.remove('open');
    }
};

window.changeModalQty = function (delta) {
    const qtyEl = document.getElementById('modalQty');
    if (!qtyEl) return;
    let val = parseInt(qtyEl.textContent) || 1;
    val += delta;
    if (val < 1) val = 1;
    qtyEl.textContent = val;
};

// 4. FILTROS Y BÚSQUEDA DINÁMICA
window.aplicarFiltros = function () {
    const urlParams = new URLSearchParams(window.location.search);
    
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        const query = searchInput.value.trim();
        if (query) {
            urlParams.set('q', query);
        } else {
            urlParams.delete('q');
        }
    }

    const filterStock = document.getElementById('filterStock');
    if (filterStock) {
        if (filterStock.checked) {
            urlParams.set('stock', '1');
        } else {
            urlParams.delete('stock');
        }
    }

    const sortSelect = document.getElementById('sortSelect');
    if (sortSelect && sortSelect.value !== 'default') {
        urlParams.set('sort', sortSelect.value);
    }

    window.location.search = urlParams.toString();
};

// 5. CONTROLADORES UI (SIDEBARS Y EVENTOS)
window.abrirCarrito = function () {
    window.guardarYActualizarCarrito();
    const cartSidebar = document.getElementById('cartSidebar');
    const cartOverlay = document.getElementById('cartOverlay');
    if (cartSidebar) cartSidebar.classList.add('open');
    if (cartOverlay) cartOverlay.classList.add('open');
};

window.cerrarCarrito = function () {
    const cartSidebar = document.getElementById('cartSidebar');
    const cartOverlay = document.getElementById('cartOverlay');
    if (cartSidebar) cartSidebar.classList.remove('open');
    if (cartOverlay) cartOverlay.classList.remove('open');
};

// Inicialización
document.addEventListener('DOMContentLoaded', function () {
    window.guardarYActualizarCarrito();

    const cartNavBtn = document.getElementById('cartNavBtn');
    const cartClose = document.getElementById('cartClose');
    const cartOverlay = document.getElementById('cartOverlay');

    if (cartNavBtn) cartNavBtn.addEventListener('click', window.abrirCarrito);
    if (cartClose) cartClose.addEventListener('click', window.cerrarCarrito);
    if (cartOverlay) cartOverlay.addEventListener('click', window.cerrarCarrito);

    const productModalClose = document.getElementById('productModalClose');
    const productModalOverlay = document.getElementById('productModalOverlay');

    if (productModalClose) productModalClose.addEventListener('click', window.cerrarModalDetalle);
    if (productModalOverlay) {
        productModalOverlay.addEventListener('click', function (e) {
            if (e.target === productModalOverlay) window.cerrarModalDetalle();
        });
    }

    const applyFiltersBtn = document.getElementById('applyFiltersBtn');
    const searchInput = document.getElementById('searchInput');
    const sortSelect = document.getElementById('sortSelect');

    if (applyFiltersBtn) applyFiltersBtn.addEventListener('click', window.aplicarFiltros);

    if (searchInput) {
        searchInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                window.aplicarFiltros();
            }
        });
    }

    if (sortSelect) {
        const urlParams = new URLSearchParams(window.location.search);
        const sortParam = urlParams.get('sort');
        if (sortParam) sortSelect.value = sortParam;

        sortSelect.addEventListener('change', window.aplicarFiltros);
    }

    const filterStock = document.getElementById('filterStock');
    if (filterStock) {
        const urlParams = new URLSearchParams(window.location.search);
        filterStock.checked = urlParams.get('stock') === '1';
    }

    const filterToggleBtn = document.getElementById('filterToggleBtn');
    const tiendaSidebar = document.getElementById('tiendaSidebar');
    if (filterToggleBtn && tiendaSidebar) {
        filterToggleBtn.addEventListener('click', function () {
            tiendaSidebar.classList.add('sidebar-open');
        });
    }
});

document.addEventListener('click', function (e) {
    const card = e.target.closest('.shop-card');
    if (!card) return;

    // Abrir modal si se hace clic en la imagen, título o botón "Ver detalles"
    if (e.target.closest('.shop-img') || e.target.closest('h3') || e.target.closest('.btn-ver-detalle')) {
        const d = card.dataset;
        if (typeof window.abrirModalDetalle === 'function') {
            window.abrirModalDetalle(d.id, d.nombre, d.cat, d.precio, d.stock, d.desc, d.img, d.sku, d.specs);
        }
    }
});