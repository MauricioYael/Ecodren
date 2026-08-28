function cargarDatosOperativosGuardados() {
    const saved = localStorage.getItem('ecodren_perfil_datos');
    if (!saved) return;
    try {
        const data = JSON.parse(saved);
        if (data.nombre) {
            const inputNombre = document.getElementById('inputNombreCompleto');
            const userNameEl = document.getElementById('userName');
            const welcomeEl = document.getElementById('displayWelcomeName');
            const avatarEl = document.getElementById('userAvatar');
            if (inputNombre) inputNombre.value = data.nombre;
            if (userNameEl) userNameEl.innerText = data.nombre;
            if (welcomeEl) welcomeEl.innerText = data.nombre.split(' ')[0];
            if (avatarEl && !localStorage.getItem('ecodren_user_avatar')) {
                avatarEl.innerText = data.nombre.charAt(0).toUpperCase();
            }
        }
        if (data.razon) {
            const inputRazon = document.getElementById('inputRazonSocial');
            if (inputRazon) inputRazon.value = data.razon;
        }
        if (data.email) {
            const inputEmail = document.getElementById('inputEmailOperativo');
            const userEmailEl = document.getElementById('userEmail');
            if (inputEmail) inputEmail.value = data.email;
            if (userEmailEl) userEmailEl.innerText = data.email;
        }
        if (data.telefono) {
            const inputTel = document.getElementById('inputTelefonoOperativo');
            if (inputTel) inputTel.value = data.telefono;
        }
        if (data.direccion) {
            const inputDir = document.getElementById('inputDireccionPrincipal');
            if (inputDir) inputDir.value = data.direccion;
        }
    } catch (e) {
        console.error("Error al cargar datos operativos:", e);
    }
}

window.guardarDatosOperativos = async function(e) {
    e.preventDefault();
    const btn = document.getElementById('btnSaveOperational');
    const originalContent = btn ? btn.innerHTML : '';

    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Guardando...';
    }

    const perfilData = {
        nombre: document.getElementById('inputNombreCompleto')?.value.trim() || '',
        razon: document.getElementById('inputRazonSocial')?.value.trim() || '',
        email: document.getElementById('inputEmailOperativo')?.value.trim() || '',
        telefono: document.getElementById('inputTelefonoOperativo')?.value.trim() || '',
        direccion: document.getElementById('inputDireccionPrincipal')?.value.trim() || ''
    };

    try {
        const response = await fetch('/api/actualizar-perfil/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
            },
            body: JSON.stringify(perfilData)
        });

        const resData = await response.json();

        if (response.ok && resData.status === 'ok') {
            const userNameEl = document.getElementById('userName');
            const welcomeEl = document.getElementById('displayWelcomeName');
            const avatarEl = document.getElementById('userAvatar');
            const userEmailEl = document.getElementById('userEmail');

            if (userNameEl) userNameEl.innerText = resData.nombre;
            if (welcomeEl) welcomeEl.innerText = resData.nombre.split(' ')[0];
            if (avatarEl && !localStorage.getItem('ecodren_user_avatar')) {
                avatarEl.innerText = resData.nombre.charAt(0).toUpperCase();
            }
            if (userEmailEl) userEmailEl.innerText = resData.email;

            localStorage.setItem('ecodren_perfil_datos', JSON.stringify(perfilData));

            if (btn) {
                btn.disabled = false;
                btn.innerHTML = '<i class="fa-solid fa-check"></i> ¡Guardado!';
                btn.style.background = 'var(--eco-green, #0f5429)';
            }

            window.toggleModoEdicion();

            if (typeof showToast === 'function') {
                showToast(resData.mensaje, 'success');
            } else {
                alert("✅ " + resData.mensaje);
            }
        } else {
            alert("❌ Error: " + (resData.mensaje || 'No se pudo actualizar'));
            if (btn) btn.disabled = false;
        }
    } catch (err) {
        alert("❌ Error de conexión al guardar los datos en MySQL.");
        if (btn) btn.disabled = false;
    } finally {
        setTimeout(() => {
            if (btn) {
                btn.innerHTML = originalContent;
                btn.style.background = '';
            }
        }, 2200);
    }
};

let modoEdicionActivo = false;

