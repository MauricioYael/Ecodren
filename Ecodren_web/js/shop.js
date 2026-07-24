(() => {
    const shopProducts = [
      { 
        id: 'btp-3', 
        nombre: 'Boquilla Modelo BTP-3', 
        cat: 'boquillas', 
        precio: 850, 
        imagen: '../Assets/catalogo/boquillas/btp-3.webp', 
        badge: 'popular', 
        bg: '#e8f5ed', 
        desc: 'Diseñada para romper y penetrar obstrucciones como rocas, raíces y sedimentos endurecidos.',
        specs: [
          { label: 'Material', value: 'Acero Inoxidable Endurecido' },
          { label: 'Tamaño', value: '3/4"' },
          { label: 'Numero de boquillas', value: '3 laterales y 6 traseras' },
          { label: 'Angulos de boquillas', value: '20° lateral, 30° trasera' },
          { label: 'Peso', value:'4.5kg'},
          { label: 'Presion de trabajo', value:'200 bar'},
          { label: 'Flujo', value:'75 GPM'}
        ]
      },
      { 
        id: 'btp-4', 
        nombre: 'Boquilla Modelo BTP-4', 
        cat: 'boquillas', 
        precio: 3200, 
        imagen: '../Assets/catalogo/boquillas/btp-4.webp', 
        badge: 'nuevo', 
        bg: '#fff3e8', 
        desc: 'Diseñada para romper y penetrar obstrucciones difíciles como rocas, sedimentos endurecidos de mayor tamaño.',
        specs: [
          { label: 'Material', value: 'Acero inoxidable endurecido' },
          { label: 'Tamaño', value: '1"' },
          { label: 'Número de boquillas', value: '4 laterales y 6 traseras' },
          { label: 'Ángulo de boquillas', value: '20° lateral, 30° trasera' },
          { label: 'Peso', value: '4.5Kg' },
          { label: 'Presión de trabajo', value: '200 bar' },
          { label: 'Flujo', value: '75 GPM' }
        ]
      },
      { 
        id: 'bsn-15', 
        nombre: 'Boquilla Modelo BSN-15', 
        cat: 'boquillas', 
        precio: 12500, 
        imagen: '../Assets/catalogo/boquillas/bsn-15.webp', 
        badge: '', 
        bg: '#e8eef8', 
        desc: 'Elimina obstrucciones persistentes y rompe sedimentos como cal, arena y lodo en zonas pequeñas.',
        specs: [
          { label: 'Material', value: 'Acero inoxidable endurecido o cerámico' },
          { label: 'Tamaño', value: '1"' },
          { label: 'Número de boquillas', value: '1 Frontal y 8 traseras' },
          { label: 'Ángulo de boquillas', value: '0° frontal, 20° trasera' },
          { label: 'Peso', value: '1.5Kg' },
          { label: 'Presión de trabajo', value: '200 bar' },
          { label: 'Flujo', value: '45 GPM' }
        ]
      },
      { 
        id: 'bsn-1530', 
        nombre: 'Boquilla Modelo BSN-1530', 
        cat: 'boquillas', 
        precio: 2100, 
        imagen: '../Assets/catalogo/boquillas/bsn-1530.webp', 
        badge: '', 
        bg: '#f0e8f8', 
        desc: 'Eliminación de obstrucciones persistentes en zonas más grandes con sedimentos como cal, arena y piedras.',
        specs: [
          { label: 'Material', value: 'Acero inoxidable endurecido o cerámico' },
          { label: 'Tamaño', value: '1"' },
          { label: 'Número de boquillas', value: '1 Frontal y 10 traseras' },
          { label: 'Ángulo de boquillas', value: '0° frontal, 20° y 25° trasera' },
          { label: 'Peso', value: '5Kg' },
          { label: 'Presión de trabajo', value: '200 bar' },
          { label: 'Flujo', value: '70 GPM' }
        ]
      },
      { 
        id: 'bpl-6', 
        nombre: 'Boquilla Modelo BPL-6', 
        cat: 'boquillas', 
        precio: 420, 
        imagen: '../Assets/catalogo/boquillas/bpl-6.webp', 
        badge: 'oferta', 
        bg: '#fef5e8', 
        desc: 'Ideal para desincrustar aquellos depósitos con dureza media en tuberías de plástico, acero o concreto.',
        specs: [
          { label: 'Material', value: 'Acero inoxidable endurecido' },
          { label: 'Tamaño', value: '3/4"' },
          { label: 'Número de boquillas', value: '2 laterales y 6 traseras' },
          { label: 'Ángulo de boquillas', value: '10° lateral, 30° trasera' },
          { label: 'Peso', value: '2.6Kg' },
          { label: 'Presión de trabajo', value: '137 bar' },
          { label: 'Flujo', value: '55 GPM' }
        ]
      },
      { 
        id: 'bpl-8', 
        nombre: 'Boquilla Modelo BPL-8', 
        cat: 'boquillas', 
        precio: 1350, 
        imagen: '../Assets/catalogo/boquillas/bpl-8.webp', 
        badge: 'nuevo', 
        bg: '#e8f5f8', 
        desc: 'Ayuda principalmente para aquellos depósitos de dureza media en tuberías de plástico, acero o concreto.',
        specs: [
          { label: 'Material', value: 'Acero inoxidable endurecido' },
          { label: 'Tamaño', value: '1"' },
          { label: 'Número de boquillas', value: '2 laterales y 6 traseras' },
          { label: 'Ángulo de boquillas', value: '5° lateral, 25° trasera' },
          { label: 'Peso', value: '6.4Kg' },
          { label: 'Presión de trabajo', value: '137 bar' },
          { label: 'Flujo', value: '70 GPM (1")' }
        ]
      },
      { 
        id: 'bpgp-3.4', 
        nombre: 'Boquilla Modelo BPGP-3.4', 
        cat: 'boquillas', 
        precio: 1890, 
        imagen: '../Assets/catalogo/boquillas/bpgp-3.4.webp', 
        badge: '', 
        bg: '#f5e8e8', 
        desc: 'Eliminado de grasa, barro, raíces y otras obstrucciones para tuberías de alcantarillado.',
        specs: [
          { label: 'Material', value: 'Acero inoxidable endurecido' },
          { label: 'Tamaño', value: '3/4"' },
          { label: 'Número de boquillas', value: '4 laterales y 6 traseras' },
          { label: 'Ángulo de boquillas', value: '90° lateral, 20° trasera' },
          { label: 'Peso', value: '1Kg' },
          { label: 'Presión de trabajo', value: '137 bar' },
          { label: 'Flujo', value: '45 GPM' }
        ]
      },
      { 
        id: 'bpgp-1', 
        nombre: 'Boquilla Modelo BPGP-1', 
        cat: 'boquillas', 
        precio: 680, 
        imagen: '../Assets/catalogo/boquillas/bpgp-1.webp', 
        badge: '', 
        bg: '#e8f0e8', 
        desc: 'Ideal para limpiar tuberías de alcantarillado, eliminando grasa, barro, raíces y otras obstrucciones.',
        specs: [
          { label: 'Material', value: 'Acero inoxidable endurecido' },
          { label: 'Tamaño', value: '1"' },
          { label: 'Número de boquillas', value: '4 laterales y 6 traseras' },
          { label: 'Ángulo de boquillas', value: '90° lateral, 25° trasera' },
          { label: 'Peso', value: '5Kg' },
          { label: 'Presión de trabajo', value: '170 bar' },
          { label: 'Flujo', value: '71 GPM' }
        ]
      },
      { 
        id: 'bpg-3.4', 
        nombre: 'Boquilla Modelo BPG-3.4', 
        cat: 'boquillas', 
        precio: 1500, 
        imagen: '../Assets/catalogo/boquillas/bpg-3.4.webp', 
        badge: '', 
        bg: '#e8f5f8', 
        desc: 'Para trabajos de menor diámetro, eliminando grasa, barro y raíces.',
        specs: [
          { label: 'Material', value: 'Acero inoxidable endurecido o cerámico' },
          { label: 'Tamaño', value: '1"' },
          { label: 'Número de boquillas', value: '1 Frontal y 8 traseras' },
          { label: 'Ángulo de boquillas', value: '0° frontal, 20° trasera' },
          { label: 'Peso', value: '1.5Kg' },
          { label: 'Presión de trabajo', value: '200 bar' },
          { label: 'Flujo', value: '45 GPM' }
        ]
      },
      { 
        id: 'bpg-1', 
        nombre: 'Boquilla Modelo BPG-1', 
        cat: 'boquillas', 
        precio: 870, 
        imagen: '../Assets/catalogo/boquillas/bpg-1.webp', 
        badge: '', 
        bg: '#fef5e8', 
        desc: 'Adecuada para limpiar todo tipo de tuberías de alcantarillado y agua de lluvia, elimina grasa, barro y otros sedimentos.',
        specs: [
          { label: 'Material', value: 'Acero inoxidable endurecido' },
          { label: 'Tamaño', value: '1"' },
          { label: 'Número de boquillas', value: '4 laterales y6 traseras' },
          { label: 'Ángulo de boquillas', value: '90° lateral, 25° trasera' },
          { label: 'Peso', value: '5Kg' },
          { label: 'Presión de trabajo', value: '170 bar' },
          { label: 'Flujo', value: '71 GPM' }
        ]
      },
      { 
        id: 'btor-15', 
        nombre: 'Boquilla Modelo BTOR-15', 
        cat: 'boquillas', 
        precio: 350, 
        imagen: '../Assets/catalogo/boquillas/btor-15.webp', 
        badge: '', 
        bg: '#f0e8f8', 
        desc: 'Diseñada para eliminar residuos pesados y compactados como arena y ladrillos en tuberías de gran tamaño y fondo plano.',
        specs: [
          { label: 'Material', value: 'Acero inoxidable endurecido, acero endurecido resistente al desgaste' },
          { label: 'Tamaño', value: '1"' },
          { label: 'Número de boquillas', value: '13 boquillas en diferentes angulos' },
          { label: 'Ángulo de boquillas', value: '0°, 8°, 13°, 15°, 18°' },
          { label: 'Peso', value: '25Kg y 15KG disponibles' },
          { label: 'Presión de trabajo', value: '200 bar' },
          { label: 'Flujo', value: '70 GPM' }
        ]
      },
      { 
        id: 'bter-1', 
        nombre: 'Boquilla Modelo BTER-1', 
        cat: 'boquillas', 
        precio: 2850, 
        imagen: '../Assets/catalogo/boquillas/bter-1.webp', 
        badge: '', 
        bg: '#f0e8f8', 
        desc: 'Especializada en la eliminación de obstrucciones complejas en alcantarillado y drenajes.',
        specs: [
          { label: 'Material', value: 'Acero inoxidable endurecido' },
          { label: 'Tamaño', value: '1"' },
          { label: 'Número de boquillas', value: '4 laterales y 10 traseras' },
          { label: 'Ángulo de boquillas', value: '20° lateral, 15° trasera' },
          { label: 'Peso', value: '23Kg' },
          { label: 'Presión de trabajo', value: '137 bar' },
          { label: 'Flujo', value: '70 GPM' }
        ]
      }
    ];

    let cart = JSON.parse(localStorage.getItem('ecodren_cart')) || [];
    let wishlist = JSON.parse(localStorage.getItem('ecodren_wishlist')) || [];
    let shopFilter = 'todos';
    let shopSearch = '';
    let modalQty = 1;

    function saveCart() {
        localStorage.setItem('ecodren_cart', JSON.stringify(cart));
    }

    function updateCartCount() {
        const countEls = document.querySelectorAll('.cart-count');
        const totalItems = cart.reduce((sum, item) => sum + (item.qty || 1), 0);
        countEls.forEach(el => {
            el.textContent = totalItems;
            el.classList.toggle('has-items', totalItems > 0);
        });
    }

    window.addToCart = function(e, id, nombre, precio, imagen, qty = 1) {
        if (e) {
            e.preventDefault();
            e.stopPropagation(); 
        }
        const existing = cart.find(item => item.id === id);
        if (existing) {
            existing.qty = (existing.qty || 1) + qty;
        } else {
            cart.push({ id, nombre, precio, imagen, qty });
        }
        saveCart();
        updateCartCount();
        if (typeof renderCartGlobal === 'function') renderCartGlobal();
        if (typeof renderCart === 'function') renderCart();
        if (typeof showToast === 'function') showToast(`🛍️ "${nombre}" agregado al carrito.`, 'success');
    };

    window.removeFromCart = function(id) {
        cart = cart.filter(item => item.id !== id);
        saveCart();
        updateCartCount();
        if (typeof renderCart === 'function') renderCart();
        if (typeof renderCartGlobal === 'function') renderCartGlobal();
    };

    window.changeQty = function(id, delta) {
        const item = cart.find(i => i.id === id);
        if (!item) return;
        item.qty = (item.qty || 1) + delta;
        if (item.qty < 1) window.removeFromCart(id);
        else {
            saveCart();
            updateCartCount();
            if (typeof renderCart === 'function') renderCart();
            if (typeof renderCartGlobal === 'function') renderCartGlobal();
        }
    };

    window.renderCart = function() {
        const itemsEl = document.getElementById('cartItems');
        const footerEl = document.getElementById('cartFooter');
        const totalEl = document.getElementById('cartTotal');
        if (!itemsEl) return;
        if (cart.length === 0) {
            itemsEl.innerHTML = `<div class="cart-empty"><span class="cart-empty-icon">🛒</span><p style="font-weight:600;margin-bottom:.5rem">Tu carrito está vacío</p><p style="font-size:.85rem;color:var(--eco-gray)">Agrega productos desde la tienda</p></div>`;
            if (footerEl) footerEl.style.display = 'none';
            return;
        }
        let html = '', total = 0;
        cart.forEach(item => {
            const itemTotal = item.precio * (item.qty || 1);
            total += itemTotal;
            html += `
            <div class="cart-item">
                <div class="cart-item-img" style="display:flex; align-items:center; justify-content:center; background:#f8fafc; border-radius:8px; overflow:hidden;">
                    <img src="${item.imagen || item.img || 'Assets/placeholder.png'}" alt="${item.nombre}" style="width:100%; height:100%; object-fit:contain; padding:4px;">
                </div>
                <div class="cart-item-info">
                    <h4>${item.nombre}</h4>
                    <span>$${item.precio.toLocaleString('es-MX')} c/u</span>
                    <div class="cart-item-controls">
                        <button class="qty-btn" onclick="changeQty('${item.id}', -1)">−</button>
                        <span class="qty-num">${item.qty || 1}</span>
                        <button class="qty-btn" onclick="changeQty('${item.id}', 1)">+</button>
                        <button class="remove-item" onclick="removeFromCart('${item.id}')">🗑</button>
                    </div>
                </div>
            </div>`;
        });
        itemsEl.innerHTML = html;
        if (totalEl) totalEl.textContent = '$' + total.toLocaleString('es-MX');
        if (footerEl) footerEl.style.display = 'block';
    };

    window.openCart = function() {
        const sidebar = document.getElementById('cartSidebar');
        const overlay = document.getElementById('cartOverlay');
        if (sidebar && overlay) {
            sidebar.classList.add('open');
            overlay.classList.add('open');
            window.renderCart();
        }
    };

    window.closeCart = function() {
        const sidebar = document.getElementById('cartSidebar');
        const overlay = document.getElementById('cartOverlay');
        if (sidebar) sidebar.classList.remove('open');
        if (overlay) overlay.classList.remove('open');
    };

    window.toggleWishlist = function(productId, productName) {
        const index = wishlist.indexOf(productId);
        const heartIcon = document.getElementById(`heart-icon-${productId}`);
        if (index > -1) {
            wishlist.splice(index, 1);
            if (heartIcon) {
                heartIcon.className = 'fa-regular fa-heart shop-wishlist-heart';
                heartIcon.classList.remove('in-wishlist');
            }
            if (typeof showToast === 'function') showToast(`"${productName}" removido de favoritos`, 'info');
        } else {
            wishlist.push(productId);
            if (heartIcon) {
                heartIcon.className = 'fa-solid fa-heart shop-wishlist-heart in-wishlist';
            }
            if (typeof showToast === 'function') showToast(`"${productName}" guardado en favoritos`, 'success');
        }
        localStorage.setItem('ecodren_wishlist', JSON.stringify(wishlist));
    };

    window.openProductModal = function(id) {
        const p = shopProducts.find(x => x.id === id);
        if (!p) return;
        
        modalQty = 1;
        if(document.getElementById('modalCat')) document.getElementById('modalCat').textContent = p.cat;
        if(document.getElementById('modalName')) document.getElementById('modalName').textContent = p.nombre;
        if(document.getElementById('modalDesc')) document.getElementById('modalDesc').textContent = p.desc;
        if(document.getElementById('modalQty')) document.getElementById('modalQty').textContent = 1;
        if(document.getElementById('modalPrice')) document.getElementById('modalPrice').textContent = '$' + p.precio.toLocaleString('es-MX');
        
        const imgWrap = document.getElementById('modalImg');
        if (imgWrap) {
            imgWrap.style.background = p.bg;
            if (p.imagen) {
                imgWrap.innerHTML = `<img src="${p.imagen}" alt="${p.nombre}" style="width:100%; height:100%; object-fit:contain; padding:20px;">`;
            } else {
                imgWrap.innerHTML = `<div class="modal-img-placeholder"><span style="font-size:6rem;">${p.emoji || '📦'}</span></div>`;
            }
        }
        
        const specsEl = document.getElementById('modalSpecs');
        if (specsEl) {
            if (p.specs && p.specs.length > 0) {
                specsEl.style.display = 'grid';
                specsEl.innerHTML = p.specs.map(s => `<div class="spec-row"><strong>${s.label}</strong><span>${s.value}</span></div>`).join('');
            } else {
                specsEl.style.display = 'none';
            }
        }
        
        const addBtn = document.getElementById('modalAddCart');
        if (addBtn) {
            addBtn.onclick = () => { 
                window.addToCart(null, p.id, p.nombre, p.precio, p.imagen || '📦', modalQty); 
                window.closeProductModal(); 
            };
        }
        
        document.getElementById('productModalOverlay')?.classList.add('open');
        document.body.style.overflow = 'hidden';
    };

    window.closeProductModal = function() {
        document.getElementById('productModalOverlay')?.classList.remove('open');
        document.body.style.overflow = '';
    };

    window.changeModalQty = function(d) {
        modalQty = Math.max(1, modalQty + d);
        if(document.getElementById('modalQty')) document.getElementById('modalQty').textContent = modalQty;
    };

    window.renderShop = function() {
        const grid = document.getElementById('shopGrid');
        if (!grid) return;

        const skeletonCount = 4;
        let skeletonHTML = '';
        for (let i = 0; i < skeletonCount; i++) {
            skeletonHTML += `
                <div class="skeleton-card">
                    <div class="skeleton-shimmer"></div>
                    <div class="skeleton-block skeleton-image"></div>
                    <div class="skeleton-block skeleton-tag"></div>
                    <div class="skeleton-block skeleton-title"></div>
                    <div class="skeleton-block skeleton-desc"></div>
                    <div class="skeleton-block skeleton-desc-short"></div>
                    <div class="skeleton-footer">
                        <div class="skeleton-block skeleton-price"></div>
                        <div class="skeleton-block skeleton-btn"></div>
                    </div>
                </div>`;
        }
        grid.innerHTML = skeletonHTML;

        setTimeout(() => {
            const filtered = shopProducts.filter(p =>
                (shopFilter === 'todos' || p.cat === shopFilter) &&
                (p.nombre.toLowerCase().includes(shopSearch.toLowerCase()) || 
                p.desc.toLowerCase().includes(shopSearch.toLowerCase()))
            );

            if (filtered.length === 0) {
                grid.innerHTML = '<p style="color:var(--eco-gray);grid-column:1/-1;padding:2rem 0;text-align:center">No se encontraron productos con ese filtro.</p>';
                return;
            }

            grid.innerHTML = filtered.map(p => {
                const isFav = wishlist.includes(p.id);
                const heartClass = isFav ? 'fa-solid fa-heart in-wishlist' : 'fa-regular fa-heart';

                return `
                <div class="shop-card reveal visible" onclick="window.openProductModal('${p.id}')" style="animation: successPanelIn 0.3s ease forwards; cursor:pointer;">
                    <div class="shop-img" style="background:${p.bg}">
                        <button class="btn-wishlist-toggle-action" onclick="event.stopPropagation(); toggleWishlist('${p.id}', '${p.nombre}')" title="Añadir a lista de deseos">
                            <i class="${heartClass} shop-wishlist-heart" id="heart-icon-${p.id}"></i>
                        </button>
                        ${p.imagen ? 
                            `<img src="${p.imagen}" alt="${p.nombre}" style="width:100%; height:100%; object-fit:contain; padding:15px;">` : 
                            `<span style="font-size:3rem">${p.emoji || '📦'}</span>`
                        }
                        <span style="font-size:0.72rem; color:rgba(10,26,15,0.35); position:absolute; bottom:8px;">★ Ecodren Premium</span>
                        ${p.badge ? `<span class="shop-badge badge-${p.badge}">${p.badge}</span>` : ''}
                    </div>
                    <div class="shop-info">
                        <div class="shop-cat-tag">${p.cat}</div>
                        <h3>${p.nombre}</h3>
                        <p>${p.desc}</p>
                        <div class="shop-footer">
                            <div class="shop-price">$${p.precio.toLocaleString('es-MX')}</div>
                            <button class="add-cart-btn" onclick="addToCart(event, '${p.id}','${p.nombre}',${p.precio},'${p.imagen}')">
                                <span class="cart-icon">🛒</span> Agregar
                            </button>
                        </div>
                    </div>
                </div>`;
            }).join('');
        }, 800);
    };

    document.addEventListener('DOMContentLoaded', () => {
        document.getElementById('productModalClose')?.addEventListener('click', window.closeProductModal);
        document.getElementById('productModalOverlay')?.addEventListener('click', e => { 
            if (e.target.id === 'productModalOverlay') window.closeProductModal(); 
        });

        const cartBtn = document.getElementById('cartNavBtn');
        const closeBtn = document.getElementById('cartClose');
        const overlay = document.getElementById('cartOverlay');

        if (cartBtn) cartBtn.addEventListener('click', () => { if(typeof renderCartGlobal === 'function') { renderCartGlobal(); } document.getElementById('cartSidebar')?.classList.add('active','open'); document.getElementById('cartOverlay')?.classList.add('active','open'); });
        if (closeBtn) closeBtn.addEventListener('click', () => { document.getElementById('cartSidebar')?.classList.remove('active','open'); document.getElementById('cartOverlay')?.classList.remove('active','open'); });
        if (overlay) overlay.addEventListener('click', () => { document.getElementById('cartSidebar')?.classList.remove('active','open'); document.getElementById('cartOverlay')?.classList.remove('active','open'); });

        updateCartCount();
        window.renderShop();
        
        const tabs = document.getElementById('catFilters');
        if (tabs) {
            tabs.addEventListener('click', e => {
                const btn = e.target.closest('.filter-check');
                if (!btn) return;
                
                document.querySelectorAll('#catFilters .filter-check').forEach(b => b.classList.remove('active-check'));
                btn.classList.add('active-check');
                
                // Forzamos la lectura del input radio interno para evitar desajustes de datos
                const radio = btn.querySelector('input[type="radio"]');
                if (radio) radio.checked = true;
                
                shopFilter = btn.getAttribute('data-filter') || btn.getAttribute('data-value') || 'todos';
                window.renderShop();
            });
        }
        
        document.body.addEventListener('contextmenu', (e) => {
            if (e.target.closest('.shop-img') || e.target.closest('.product-modal-img') || e.target.tagName === 'IMG') {
                e.preventDefault();
                if (typeof showToast === 'function') {
                    showToast('🔒 Contenido protegido por la propiedad intelectual de Ecodren.', 'info');
                }
            }
        });
    });
})();