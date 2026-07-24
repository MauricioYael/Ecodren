document.addEventListener('DOMContentLoaded', () => {

    // ── 🚀 DETECTOR DE RUTAS E INYECCIÓN DIRECTA DESDE EL NAV ──────────
    setTimeout(() => {
        const urlParams = new URLSearchParams(window.location.search);
        let activeParam = urlParams.get('tab') || urlParams.get('pane');

        if (activeParam) {
            // Normalización estricta de variables de navegación
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

    // Campos del formulario
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
            addressFormTitle.innerHTML = `<i class="fa-solid fa-map-location-dot"></i> Agregar Nueva Dirección`;
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

    // Resetear formulario
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
                // Modo Edición: Buscar la tarjeta existente por su data-id
                const existingCard = document.querySelector(`.operational-address-block[data-id="${id}"]`);
                if (existingCard) {
                    existingCard.querySelector('.card-title-data').innerText = name;
                    existingCard.querySelector('.card-desc-data').innerHTML = `${street}, Col. ${colony}, C.P. ${cp}<br>${city}, México`;
                    alert("✅ Dirección actualizada correctamente.");
                }
            } else {
                // Modo Creación: Generar una nueva tarjeta dinámica con un ID basado en timestamps
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
            attachAddressEvents(); // Re-vincular eventos a los nuevos botones creados
        });
    }

    // Vincular funciones de Editar y Eliminar de las tarjetas
    function attachAddressEvents() {
        // Evento Editar
        document.querySelectorAll('.btn-address-edit-inline').forEach(btn => {
            btn.onclick = function(e) {
                e.preventDefault();
                const card = btn.closest('.operational-address-block');
                const id = card.dataset.id;
                const name = card.querySelector('.card-title-data').innerText;
                
                // Mapeo simple de datos del string
                const descRaw = card.querySelector('.card-desc-data').innerHTML;
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

                // Cargar datos en el formulario
                addressIdField.value = id;
                addressNameInput.value = name;
                addressStreetInput.value = street;
                addressColonyInput.value = colony;
                addressCpInput.value = cp;
                addressCityInput.value = city;

                addressFormTitle.innerHTML = `<i class="fa-solid fa-pen-to-square"></i> Editar Ubicación Existente`;
                addressFormContainer.classList.add('active');
                addressFormContainer.scrollIntoView({ behavior: 'smooth' });
            };
        });

        // Evento Eliminar
        document.querySelectorAll('.btn-address-delete-inline').forEach(btn => {
            btn.onclick = function(e) {
                e.preventDefault();
                if (confirm("🗑️ ¿Estás seguro de que deseas eliminar esta dirección de despacho?")) {
                    const card = btn.closest('.operational-address-block');
                    card.remove();
                }
            };
        });
    }

    // Inicializar eventos de direcciones por primera vez
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

    const btnSaveOperational = document.querySelector('.btn-save-operational-changes');
    if (btnSaveOperational) {
        btnSaveOperational.addEventListener('click', () => {
            alert("💼 Datos Generales de la Empresa sincronizados correctamente.");
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

window.mostrarManualTecnico = function() {
    alert("📚 Descarga iniciada: Carpeta de Manuales Técnicos y Diagramas Ecodren 2026.");
};

window.confirmDeleteAccount = function() {
    if (confirm("🚨 ALERTA CRÍTICA: ¿Estás seguro de querer dar de baja esta cuenta? Se perderán todos tus pedimentos logísticos.")) {
        alert("Solicitud de desactivación enviada a revisión con el administrador de Equipos MC.");
    }
};