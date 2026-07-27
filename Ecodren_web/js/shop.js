(() => {
    let cart = JSON.parse(localStorage.getItem('ecodren_cart')) || [];
    let wishlist = JSON.parse(localStorage.getItem('ecodren_wishlist')) || [];

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

    // 🛒 Agregar al Carrito desde Django
    window.addToCart = function(e, sku, nombre, precio, imagen, qty = 1) {
        if (e) {
            e.preventDefault();
            e.stopPropagation(); 
        }
        const existing = cart.find(item => item.id === sku);
        if (existing) {
            existing.qty = (existing.qty || 1) + qty;
        } else {
            cart.push({ id: sku, nombre, precio, imagen, qty });
        }
        saveCart();
        updateCartCount();
        if (typeof renderCart === 'function') renderCart();
        if (typeof showToast === 'function') showToast(`🛍️ "${nombre}" agregado al carrito.`, 'success');
    };

    window.removeFromCart = function(id) {
        cart = cart.filter(item => item.id !== id);
        saveCart();
        updateCartCount();
        if (typeof renderCart === 'function') renderCart();
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
        }
    };

    // 🛍️ Drawer del Carrito
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
            <div class="cart-item" style="display:flex; gap:10px; margin-bottom:12px; align-items:center;">
                <div class="cart-item-info" style="flex:1;">
                    <h4 style="font-size:0.85rem; margin:0;">${item.nombre}</h4>
                    <span style="font-size:0.75rem; color:var(--eco-gray);">$${item.precio.toLocaleString('es-MX')} c/u</span>
                    <div class="cart-item-controls" style="display:flex; gap:6px; align-items:center; margin-top:4px;">
                        <button class="qty-btn" onclick="changeQty('${item.id}', -1)">−</button>
                        <span class="qty-num">${item.qty || 1}</span>
                        <button class="qty-btn" onclick="changeQty('${item.id}', 1)">+</button>
                        <button class="remove-item" style="background:none; border:none; cursor:pointer;" onclick="removeFromCart('${item.id}')">🗑</button>
                    </div>
                </div>
            </div>`;
        });
        itemsEl.innerHTML = html;
        if (totalEl) totalEl.textContent = '$' + total.toLocaleString('es-MX');
        if (footerEl) footerEl.style.display = 'block';
    };

    document.addEventListener('DOMContentLoaded', () => {
        const cartBtn = document.getElementById('cartNavBtn');
        const closeBtn = document.getElementById('cartClose');
        const overlay = document.getElementById('cartOverlay');

        if (cartBtn) cartBtn.addEventListener('click', () => { 
            document.getElementById('cartSidebar')?.classList.add('active','open'); 
            document.getElementById('cartOverlay')?.classList.add('active','open'); 
            window.renderCart();
        });
        if (closeBtn) closeBtn.addEventListener('click', () => { 
            document.getElementById('cartSidebar')?.classList.remove('active','open'); 
            document.getElementById('cartOverlay')?.classList.remove('active','open'); 
        });
        if (overlay) overlay.addEventListener('click', () => { 
            document.getElementById('cartSidebar')?.classList.remove('active','open'); 
            document.getElementById('cartOverlay')?.classList.remove('active','open'); 
        });

        updateCartCount();
    });
})();