function actualizarContadorCarritoGlobal() {
    let carrito = [];
    try { 
        carrito = JSON.parse(localStorage.getItem('ecodren_cart')) || []; 
    } catch (e) { 
        carrito = []; 
    }
 
    const limpio = carrito.filter(i => i && (i.qty || i.cantidad || 0) > 0);
    if (limpio.length !== carrito.length) {
        localStorage.setItem('ecodren_cart', JSON.stringify(limpio));
    }
    const total = limpio.reduce((s, i) => s + parseInt(i.qty || i.cantidad || 1, 10), 0);
    const el = document.getElementById('cartCount');
    if (!el) return;
    el.textContent = total;
    if (total > 0) {
        el.style.display = 'inline-flex';
        el.classList.add('has-items');
    } else {
        el.style.display = 'none';
        el.classList.remove('has-items');
    }
}
 
const nav = document.getElementById('mainNav');
if (nav) {
    const hasHero = !document.getElementById('hero3d');
    window.addEventListener('scroll', () => {
        nav.classList.toggle('scrolled', window.scrollY > 40);
        if (hasHero) nav.classList.toggle('light', window.scrollY > window.innerHeight - 80);
    }, { passive: true });
}
 
const hamburger = document.getElementById('hamburger') || document.getElementById('hamburgerBtn');
const mobileMenu = document.getElementById('mobileMenu');
if (hamburger && mobileMenu) {
    hamburger.addEventListener('click', () => {
        hamburger.classList.toggle('open');
        mobileMenu.classList.toggle('open');
    });
    mobileMenu.querySelectorAll('a').forEach(l =>
        l.addEventListener('click', () => {
            hamburger.classList.remove('open');
            mobileMenu.classList.remove('open');
        })
    );
}
 
const profileBtn = document.getElementById('profileBtn');
const profileDropdown = document.getElementById('profileDropdown');
if (profileBtn && profileDropdown) {
    profileBtn.addEventListener('click', e => {
        e.stopPropagation();
        profileDropdown.classList.toggle('open');
    });
    document.addEventListener('click', () => profileDropdown.classList.remove('open'));
    profileDropdown.addEventListener('click', e => e.stopPropagation());
}
 
window.openModal = function(tab) {
    const overlay = document.getElementById('modalOverlay');
    if (!overlay) return;
    overlay.classList.add('open');
    if (profileDropdown) profileDropdown.classList.remove('open');
    switchTab(tab);
};

window.closeModal = function() {
    const overlay = document.getElementById('modalOverlay');
    if (overlay) overlay.classList.remove('open');
};

window.switchTab = function(t) {
    const tabsWrapper = document.querySelector('.modal-tabs');
    if (tabsWrapper) tabsWrapper.style.display = (t === 'checkout' || t === 'forget') ? 'none' : 'flex';
    document.querySelectorAll('.modal-tab').forEach((b, i) =>
        b.classList.toggle('active', (i === 0 && t === 'login') || (i === 1 && t === 'register'))
    );
    ['login','register','forget','checkout'].forEach(name => {
        const p = document.getElementById('panel-' + name);
        if (p) p.classList.toggle('active', t === name);
    });
};

window.openForgetPanel = function() {
    ['login','register'].forEach(n => document.getElementById('panel-' + n)?.classList.remove('active'));
    document.querySelectorAll('.modal-tab').forEach(b => b.classList.remove('active'));
    document.getElementById('panel-forget')?.classList.add('active');
};

window.handleForgetPassword = function(event) {
    event.preventDefault();
    const email = document.getElementById('forgetEmail')?.value.trim();
    showToast(`Enlace enviado a: ${email}`, 'success');
    switchTab('login');
};

const modalOverlay = document.getElementById('modalOverlay');
if (modalOverlay) {
    modalOverlay.addEventListener('click', e => { if (e.target === modalOverlay) closeModal(); });
}
 
window.handleLogin = async function(e) {
    e.preventDefault();
    const email    = document.getElementById('loginEmail')?.value.trim().toLowerCase() ?? '';
    const password = document.getElementById('loginPassword')?.value ?? '';
    const btn      = document.querySelector('#panel-login .mform-submit');
 
    if (!email || !password) { showToast('Completa todos los campos.', 'error'); return; }
 
    const users = JSON.parse(localStorage.getItem('ecodren_users') ?? '[]');
    const hash  = await hashPassword(password);
    const found = users.find(u => u.email === email && u.password === hash);
 
    if (!found) {
        if (btn) { btn.textContent = '⚠️ Datos incorrectos'; setTimeout(() => { btn.textContent = 'Iniciar sesión'; }, 2200); }
        return;
    }
    closeModal();
    showToast('Bienvenido, ' + found.name.split(' ')[0] + '.', 'success');
    location.reload();
};
 
