let configActual = {
    maquinaIndex: 0,
    fotoIndex: 0,
    chasis: "chasis-6x4",
    equipamentos: [],
    extras: []
};

window.cambiarFotoInterna = function(direccion) {
    if (!window.MAQUINARIA || !window.MAQUINARIA[configActual.maquinaIndex]) return;
    const fotosDelModelo = window.MAQUINARIA[configActual.maquinaIndex].imagenes || [];
    if (fotosDelModelo.length === 0) return;
    configActual.fotoIndex = (configActual.fotoIndex + direccion + fotosDelModelo.length) % fotosDelModelo.length;
    actualizarSoloFotoYIndicadores();
};

window.irAFotoInterna = function(index) {
    configActual.fotoIndex = index;
    actualizarSoloFotoYIndicadores();
};

window.renderMaquina = function() {
    if (!window.MAQUINARIA || window.MAQUINARIA.length === 0 || !window.MAQUINARIA[configActual.maquinaIndex]) return;
    const maquina = window.MAQUINARIA[configActual.maquinaIndex];
    
    const nameHeading = document.getElementById('current-machine-name');
    if (nameHeading) nameHeading.innerText = maquina.nombre;
    
    const taglineParagraph = document.querySelector('.machine-tagline-radical');
    if (taglineParagraph && maquina.tagline) taglineParagraph.innerText = maquina.tagline;

    const elCap = document.getElementById('strip-capacidad');
    if (elCap) elCap.innerText = maquina.capacidad || 'N/A';

    const elPres = document.getElementById('strip-presion');
    if (elPres) elPres.innerText = maquina.presion || 'N/A';

    const elSuc = document.getElementById('strip-succion');
    if (elSuc) elSuc.innerText = maquina.succion || 'Alto vacío';

    const elPeso = document.getElementById('strip-peso');
    if (elPeso) elPeso.innerText = maquina.peso || 'N/A';

    const elTipo = document.getElementById('strip-tipo');
    if (elTipo) elTipo.innerText = maquina.tipo_trabajo || 'Industrial';

    actualizarSoloFotoYIndicadores();
    
    const activeTabBtn = document.querySelector('.radical-tab-btn.active');
    if (activeTabBtn) {
        window.cambiarTab(activeTabBtn);
    }
};

function actualizarSoloFotoYIndicadores() {
    if (!window.MAQUINARIA || window.MAQUINARIA.length === 0 || !window.MAQUINARIA[configActual.maquinaIndex]) return;
    const maquina = window.MAQUINARIA[configActual.maquinaIndex];
    if (!maquina.imagenes || maquina.imagenes.length === 0) return;

    const imgElement = document.getElementById('mainMachineImage');
    if (imgElement) {
        imgElement.src = maquina.imagenes[configActual.fotoIndex];
    }
    const barras = document.querySelectorAll('.radical-slider-indicators .indicator-bar');
    barras.forEach((barra, index) => {
        if (index === configActual.fotoIndex) barra.classList.add('active');
        else barra.classList.remove('active');
    });
}

window.toggleEquipamento = function(checkbox, nombre) {
    if (!configActual.equipamentos) configActual.equipamentos = [];
    
    if (checkbox.checked) {
        if (!configActual.equipamentos.includes(nombre)) configActual.equipamentos.push(nombre);
        checkbox.closest('.radical-option-selectable-card').classList.add('active-option-card');
    } else {
        configActual.equipamentos = configActual.equipamentos.filter(e => e !== nombre);
        checkbox.closest('.radical-option-selectable-card').classList.remove('active-option-card');
    }
};

