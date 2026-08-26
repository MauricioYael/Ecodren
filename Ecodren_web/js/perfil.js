// ── 💾 PERSISTENCIA Y CARGA DE DATOS OPERATIVOS ───────────────────
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
            if (avatarEl) avatarEl.innerText = data.nombre.charAt(0).toUpperCase();
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

window.guardarDatosOperativos = function(e) {
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

    localStorage.setItem('ecodren_perfil_datos', JSON.stringify(perfilData));

    setTimeout(() => {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="fa-solid fa-check"></i> ¡Guardado!';
            btn.style.background = 'var(--eco-green, #0f5429)';
        }

        // Actualizar datos visibles en tiempo real
        cargarDatosOperativosGuardados();

        if (typeof showToast === 'function') {
            showToast('Información operativa actualizada con éxito.', 'success');
        } else {
            alert("✅ Información corporativa actualizada con éxito.");
        }

        setTimeout(() => {
            if (btn) {
                btn.innerHTML = originalContent;
                btn.style.background = '';
            }
        }, 2200);
    }, 600);
};

document.addEventListener('DOMContentLoaded', () => {

    // Cargar datos operativos guardados al iniciar
    cargarDatosOperativosGuardados();

    // ── 🚀 DETECTOR DE RUTAS E INYECCIÓN DIRECTA DESDE EL NAV ──────────
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

    // ── 💻 MANEJO DE PESTAÑAS (ESCRITORIO & MÓVIL) ────────────────────
    const menuButtons = document.querySelectorAll('.sidebar-menu-item');
    menuButtons.forEach(button => {
        button.addEventListener('click', () => {
            const paneId = button.dataset.pane;

            menuButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');

            document.querySelectorAll('.profile-pane').forEach(pane => pane.classList.remove('active'));
            const targetPane = document.getElementById(`pane-${paneId}`);
            if (targetPane) targetPane.classList.add('active');

            // Cierre automático del menú móvil al seleccionar
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

    // ── 📱 ACORDEÓN DESPLEGABLE PARA CELULARES ────────────────────────
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
    });

    // ── 📍 SISTEMA COMPLETO E INTERACTIVO DE DIRECCIONES (CRUD) ───────
    const btnToggleAddressForm = document.getElementById('btn-toggle-address-form');
    const addressFormContainer = document.getElementById('address-form-container');
    const btnCancelAddress = document.getElementById('btn-cancel-address');
    const formManageAddress = document.getElementById('form-manage-address');
    const addressCardsList = document.getElementById('address-cards-list');

    // Campos del formulario de dirección
    const addressIdField = document.getElementById('address-id-field');
    const addressNameInput = document.getElementById('address-name');
    const addressStreetInput = document.getElementById('address-street');
    const addressColonyInput = document.getElementById('address-colony');
    const addressCpInput = document.getElementById('address-cp');
    const addressCityInput = document.getElementById('address-city');
    const addressFormTitle = document.getElementById('address-form-title');

    // Abrir formulario para agregar nueva dirección
    if (btnToggleAddressForm && addressFormContainer) {
        btnToggleAddressForm.addEventListener('click', () => {
            resetAddressForm();
            if (addressFormTitle) addressFormTitle.innerHTML = `<i class="fa-solid fa-map-location-dot"></i> Agregar Nueva Dirección`;
            addressFormContainer.classList.toggle('active');
        });
    }

    // Cancelar formulario
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

    // Procesar alta o edición de dirección
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

    // ── 🔒 GESTIÓN DE SEGURIDAD Y PREFERENCIAS GENERALES ──────────────
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

// ── 📞 CONTROL GLOBAL DEL MENÚ FLOTANTE DE SOPORTE ────────────────────
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

document.addEventListener('click', () => {
    const triggerCard = document.getElementById('btn-support-trigger');
    const floatingMenu = document.getElementById('supportFloatingMenu');

    if (floatingMenu && floatingMenu.classList.contains('open')) {
        floatingMenu.classList.remove('open');
        if (triggerCard) triggerCard.classList.remove('open-active');
    }
});

window.confirmDeleteAccount = function() {
    if (confirm("🚨 ALERTA CRÍTICA: ¿Estás seguro de querer dar de baja esta cuenta? Se perderán todos tus pedimentos logísticos.")) {
        alert("Solicitud de desactivación enviada a revisión con el administrador de Equipos MC.");
    }
};

let modoEdicionActivo = false;

window.toggleModoEdicion = function() {
    modoEdicionActivo = !modoEdicionActivo;
    const inputs = document.querySelectorAll('#form-datos-empresa .operational-inline-input');
    const btnToggle = document.getElementById('btnToggleEdit');
    const containerSave = document.getElementById('containerSaveBtn');

    if (modoEdicionActivo) {
        // Habilitar edición
        inputs.forEach(input => input.removeAttribute('readonly'));
        if (btnToggle) {
            btnToggle.classList.add('active-edit');
            btnToggle.innerHTML = '<i class="fa-solid fa-xmark"></i> <span>Cancelar</span>';
        }
        if (containerSave) containerSave.style.display = 'block';
        document.getElementById('inputNombreCompleto')?.focus();
    } else {
        // Deshabilitar edición / Restaurar valores guardados
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
            if (avatarEl) avatarEl.innerText = data.nombre.charAt(0).toUpperCase();
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

window.guardarDatosOperativos = function(e) {
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

    localStorage.setItem('ecodren_perfil_datos', JSON.stringify(perfilData));

    setTimeout(() => {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="fa-solid fa-check"></i> ¡Guardado!';
            btn.style.background = 'var(--eco-green, #0f5429)';
        }

        // Bloquear de nuevo los inputs a modo solo lectura
        window.toggleModoEdicion();
        cargarDatosOperativosGuardados();

        if (typeof showToast === 'function') {
            showToast('Información operativa actualizada con éxito.', 'success');
        } else {
            alert("✅ Información corporativa actualizada con éxito.");
        }

        setTimeout(() => {
            if (btn) {
                btn.innerHTML = originalContent;
                btn.style.background = '';
            }
        }, 2000);
    }, 500);
};