window.logOut = function() {
    window.location.href = "/accounts/logout/";
};
 
async function hashPassword(password) {
    const buffer = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(password));
    return Array.from(new Uint8Array(buffer)).map(b => b.toString(16).padStart(2,'0')).join('');
}

function showRegisterStatus(message, isError) {
    const el = document.getElementById('registerErrorMsg');
    if (!el) return;
    el.textContent = (isError ? '⚠️ ' : '') + message;
    el.style.color = isError ? '#c0392b' : 'var(--eco-green)';
    el.style.display = 'block';
}

window.handleRegister = function(event) {
    event.preventDefault();
    const name            = document.getElementById('regName')?.value.trim() ?? '';
    const company         = document.getElementById('regCompany')?.value.trim() ?? '';
    const email           = document.getElementById('regEmail')?.value.trim().toLowerCase() ?? '';
    const password        = document.getElementById('regPassword')?.value ?? '';
    const confirmPassword = document.getElementById('regConfirmPassword')?.value ?? '';
    const termsChecked    = document.getElementById('regTerms')?.checked ?? false;
    const submitBtn       = document.getElementById('regSubmitBtn');
 
    document.getElementById('registerErrorMsg') && (document.getElementById('registerErrorMsg').style.display = 'none');
 
    if (!/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email)) { showRegisterStatus('Correo inválido.', true); return; }
    if (password.length < 8)            { showRegisterStatus('Mínimo 8 caracteres.', true); return; }
    if (password !== confirmPassword)   { showRegisterStatus('Las contraseñas no coinciden.', true); return; }
    if (!termsChecked)                  { showRegisterStatus('Acepta los Términos.', true); return; }
 
    const users = JSON.parse(localStorage.getItem('ecodren_users') ?? '[]');
    if (users.some(u => u.email === email)) { showRegisterStatus('Correo ya registrado.', true); return; }
 
    if (submitBtn) { submitBtn.disabled = true; submitBtn.textContent = 'Procesando...'; }
 
    hashPassword(password).then(hash => {
        users.push({ id: 'usr_' + Date.now(), name, company: company || 'No especificada', email, password: hash, createdAt: new Date().toISOString() });
        localStorage.setItem('ecodren_users', JSON.stringify(users));
        showRegisterStatus('✔ Registro exitoso. Revisa tu correo.', false);
        setTimeout(() => {
            showToast(`Enlace de confirmación enviado a: ${email}`, 'success');
            document.getElementById('registerForm')?.reset();
            switchTab('login');
            if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = 'Crear cuenta'; }
        }, 1800);
    }).catch(() => {
        showRegisterStatus('Error interno. Inténtalo de nuevo.', true);
        if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = 'Crear cuenta'; }
    });
};

function obtenerPrecioNumerico(val) {
    if (typeof val === 'number') return isNaN(val) ? 0 : val;
    if (!val) return 0;
    const limpio = String(val).replace(/[^0-9.-]+/g, "");
    const num = parseFloat(limpio);
    return isNaN(num) ? 0 : num;
}