function renderAccesorios() {
    const container = document.getElementById('tab-accesorios');
    if (!container) return;

    if (!window.MAQUINARIA || window.MAQUINARIA.length === 0 || !window.MAQUINARIA[configActual.maquinaIndex]) {
        container.innerHTML = `<p style="color: #aaa; padding: 1.5rem;">No hay información disponible.</p>`;
        return;
    }

    const maquinaActual = window.MAQUINARIA[configActual.maquinaIndex];
    const equipamientos = maquinaActual.equipamento || [];

    if (equipamientos.length === 0) {
        container.innerHTML = `<p style="color: #aaa; padding: 1.5rem; text-align: center;">No hay equipamiento registrado en la base de datos para este modelo.</p>`;
        return;
    }

    let html = `<h3 style="margin-bottom: 1rem; font-size: 1.1rem; color: #fff;">Equipamiento Seleccionable</h3>`;
    equipamientos.forEach(item => {
        const isChecked = configActual.equipamentos.includes(item.nombre);
        const activeClass = isChecked ? 'active-option-card' : '';
        const checkedAttr = isChecked ? 'checked' : '';

        html += `
            <label class="radical-option-selectable-card ${activeClass}" style="margin-bottom: 0.75rem; display: flex; align-items: center; gap: 1rem; cursor: pointer;">
                <input type="checkbox" ${checkedAttr} onchange="toggleEquipamento(this, '${item.nombre}')" style="display: none;">
                <div class="option-card-indicator-box">
                    <i class="fa-solid fa-check"></i>
                </div>
                <div class="desc-card-icon" style="font-size: 1.2rem; color: var(--eco-green, #88ff00); width: 35px; text-align: center;">
                    <i class="fa-solid ${item.icono || 'fa-screwdriver-wrench'}"></i>
                </div>
                <div class="option-card-text-content" style="flex: 1;">
                    <strong style="display: block; font-size: 0.95rem; color: #fff;">${item.nombre}</strong>
                    <p style="margin: 0; font-size: 0.8rem; color: #aaa;">${item.especificacion}</p>
                </div>
            </label>
        `;
    });
    container.innerHTML = html;
}

window.cambiarTabChasis = function(radioBtn) {
    configActual.chasis = radioBtn.value;
    document.querySelectorAll('.radical-chasis-selectable-card').forEach(card => {
        card.classList.remove('active-chasis-card');
    });
    radioBtn.closest('.radical-chasis-selectable-card').classList.add('active-chasis-card');
};

window.cambiarTabExtra = function(checkboxBtn, extraName) {
    if (checkboxBtn.checked) {
        if (!configActual.extras.includes(extraName)) configActual.extras.push(extraName);
        checkboxBtn.closest('.radical-option-selectable-card').classList.add('active-option-card');
    } else {
        configActual.extras = configActual.extras.filter(e => e !== extraName);
        checkboxBtn.closest('.radical-option-selectable-card').classList.remove('active-option-card');
    }
};

function renderComponentes() {
    const container = document.getElementById('tab-componentes');
    if (!container) return;
    const chasis = [
        {id: "chasis-4x2", nombre: "Chasis Corto (4x2)", desc: "Ideal para maniobras urbanas."},
        {id: "chasis-6x4", nombre: "Chasis Estándar (6x4)", desc: "Balance perfecto entre estabilidad y capacidad."},
        {id: "chasis-hd", nombre: "Chasis Heavy Duty", desc: "Para terrenos difíciles."}
    ];

    let html = `<h3>Selección de Chasis</h3>`;
    chasis.forEach(c => {
        const isActive = configActual.chasis === c.id ? 'active-chasis-card' : '';
        const checked = configActual.chasis === c.id ? 'checked' : '';
        html += `
            <label class="radical-chasis-selectable-card ${isActive}">
                <input type="radio" name="chasis" value="${c.id}" ${checked} onchange="cambiarTabChasis(this)">
                <div class="chasis-card-indicator-dot"></div>
                <div class="chasis-card-text-content">
                    <strong>${c.nombre}</strong>
                    <p>${c.desc}</p>
                </div>
            </label>
        `;
    });
    container.innerHTML = html;
}

