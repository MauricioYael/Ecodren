let carrito = JSON.parse(localStorage.getItem('ecodren_cart')) || [];

window.guardarYActualizarCarrito = function () {
    localStorage.setItem('ecodren_cart', JSON.stringify(carrito));
    if (typeof window.renderCartGlobal === 'function') {
        window.renderCartGlobal();
    }
};

window.agregarAlCarrito = function (id, nombre, precio, imagen) {
    const precioLimpio = String(precio).replace(/[^0-9.-]+/g, "");
    const precioNum = parseFloat(precioLimpio) || 0;
    const itemId = String(id);

    carrito = JSON.parse(localStorage.getItem('ecodren_cart')) || [];
    const itemExistente = carrito.find(item => String(item.id) === itemId);

    if (itemExistente) {
        const cantActual = parseInt(itemExistente.qty || itemExistente.cantidad || 1, 10);
        itemExistente.qty = cantActual + 1;
        itemExistente.cantidad = itemExistente.qty;
    } else {
        carrito.push({
            id: itemId,
            nombre: nombre,
            precio: precioNum,
            imagen: imagen || '',
            qty: 1,
            cantidad: 1
        });
    }

    localStorage.setItem('ecodren_cart', JSON.stringify(carrito));
    
    if (typeof window.renderCartGlobal === 'function') {
        window.renderCartGlobal();
    }
    if (typeof window.showToast === 'function') {
        window.showToast(`¡${nombre} agregado al carrito!`, 'success');
    }
};

window.eliminarDelCarrito = function (id) {
    if (typeof window.removeGlobalItem === 'function') {
        window.removeGlobalItem(id);
    }
};

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
        const defaultImg = '/static/Assets/catalogo/boquillas/btp-3.webp';
        imgContainer.innerHTML = `<img src="${imagenUrl || defaultImg}" alt="${nombre}">`;
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
    } else {
        urlParams.delete('sort');
    }

    const priceRange = document.getElementById('priceRange');
    if (priceRange) {
        const valorPrecio = parseInt(priceRange.value, 10);
        if (valorPrecio < 20000) {
            urlParams.set('precio_max', valorPrecio);
        } else {
            urlParams.delete('precio_max');
        }
    }

    window.location.search = urlParams.toString();
};

window.abrirCarrito = function () {
    if (typeof window.renderCartGlobal === 'function') {
        window.renderCartGlobal();
    }
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

document.addEventListener('DOMContentLoaded', function () {
    if (typeof window.renderCartGlobal === 'function') {
        window.renderCartGlobal();
    }

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
        filterStock.addEventListener('change', window.aplicarFiltros);
    }

    const priceRange = document.getElementById('priceRange');
    const priceLabel = document.getElementById('priceLabel');

    if (priceRange && priceLabel) {
        const urlParams = new URLSearchParams(window.location.search);
        const precioGuardado = urlParams.get('precio_max');
        
        if (precioGuardado) {
            priceRange.value = precioGuardado;
            priceLabel.textContent = `$${parseInt(precioGuardado, 10).toLocaleString('es-MX')}`;
        }

        priceRange.addEventListener('input', function () {
            priceLabel.textContent = `$${parseInt(this.value, 10).toLocaleString('es-MX')}`;
        });

        priceRange.addEventListener('change', window.aplicarFiltros);
    }

    const filterToggleBtn = document.getElementById('filterToggleBtn');
    const tiendaSidebar = document.getElementById('tiendaSidebar');
    if (filterToggleBtn && tiendaSidebar) {
        filterToggleBtn.addEventListener('click', function () {
            tiendaSidebar.classList.add('sidebar-open');
        });
    }

    const viewGrid = document.getElementById('viewGrid');
    const viewList = document.getElementById('viewList');
    const shopGrid = document.getElementById('shopGrid');

    function setViewMode(mode) {
        if (!shopGrid) return;
        if (mode === 'list') {
            shopGrid.classList.add('list-view');
            viewList?.classList.add('active');
            viewGrid?.classList.remove('active');
            localStorage.setItem('ecodren_view_mode', 'list');
        } else {
            shopGrid.classList.remove('list-view');
            viewGrid?.classList.add('active');
            viewList?.classList.remove('active');
            localStorage.setItem('ecodren_view_mode', 'grid');
        }
    }

    const savedMode = localStorage.getItem('ecodren_view_mode') || 'grid';
    setViewMode(savedMode);

    viewGrid?.addEventListener('click', () => setViewMode('grid'));
    viewList?.addEventListener('click', () => setViewMode('list'));

    document.addEventListener('click', function (e) {
        const btnAdd = e.target.closest('.btn-add-cart');
        if (btnAdd) {
            e.preventDefault();
            e.stopPropagation();
            const d = btnAdd.dataset;
            window.agregarAlCarrito(d.id, d.nombre, d.precio, d.img);
            return;
        }

        const card = e.target.closest('.product-card');
        if (!card) return;

        if (e.target.closest('.product-card-img') || e.target.closest('.product-title')) {
            const imgContainer = card.querySelector('.product-card-img');
            if (!imgContainer) return;
            const d = imgContainer.dataset;
            window.abrirModalDetalle(d.id, d.nombre, d.cat, d.precio, d.stock, d.desc, d.img, d.sku, d.specs);
        }
    });
});