window.renderCartGlobal = function() {
    const container = document.getElementById('cartItems');
    const footer    = document.getElementById('cartFooter');
    const totalEl   = document.getElementById('cartTotal');
    if (!container) return;
 
    let carrito = [];
    try { 
        carrito = JSON.parse(localStorage.getItem('ecodren_cart')) || [];
    } catch (e) { 
        carrito = []; 
    }
    const limpio = carrito.filter(i => i && (i.qty || i.cantidad || 0) > 0);
 
    if (limpio.length === 0) {
        container.innerHTML = `<div class="cart-empty"><span class="cart-empty-icon">🛒</span><p style="font-weight:600;margin-bottom:.5rem">Tu carrito está vacío</p><p style="font-size:.85rem;color:var(--eco-gray)">Agrega productos desde la tienda</p></div>`;
        if (footer) footer.style.display = 'none';
    } else {
        let html = '', total = 0;
        limpio.forEach(item => {
            const precioNum = obtenerPrecioNumerico(item.precio || item.price || 0);
            const cantidadNum = parseInt(item.qty || item.cantidad || 1, 10);
            total += precioNum * cantidadNum;
            html += `
            <div class="cart-item" style="display:flex;align-items:center;gap:1rem;margin-bottom:1rem;padding-bottom:1rem;border-bottom:1px solid #eee">
                <div style="background:#f8f9fa;width:50px;height:50px;display:flex;align-items:center;justify-content:center;border-radius:8px;flex-shrink:0;overflow:hidden;">
                    <img src="${item.imagen || item.img || '/static/Assets/logo_web_ecodren.png'}" alt="${item.nombre || item.name || 'Producto'}" style="width:100%; height:100%; object-fit:contain; padding:4px;">
                </div>
                <div style="flex:1;min-width:0">
                    <h4 style="margin:0;font-size:.88rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${item.nombre || item.name || 'Producto'}</h4>
                    <div style="color:var(--eco-green);font-weight:600;font-size:.88rem">$${precioNum.toLocaleString('es-MX', {minimumFractionDigits: 2, maximumFractionDigits: 2})} MXN</div>
                    <div style="display:flex;align-items:center;gap:.4rem;margin-top:.35rem">
                        <button onclick="changeGlobalQty('${item.id}',-1)" class="qty-btn">−</button>
                        <span style="font-size:.85rem;min-width:20px;text-align:center">${cantidadNum}</span>
                        <button onclick="changeGlobalQty('${item.id}',1)" class="qty-btn">+</button>
                    </div>
                </div>
                <button onclick="removeGlobalItem('${item.id}')" style="background:none;border:none;color:#c0392b;cursor:pointer;font-size:1.4rem;padding:0 .3rem;flex-shrink:0">×</button>
            </div>`;
        });
        container.innerHTML = html;
        if (totalEl) totalEl.textContent = `$${total.toLocaleString('es-MX', {minimumFractionDigits: 2, maximumFractionDigits: 2})} MXN`;
        if (footer) footer.style.display = 'block';
    }
    actualizarContadorCarritoGlobal();
};
 
window.changeGlobalQty = function(id, d) {
    let carrito = JSON.parse(localStorage.getItem('ecodren_cart') ?? '[]');
    const item  = carrito.find(i => String(i.id) === String(id));
    if (!item) return;
    
    let currentQty = parseInt(item.qty || item.cantidad || 1, 10);
    currentQty += d;
    item.qty = currentQty;
    item.cantidad = currentQty;

    if (currentQty < 1) {
        carrito = carrito.filter(i => String(i.id) !== String(id));
    }
    
    localStorage.setItem('ecodren_cart', JSON.stringify(carrito));
    renderCartGlobal();
};
 
window.removeGlobalItem = function(id) {
    let carrito = JSON.parse(localStorage.getItem('ecodren_cart') ?? '[]');
    localStorage.setItem('ecodren_cart', JSON.stringify(carrito.filter(i => String(i.id) !== String(id))));
    renderCartGlobal();
};
 
window.handleCheckout = function() {
    const carrito = JSON.parse(localStorage.getItem('ecodren_cart') ?? '[]');
    if (carrito.length === 0) { showToast('Tu carrito está vacío.', 'error'); return; }
    
    const isAuthenticated = document.body.dataset.userAuth === 'true';
    if (!isAuthenticated) {
        document.getElementById('cartSidebar')?.classList.remove('active','open');
        document.getElementById('cartOverlay')?.classList.remove('active','open');
        showToast('Inicia sesión para continuar.', 'info');
        openModal('login');
        return;
    }
    
    const total = carrito.reduce((s, i) => {
        const precio = obtenerPrecioNumerico(i.precio || i.price || 0);
        const qty = parseInt(i.qty || i.cantidad || 1, 10);
        return s + (precio * qty);
    }, 0);
    
    const el = document.getElementById('checkoutTotalDisplay');
    if (el) el.textContent = `$${total.toLocaleString('es-MX', {minimumFractionDigits: 2, maximumFractionDigits: 2})} MXN`;
    document.getElementById('cartSidebar')?.classList.remove('active','open');
    document.getElementById('cartOverlay')?.classList.remove('active','open');
    openModal('checkout');
};
 