function renderOpciones() {
    const container = document.getElementById('tab-opciones');
    if (!container) return;

    let html = `<h3>Accesorios Adicionales</h3>`;

    if (!window.MAQUINARIA || window.MAQUINARIA.length === 0 || !window.MAQUINARIA[configActual.maquinaIndex]) {
        container.innerHTML = html + `<p style="color: #aaa; padding: 1.5rem;">No hay información disponible.</p>`;
        return;
    }

    const maquinaActual = window.MAQUINARIA[configActual.maquinaIndex];
    const accesoriosDb = maquinaActual.accesorios || [];

    if (accesoriosDb.length === 0) {
        container.innerHTML = html + `<p style="color: #aaa; padding: 1.5rem;">No hay accesorios adicionales registrados en la base de datos para este equipo.</p>`;
        return;
    }

    accesoriosDb.forEach(opt => {
        const isChecked = configActual.extras.includes(opt.id);
        const activeClass = isChecked ? 'active-option-card' : '';
        const checkedAttr = isChecked ? 'checked' : '';
        
        html += `
            <label class="radical-option-selectable-card ${activeClass}">
                <input type="checkbox" ${checkedAttr} onchange="cambiarTabExtra(this, '${opt.id}')">
                <div class="option-card-indicator-box">
                    <i class="fa-solid fa-check"></i>
                </div>
                <div class="option-card-text-content">
                    <strong>${opt.nombre}</strong>
                    ${opt.descripcion ? `<p>${opt.descripcion}</p>` : ''}
                </div>
            </label>
        `;
    });
    container.innerHTML = html;
}

function renderModelos() {
    const container = document.getElementById('tab-modelos');
    if (!container || !window.MAQUINARIA) return;

    let html = `<h3 class="tab-models-title">Modelos disponibles</h3>`;

    window.MAQUINARIA.forEach((maq, index) => {
        const isActive = (configActual.maquinaIndex === index) ? 'active-model-card' : '';
        
        html += `
            <div class="radical-model-selectable-card ${isActive}" onclick="seleccionarModelo(${index})">
                <div class="model-card-main-info">
                    <div class="model-card-header-row">
                        <strong>${maq.nombre}</strong>
                        ${maq.recomendado ? '<span class="model-badge-recommended">Recomendado</span>' : ''}
                    </div>
                    <p>Capacidad: ${maq.capacidad} &nbsp;|&nbsp; Presión: ${maq.presion}</p>
                </div>
                <div class="model-card-indicator-circle">
                    <i class="fa-solid fa-check"></i>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

window.seleccionarModelo = function(index) {
    configActual.maquinaIndex = index;
    configActual.fotoIndex = 0;
    renderMaquina();
};

window.cambiarTab = function(btn) {
    const tabName = btn.dataset.tab;
    
    document.querySelectorAll('.radical-tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.radical-tab-pane').forEach(p => p.classList.remove('active'));
    
    btn.classList.add('active');
    const target = document.getElementById(`tab-${tabName}`);
    if (target) target.classList.add('active');

    if (tabName === 'accesorios') {
        renderAccesorios();
    } else if (tabName === 'componentes') {
        renderComponentes();
    } else if (tabName === 'opciones') {
        renderOpciones();
    } else if (tabName === 'modelos') {
        renderModelos();
    }
};

window.activarEcodren = function() {
    const ecodrenCard = document.querySelector('.top-category-card[data-machine="ecodren"]');
    if (ecodrenCard) ecodrenCard.click();
};

document.addEventListener('DOMContentLoaded', () => {
    if (window.MAQUINARIA && window.MAQUINARIA.length > 0) {
        renderMaquina();
    } else {
        renderAccesorios();
    }

    const categoryCard = document.querySelectorAll('.top-category-card');
    const configuratorView = document.getElementById('configurator-main-view');
    const constructionView = document.getElementById('under-construction-view');
    const constructionTitle = document.getElementById('construction-category-title');

    categoryCard.forEach(card => {
        card.addEventListener('click', () => {
            const selectedCategory = card.getAttribute('data-machine');

            categoryCard.forEach(c => c.classList.remove('active'));
            card.classList.add('active');

            if (selectedCategory === 'ecodren') {
                if (configuratorView) configuratorView.style.display = 'contents';
                if (constructionView) constructionView.style.display = 'none';
            } else {
                if (configuratorView) configuratorView.style.display = 'none';
                if (constructionView) constructionView.style.display = 'flex';

                const nombres = {
                    ecojet: 'Línea Ecojet',
                    ecovac: 'Línea Ecovac',
                    ecoclean: 'Línea Ecoclean'
                };
                if (constructionTitle) {
                    constructionTitle.textContent = `${nombres[selectedCategory] || 'Línea'} — En Construcción`;
                }
            }
        });
    });
});