window.toggleModoEdicion = function() {
    modoEdicionActivo = !modoEdicionActivo;
    const inputs = document.querySelectorAll('#form-datos-empresa .operational-inline-input');
    const btnToggle = document.getElementById('btnToggleEdit');
    const containerSave = document.getElementById('containerSaveBtn');

    if (modoEdicionActivo) {
        inputs.forEach(input => input.removeAttribute('readonly'));
        if (btnToggle) {
            btnToggle.classList.add('active-edit');
            btnToggle.innerHTML = '<i class="fa-solid fa-xmark"></i> <span>Cancelar</span>';
        }
        if (containerSave) containerSave.style.display = 'block';
        document.getElementById('inputNombreCompleto')?.focus();
    } else {
        inputs.forEach(input => input.setAttribute('readonly', 'readonly'));
        if (btnToggle) {
            btnToggle.classList.remove('active-edit');
            btnToggle.innerHTML = '<i class="fa-solid fa-pen-to-square"></i> <span>Editar Información</span>';
        }
        if (containerSave) containerSave.style.display = 'none';
        cargarDatosOperativosGuardados();
    }
};

window.habilitarYFocarDireccion = function() {
    if (!modoEdicionActivo) {
        window.toggleModoEdicion();
    }
    const inputDir = document.getElementById('inputDireccionPrincipal');
    if (inputDir) {
        inputDir.focus();
        inputDir.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
};

window.togglePaymentForm = function() {
    const formBox = document.getElementById('payment-form-container');
    if (!formBox) return;
    const isActive = formBox.classList.toggle('active');
    if (isActive) {
        document.getElementById('form-manage-payment')?.reset();
        window.cambiarTipoMetodoForm('card');
        formBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
};

window.cambiarTipoMetodoForm = function(tipo) {
    const rowCard = document.getElementById('row-card-fields');
    const rowSpei = document.getElementById('row-spei-field');
    const inputNum = document.getElementById('payment-number');
    const inputExp = document.getElementById('payment-expiry');
    const inputClabe = document.getElementById('payment-clabe');
    const lblTitle = document.getElementById('lbl-payment-title');

    if (tipo === 'spei') {
        if (rowCard) rowCard.style.display = 'none';
        if (rowSpei) rowSpei.style.display = 'block';
        if (lblTitle) lblTitle.textContent = 'Banco / Nombre del Beneficiario';
        inputNum?.removeAttribute('required');
        inputExp?.removeAttribute('required');
        inputClabe?.setAttribute('required', 'required');
    } else {
        if (rowCard) rowCard.style.display = 'grid';
        if (rowSpei) rowSpei.style.display = 'none';
        if (lblTitle) lblTitle.textContent = 'Identificador / Nombre en la Tarjeta';
        inputNum?.setAttribute('required', 'required');
        inputExp?.setAttribute('required', 'required');
        inputClabe?.removeAttribute('required');
    }
};

window.guardarNuevoMetodoPago = function(event) {
    event.preventDefault();
    const tipo = document.getElementById('payment-type').value;
    const titulo = document.getElementById('payment-title').value.trim();
    const grid = document.getElementById('payment-methods-grid');
    const newId = Date.now();

    let iconHtml = '<i class="fa-solid fa-credit-card"></i>';
    let infoHtml = '';

    if (tipo === 'spei') {
        const clabe = document.getElementById('payment-clabe').value.trim();
        const ultimosDigitos = clabe.slice(-4) || '••••';
        iconHtml = '<i class="fa-solid fa-wallet"></i>';
        infoHtml = `
            <label>${titulo || 'Transferencia Interbancaria (SPEI)'}</label>
            <p>Transferencia Interbancaria (SPEI)</p>
            <label style="margin-top: 4px;">CLABE Registrada: •••• ${ultimosDigitos}</label>
        `;
    } else {
        const tarjeta = document.getElementById('payment-number').value.trim();
        const vencimiento = document.getElementById('payment-expiry').value.trim();
        const ultimosDigitos = tarjeta.slice(-4) || '••••';
        iconHtml = '<i class="fa-solid fa-credit-card"></i>';
        infoHtml = `
            <label>${titulo || 'Tarjeta de Crédito / Débito'}</label>
            <p>•••• •••• •••• ${ultimosDigitos}</p>
            <label style="margin-top: 4px; color: #10b981; font-weight: 700;">Vence: ${vencimiento}</label>
        `;
    }

    const cardElement = document.createElement('div');
    cardElement.className = 'swipe-container-wrapper';
    cardElement.setAttribute('data-payment-id', newId);
    cardElement.innerHTML = `
        <div class="company-card payment-swipe-card">
            <div class="company-card-icon">${iconHtml}</div>
            <div class="company-card-info">
                ${infoHtml}
            </div>
            <div class="desktop-card-actions">
                <button type="button" class="btn-action-delete" title="Eliminar" onclick="eliminarMetodoPago('${newId}')"><i class="fa-solid fa-trash"></i></button>
            </div>
        </div>
    `;

    if (grid) grid.appendChild(cardElement);
    window.togglePaymentForm();

    if (typeof showToast === 'function') {
        showToast('Método de pago registrado con éxito.', 'success');
    } else {
        alert("✅ Método de pago guardado.");
    }
};

window.eliminarMetodoPago = function(id) {
    const card = document.querySelector(`.swipe-container-wrapper[data-payment-id="${id}"]`);
    if (card) {
        card.style.opacity = '0';
        card.style.transform = 'scale(0.9)';
        card.style.transition = 'all 0.25s ease';
        setTimeout(() => {
            card.remove();
            if (typeof showToast === 'function') {
                showToast('Método de pago eliminado.', 'info');
            }
        }, 250);
    }
};

window.toggleSupportMenu = function(event) {
    event.preventDefault();
    event.stopPropagation();

    const triggerCard = document.getElementById('btn-support-trigger');
    const floatingMenu = document.getElementById('supportFloatingMenu');

    if (triggerCard && floatingMenu) {
        triggerCard.classList.toggle('open-active');
        floatingMenu.classList.toggle('open');
    }
};

window.confirmDeleteAccount = function() {
    if (confirm("🚨 ALERTA CRÍTICA: ¿Estás seguro de querer dar de baja esta cuenta? Se perderán todos tus pedimentos logísticos.")) {
        alert("Solicitud de desactivación enviada a revisión con el administrador de Equipos MC.");
    }
};

document.addEventListener('DOMContentLoaded', () => {
    cargarDatosOperativosGuardados();
    cargarAvatarGuardado();

    const btnAddPayment = document.getElementById('btn-add-payment');
    if (btnAddPayment) {
        btnAddPayment.onclick = function(e) {
            e.preventDefault();
            window.togglePaymentForm();
        };
    }

    setTimeout(() => {
        const urlParams = new URLSearchParams(window.location.search);
        let activeParam = urlParams.get('tab') || urlParams.get('pane');

        if (activeParam) {
            if (activeParam === 'preferencias') activeParam = 'configuracion';

            const targetButton = document.querySelector(`.sidebar-menu-item[data-pane="${activeParam}"]`);
            
            if (targetButton) {
                document.querySelectorAll('.sidebar-menu-item').forEach(btn => btn.classList.remove('active'));
                document.querySelectorAll('.profile-pane').forEach(pane => pane.classList.remove('active'));

                targetButton.classList.add('active');
                const targetPane = document.getElementById(`pane-${activeParam}`);
                if (targetPane) targetPane.classList.add('active');
                
                const mobileTriggerSpan = document.querySelector('#mobileMenuTrigger span');
                if (mobileTriggerSpan) mobileTriggerSpan.innerHTML = targetButton.innerHTML;
            }
        }
    }, 100);

    const menuButtons = document.querySelectorAll('.sidebar-menu-item');
    menuButtons.forEach(button => {
        button.addEventListener('click', () => {
            const paneId = button.dataset.pane;

            menuButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');

            document.querySelectorAll('.profile-pane').forEach(pane => pane.classList.remove('active'));
            const targetPane = document.getElementById(`pane-${paneId}`);
            if (targetPane) targetPane.classList.add('active');

            const accordionMenu = document.getElementById('accordionMenu');
            const mobileMenuTrigger = document.getElementById('mobileMenuTrigger');
            if (accordionMenu && accordionMenu.classList.contains('open')) {
                accordionMenu.classList.remove('open');
                if (mobileMenuTrigger) mobileMenuTrigger.classList.remove('open');
                const mobileTriggerSpan = mobileMenuTrigger.querySelector('span');
                if (mobileTriggerSpan) mobileTriggerSpan.innerHTML = button.innerHTML;
            }
        });
    });

    const mobileMenuTrigger = document.getElementById('mobileMenuTrigger');
    const accordionMenu = document.getElementById('accordionMenu');

    if (mobileMenuTrigger && accordionMenu) {
        mobileMenuTrigger.addEventListener('click', (e) => {
            e.stopPropagation();
            mobileMenuTrigger.classList.toggle('open');
            accordionMenu.classList.toggle('open');
        });
    }

    document.addEventListener('click', (e) => {
        if (accordionMenu && accordionMenu.classList.contains('open')) {
            if (!e.target.closest('.profile-sidebar')) {
                accordionMenu.classList.remove('open');
                if (mobileMenuTrigger) mobileMenuTrigger.classList.remove('open');
            }
        }

        const triggerCard = document.getElementById('btn-support-trigger');
        const floatingMenu = document.getElementById('supportFloatingMenu');
        if (floatingMenu && floatingMenu.classList.contains('open')) {
            if (!e.target.closest('.sidebar-support-wrapper')) {
                floatingMenu.classList.remove('open');
                if (triggerCard) triggerCard.classList.remove('open-active');
            }
        }
    });

    const btnToggleAddressForm = document.getElementById('btn-toggle-address-form');
    const addressFormContainer = document.getElementById('address-form-container');
    const btnCancelAddress = document.getElementById('btn-cancel-address');
    const formManageAddress = document.getElementById('form-manage-address');
    const addressCardsList = document.getElementById('address-cards-list');

    const addressIdField = document.getElementById('address-id-field');
    const addressNameInput = document.getElementById('address-name');
    const addressStreetInput = document.getElementById('address-street');
    const addressColonyInput = document.getElementById('address-colony');
    const addressCpInput = document.getElementById('address-cp');
    const addressCityInput = document.getElementById('address-city');
    const addressFormTitle = document.getElementById('address-form-title');

    if (btnToggleAddressForm && addressFormContainer) {
        btnToggleAddressForm.addEventListener('click', () => {
            resetAddressForm();
            if (addressFormTitle) addressFormTitle.innerHTML = `<i class="fa-solid fa-map-location-dot"></i> Agregar Nueva Dirección`;
            addressFormContainer.classList.toggle('active');
        });
    }

    if (btnCancelAddress && addressFormContainer) {
        btnCancelAddress.addEventListener('click', () => {
            addressFormContainer.classList.remove('active');
            resetAddressForm();
        });
    }

    function resetAddressForm() {
        if (formManageAddress) formManageAddress.reset();
        if (addressIdField) addressIdField.value = '';
    }

    if (formManageAddress) {
        formManageAddress.addEventListener('submit', (e) => {
            e.preventDefault();

            const id = addressIdField.value;
            const name = addressNameInput.value;
            const street = addressStreetInput.value;
            const colony = addressColonyInput.value;
            const cp = addressCpInput.value;
            const city = addressCityInput.value;

            if (id) {
                const existingCard = document.querySelector(`.operational-address-block[data-id="${id}"]`);
                if (existingCard) {
                    existingCard.querySelector('.card-title-data').innerText = name;
                    existingCard.querySelector('.card-desc-data').innerHTML = `${street}, Col. ${colony}, C.P. ${cp}<br>${city}, México`;
                    alert("✅ Dirección actualizada correctamente.");
                }
            } else {
                const newId = Date.now();
                const newCardHTML = `
                    <div class="operational-address-block" data-id="${newId}">
                        <div class="address-icon-box"><i class="fa-solid fa-location-dot"></i></div>
                        <div class="address-text-box">
                            <h4 class="card-title-data">${name}</h4>
                            <p class="card-desc-data">${street}, Col. ${colony}, C.P. ${cp}<br>${city}, México</p>
                        </div>
                        <div class="address-action-box">
                            <button class="btn-address-edit-inline" title="Editar dirección"><i class="fa-solid fa-pen"></i> Editar</button>
                            <button class="btn-address-delete-inline" title="Eliminar dirección"><i class="fa-solid fa-trash-can"></i></button>
                        </div>
                    </div>
                `;
                if (addressCardsList) addressCardsList.insertAdjacentHTML('beforeend', newCardHTML);
                alert("🎉 Nueva ubicación registrada con éxito.");
            }

            addressFormContainer.classList.remove('active');
            resetAddressForm();
            attachAddressEvents();
        });
    }

    function attachAddressEvents() {
        document.querySelectorAll('.btn-address-edit-inline').forEach(btn => {
            btn.onclick = function(e) {
                e.preventDefault();
                const card = btn.closest('.operational-address-block');
                if (!card || !card.dataset.id) return;
                
                const id = card.dataset.id;
                const name = card.querySelector('.card-title-data')?.innerText || '';
                
                const descRaw = card.querySelector('.card-desc-data')?.innerHTML || '';
                const parts = descRaw.split('<br>');
                const line1 = parts[0] || '';
                const line2 = parts[1] || '';

                const line1Parts = line1.split(', Col. ');
                const street = line1Parts[0] || '';
                const remainingLine1 = line1Parts[1] || '';
                const line1SubParts = remainingLine1.split(', C.P. ');
                const colony = line1SubParts[0] || '';
                const cp = line1SubParts[1] || '';
                const city = line2.replace(', México', '');

                if (addressIdField) addressIdField.value = id;
                if (addressNameInput) addressNameInput.value = name;
                if (addressStreetInput) addressStreetInput.value = street;
                if (addressColonyInput) addressColonyInput.value = colony;
                if (addressCpInput) addressCpInput.value = cp;
                if (addressCityInput) addressCityInput.value = city;

                if (addressFormTitle) addressFormTitle.innerHTML = `<i class="fa-solid fa-pen-to-square"></i> Editar Ubicación Existente`;
                if (addressFormContainer) {
                    addressFormContainer.classList.add('active');
                    addressFormContainer.scrollIntoView({ behavior: 'smooth' });
                }
            };
        });

        document.querySelectorAll('.btn-address-delete-inline').forEach(btn => {
            btn.onclick = function(e) {
                e.preventDefault();
                if (confirm("🗑️ ¿Estás seguro de que deseas eliminar esta dirección de despacho?")) {
                    const card = btn.closest('.operational-address-block');
                    if (card) card.remove();
                }
            };
        });
    }

    attachAddressEvents();

    const formPassword = document.getElementById('form-password');
    if (formPassword) {
        formPassword.addEventListener('submit', (e) => {
            e.preventDefault();
            const newPass = document.getElementById('new-password').value;
            const confirmPass = document.getElementById('confirm-password').value;

            if (newPass !== confirmPass) {
                alert("❌ Las contraseñas nuevas no coinciden. Inténtalo de nuevo.");
                return;
            }
            alert("🔒 Seguridad Ecodren: Contraseña corporativa actualizada con éxito.");
            formPassword.reset();
        });
    }
});

let rawImageSrc = '';
let cropState = { scale: 1, x: 0, y: 0 };
let isDragging = false;
let startPos = { x: 0, y: 0 };

window.manejarSubidaAvatar = function(event) {
    const file = event.target.files[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
        alert('Por favor selecciona un archivo de imagen válido.');
        return;
    }

    const reader = new FileReader();
    reader.onload = function(e) {
        rawImageSrc = e.target.result;
        abrirModalCrop(rawImageSrc);
    };
    reader.readAsDataURL(file);
    event.target.value = '';
};

function abrirModalCrop(src) {
    const modal = document.getElementById('modal-crop-avatar');
    const previewImg = document.getElementById('avatarCropPreview');
    const slider = document.getElementById('avatarZoomSlider');

    cropState = { scale: 1, x: 0, y: 0 };
    if (slider) slider.value = 1;

    if (previewImg) {
        previewImg.src = src;
        previewImg.onload = function() {
            const aspect = previewImg.naturalWidth / previewImg.naturalHeight;
            if (aspect >= 1) {
                previewImg.style.height = '220px';
                previewImg.style.width = 'auto';
            } else {
                previewImg.style.width = '220px';
                previewImg.style.height = 'auto';
            }
            actualizarTransformacionPreview();
        };
    }

    if (modal) modal.classList.add('modal-active');
    iniciarEventosDrag();
}

window.cerrarModalCrop = function() {
    const modal = document.getElementById('modal-crop-avatar');
    if (modal) modal.classList.remove('modal-active');
};

function actualizarTransformacionPreview() {
    const previewImg = document.getElementById('avatarCropPreview');
    if (previewImg) {
        previewImg.style.transform = `translate(calc(-50% + ${cropState.x}px), calc(-50% + ${cropState.y}px)) scale(${cropState.scale})`;
    }
}

function iniciarEventosDrag() {
    const viewport = document.getElementById('avatarCropViewport');
    const slider = document.getElementById('avatarZoomSlider');
    if (!viewport) return;

    slider.oninput = function() {
        cropState.scale = parseFloat(this.value);
        actualizarTransformacionPreview();
    };

    function start(e) {
        isDragging = true;
        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        const clientY = e.touches ? e.touches[0].clientY : e.clientY;
        startPos = { x: clientX - cropState.x, y: clientY - cropState.y };
    }

    function move(e) {
        if (!isDragging) return;
        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        const clientY = e.touches ? e.touches[0].clientY : e.clientY;
        cropState.x = clientX - startPos.x;
        cropState.y = clientY - startPos.y;
        actualizarTransformacionPreview();
    }

    function end() {
        isDragging = false;
    }

    viewport.onmousedown = start;
    window.onmousemove = move;
    window.onmouseup = end;

    viewport.ontouchstart = start;
    window.ontouchmove = move;
    window.ontouchend = end;
}

window.guardarRecorteAvatar = function() {
    const previewImg = document.getElementById('avatarCropPreview');
    if (!previewImg) return;

    const canvas = document.createElement('canvas');
    const size = 300;
    canvas.width = size;
    canvas.height = size;
    const ctx = canvas.getContext('2d');

    const viewportSize = 220;
    const factorCanvas = size / viewportSize;

    const renderedW = previewImg.offsetWidth * cropState.scale * factorCanvas;
    const renderedH = previewImg.offsetHeight * cropState.scale * factorCanvas;

    const centerX = (size / 2) + (cropState.x * factorCanvas);
    const centerY = (size / 2) + (cropState.y * factorCanvas);

    ctx.save();
    ctx.beginPath();
    ctx.arc(size / 2, size / 2, size / 2, 0, Math.PI * 2);
    ctx.closePath();
    ctx.clip();

    ctx.drawImage(previewImg, centerX - (renderedW / 2), centerY - (renderedH / 2), renderedW, renderedH);
    ctx.restore();

    const croppedBase64 = canvas.toDataURL('image/png');
    aplicarAvatarUsuario(croppedBase64);
    localStorage.setItem('ecodren_user_avatar', croppedBase64);

    cerrarModalCrop();

    if (typeof showToast === 'function') {
        showToast('Foto de perfil recortada y actualizada con éxito.', 'success');
    } else {
        alert('✅ Foto de perfil actualizada.');
    }
};

function aplicarAvatarUsuario(imageSrc) {
    const userAvatarEl = document.getElementById('userAvatar');
    if (userAvatarEl && imageSrc) {
        userAvatarEl.innerHTML = `<img src="${imageSrc}" alt="Avatar de usuario" style="width: 100%; height: 100%; object-fit: cover; border-radius: 50%; display: block;">`;
    }

    const navSvg = document.getElementById('navProfileSvg');
    const navImg = document.getElementById('navProfileImg');
    const navBtn = document.getElementById('navProfileBtn') || document.getElementById('profileBtn');

    if (navImg && imageSrc) {
        navImg.src = imageSrc;
        navImg.style.display = 'block';
        if (navSvg) navSvg.style.display = 'none';
        if (navBtn) navBtn.style.border = '1.5px solid var(--eco-lime, #bffd00)';
    }
}

function cargarAvatarGuardado() {
    const savedAvatar = localStorage.getItem('ecodren_user_avatar');
    if (savedAvatar) {
        aplicarAvatarUsuario(savedAvatar);
    }
}