window.processSimulatedPayment = async function(e) {
    e.preventDefault();
    
    let carrito = [];
    try {
        carrito = JSON.parse(localStorage.getItem('ecodren_cart')) || [];
    } catch (err) {
        carrito = [];
    }

    if (carrito.length === 0) {
        showToast('Tu carrito está vacío.', 'error');
        return;
    }

    const totalCalculado = carrito.reduce((acc, item) => {
        const precio = obtenerPrecioNumerico(item.precio || item.price || 0);
        const qty = parseInt(item.qty || item.cantidad || 1, 10);
        return acc + (precio * qty);
    }, 0);

    const totalPagar = `$${totalCalculado.toLocaleString('es-MX', {minimumFractionDigits: 2, maximumFractionDigits: 2})} MXN`;
    const modalBox = document.querySelector('#modalOverlay .modal-box');
    const btn = e.target.querySelector('button[type="submit"]');

    if (btn) {
        btn.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Procesando Orden en Servidor...';
        btn.disabled = true;
    }

    try {
        const response = await fetch('/api/crear-pedido/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken') || document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
            },
            body: JSON.stringify({
                items: carrito,
                total: totalCalculado
            })
        });

        const data = await response.json();

        if (response.ok && data.status === 'ok') {
            const numeroTicket = data.codigo_pedido || ("EC-" + Math.floor(100000 + Math.random() * 900000));
            
            localStorage.removeItem('ecodren_cart');
            actualizarContadorCarritoGlobal();

            if (btn) {
                btn.innerHTML = '<i class="fas fa-check"></i> ¡Pago Autorizado!';
                btn.style.background = 'var(--eco-green, #0f5429)';
            }

            setTimeout(() => {
                if (modalBox) {
                    modalBox.innerHTML = `
                        <div class="checkout-success-wrapper">
                            <div class="success-icon-animated">
                                <i class="fas fa-check-circle"></i>
                            </div>
                            <h3>¡Pago Autorizado!</h3>
                            <p>Tu orden ha sido registrada en el sistema de logística de Ecodren y guardada en tu historial.</p>
                            
                            <div class="order-meta-box">
                                <div class="order-meta-row">
                                    <span>No. Pedimento / Ticket:</span>
                                    <strong>${numeroTicket}</strong>
                                </div>
                                <div class="order-meta-row">
                                    <span>Monto Liquidado:</span>
                                    <strong style="color: #0f5429;">${totalPagar}</strong>
                                </div>
                                <div class="order-meta-row">
                                    <span>Estatus de Despacho:</span>
                                    <strong style="color: #e85c1a;">En Preparación</strong>
                                </div>
                            </div>

                            <button class="mform-submit" onclick="closeModalAndRedirect();" style="margin-top: 0; padding: 0.85rem; width: 100%;">
                                Ver Mi Historial de Pedidos <i class="fas fa-arrow-right" style="margin-left: 6px;"></i>
                            </button>
                        </div>
                    `;
                }
            }, 900);
        } else {
            showToast(data.mensaje || 'Error al procesar el pedido.', 'error');
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = 'Proceder al Pago Seguro';
            }
        }
    } catch (error) {
        console.error("Error al registrar pedido:", error);
        showToast('Error de conexión con el servidor de pagos.', 'error');
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = 'Proceder al Pago Seguro';
        }
    }
};

window.closeModalAndRedirect = function() {
    const overlay = document.getElementById('modalOverlay');
    if (overlay) overlay.classList.remove('open');
    setTimeout(() => {
        window.location.href = "/perfil/?tab=pedidos";
    }, 300);
};
 
document.addEventListener('change', e => {
    if (e.target.name !== 'payMethod') return;

    document.querySelectorAll('.payment-method-option').forEach(opt => {
        opt.style.borderColor = '#ddd';
        opt.style.backgroundColor = 'transparent';
        const icon = opt.querySelector('i');
        const span = opt.querySelector('span');
        if (icon) icon.style.color = 'var(--eco-gray)';
        if (span) span.style.color = 'var(--eco-gray)';
    });

    const sel = e.target.closest('.payment-method-option');
    if (sel) {
        sel.style.borderColor = 'var(--eco-green)';
        sel.style.backgroundColor = 'rgba(191, 253, 0, 0.05)';
        const icon = sel.querySelector('i');
        const span = sel.querySelector('span');
        if (icon) icon.style.color = 'var(--eco-dark)';
        if (span) span.style.color = 'inherit';
    }

    const cardForm = document.getElementById('cardDetailsForm');
    const speiInfo = document.getElementById('speiDetailsInfo');
    const cardInputs = cardForm ? cardForm.querySelectorAll('input') : [];

    if (e.target.value === 'transfer') {
        if (cardForm) cardForm.style.display = 'none';
        if (speiInfo) speiInfo.style.display = 'block';
        cardInputs.forEach(input => input.removeAttribute('required'));
    } else {
        if (cardForm) cardForm.style.display = 'block';
        if (speiInfo) speiInfo.style.display = 'none';
        cardInputs.forEach(input => input.setAttribute('required', 'required'));
    }
});
 
const revealObserver = new IntersectionObserver(
    entries => entries.forEach(e => {
        if (e.isIntersecting) { e.target.classList.add('visible'); revealObserver.unobserve(e.target); }
    }),
    { threshold: 0.1 }
);
document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));
 
window.handleSubmit = async function(e) {
    e.preventDefault();
    const form = e.target;
    const btn = form.querySelector('.form-submit');
    const originalText = btn.textContent;
    const formData = new FormData(form);

    btn.disabled = true;
    btn.textContent = 'Enviando cotización...';

    try {
        const response = await fetch('/api/enviar-cotizacion/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        const data = await response.json();

        if (response.ok && data.status === 'ok') {
            btn.textContent = '✅ ¡Enviada!';
            showToast(data.mensaje, 'success');
            form.reset();
        } else {
            showToast(data.mensaje || 'Ocurrió un error al procesar tu solicitud.', 'error');
            btn.textContent = originalText;
        }
    } catch (error) {
        showToast('Error de conexión con el servidor.', 'error');
        btn.textContent = originalText;
    } finally {
        setTimeout(() => {
            btn.disabled = false;
            btn.textContent = originalText;
        }, 3500);
    }
};
 
function initFleetCarousel() {
    document.querySelectorAll('.fleet-img-wrap').forEach(container => {
        const images = container.querySelectorAll('.fleet-img');
        if (images.length <= 1) return;
        if (!container.querySelector('.fleet-img.active')) images[0].classList.add('active');
        let current = [...images].findIndex(img => img.classList.contains('active'));
        if (current < 0) current = 0;
        setInterval(() => {
            images[current].classList.remove('active');
            current = (current + 1) % images.length;
            images[current].classList.add('active');
        }, 2500);
    });
}
 
function inicializarInteraccionCarrito() {
    const cartBtn     = document.getElementById('cartNavBtn');
    const cartSidebar = document.getElementById('cartSidebar');
    const cartOverlay = document.getElementById('cartOverlay');
    const cartClose   = document.getElementById('cartClose');
    const cerrar = () => {
        cartSidebar?.classList.remove('active','open');
        cartOverlay?.classList.remove('active','open');
    };
    cartBtn     && (cartBtn.onclick = e => { e.preventDefault(); renderCartGlobal(); cartSidebar?.classList.add('active','open'); cartOverlay?.classList.add('active','open'); });
    cartClose   && (cartClose.onclick   = cerrar);
    cartOverlay && (cartOverlay.onclick = cerrar);
}
 
window.showToast = function(mensaje, tipo = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast ${tipo}`;
    const icon = tipo === 'success' ? 'fa-circle-check' : tipo === 'error' ? 'fa-circle-xmark' : 'fa-circle-info';
    
    toast.innerHTML = `
        <i class="fa-solid ${icon}"></i>
        <div class="toast-content">
            <div class="toast-message">${mensaje}</div>
        </div>
        ${tipo === 'success' ? `<button class="toast-action-btn" onclick="if(typeof openCart === 'function') { openCart(); } else { document.getElementById('cartNavBtn')?.click(); }">Ver Carrito</button>` : ''}
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'toastOut 0.3s ease forwards';
        setTimeout(() => toast.remove(), 300);
    }, 3800);
};
 
document.addEventListener('DOMContentLoaded', () => {
    initFleetCarousel();
    inicializarInteraccionCarrito();
    actualizarContadorCarritoGlobal();
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

async function enviarPeticionSegura(url, data, metodo = 'POST') {
    const csrftoken = getCookie('csrftoken');
    return await fetch(url, {
        method: metodo,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify(data)
    });
}