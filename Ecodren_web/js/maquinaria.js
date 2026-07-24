const MAQUINARIA = [
    {
        id: "Ecodren-17",
        nombre: "Ecodren 17",
        tagline: "Equipos de alto rendimiento diseñado para trabajos de limpieza y succión industrial en cualquier condición.",
        precioBase: 2450000,
        imagenes: [
            "Assets/ecodren-17/Ecodren ED-17.webp",
            "Assets/ecodren-17/Ecodren ED-17 v2.webp",
            "Assets/ecodren-17/Ecodren ED-17 v3.webp"
        ]
    },
    {
        id: "Ecodren-15",
        nombre: "Ecodren 15",
        tagline: "Configuración robusta optimizada para operaciones intensivas y alta productividad municipal.",
        precioBase: 2100000,
        imagenes: [
            "Assets/ecodren-15/Ecodren ED-15.webp",
            "Assets/ecodren-15/Ecodren ED-15 v2.webp",
            "Assets/ecodren-15/Ecodren ED-15 v3.webp"
        ]
    }
];

const PRECIOS_OPCIONES = {
    accesorios: {
        "boquilla-estandar": 15000,
        "boquilla-premium": 45000
    },
    mangueras: {
        "manguera-34": 12000,
        "manguera-1": 28000
    },
    bombas: {
        "bomba-estandar": 0,
        "bomba-industrial": 75000
    },
    chasis: {
        "chasis-4x2": -50000,
        "chasis-6x4": 0,
        "chasis-hd": 85000
    },
    extras: {
        "led": 12000,
        "gps": 8500,
        "camara": 18000
    }
};

let configActual = {
    maquinaIndex: 0,
    fotoIndex: 0,
    chasis: "chasis-6x4",
    accesorio: "",
    manguera: "",
    bomba: "",
    extras: []
};

window.nextVariant = function() {
    configActual.maquinaIndex = (configActual.maquinaIndex + 1) % MAQUINARIA.length;
    configActual.fotoIndex = 0;
    renderMaquina();
};

window.prevVariant = function() {
    configActual.maquinaIndex = (configActual.maquinaIndex - 1 + MAQUINARIA.length) % MAQUINARIA.length;
    configActual.fotoIndex = 0;
    renderMaquina();
};

window.cambiarFotoInterna = function(direccion) {
    const fotosDelModelo = MAQUINARIA[configActual.maquinaIndex].imagenes;
    configActual.fotoIndex = (configActual.fotoIndex + direccion + fotosDelModelo.length) % fotosDelModelo.length;
    actualizarSoloFotoYIndicadores();
};

window.irAFotoInterna = function(index) {
    configActual.fotoIndex = index;
    actualizarSoloFotoYIndicadores();
};

window.renderMaquina = function() {
    const maquina = MAQUINARIA[configActual.maquinaIndex];
    const nameHeading = document.getElementById('current-machine-name');
    if (nameHeading) nameHeading.innerText = maquina.nombre;
    
    const taglineParagraph = document.querySelector('.machine-tagline-radical');
    if (taglineParagraph && maquina.tagline) taglineParagraph.innerText = maquina.tagline;

    actualizarSoloFotoYIndicadores();
    actualizarPrecioDinamico();
    
    const activeTabBtn = document.querySelector('.radical-tab-btn.active');
    if (activeTabBtn) {
        window.cambiarTab(activeTabBtn);
    }
};

function actualizarSoloFotoYIndicadores() {
    const maquina = MAQUINARIA[configActual.maquinaIndex];
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

function actualizarPrecioDinamico() {
    const maquina = MAQUINARIA[configActual.maquinaIndex];
    let total = maquina.precioBase;

    if (configActual.accesorio) {
        total += PRECIOS_OPCIONES.accesorios[configActual.accesorio] || 0;
    }
    if (configActual.manguera) {
        total += PRECIOS_OPCIONES.mangueras[configActual.manguera] || 0;
    }
    if (configActual.bomba) {
        total += PRECIOS_OPCIONES.bombas[configActual.bomba] || 0;
    }
    
    total += PRECIOS_OPCIONES.chasis[configActual.chasis] || 0;

    configActual.extras.forEach(extra => {
        total += PRECIOS_OPCIONES.extras[extra] || 0;
    });

    const priceDisplay = document.getElementById('dynamicMachinePrice');
    if (priceDisplay) {
        priceDisplay.innerText = `$${total.toLocaleString('es-MX')} MXN`;
    }
}

function renderAccesorios() {
    const container = document.getElementById('tab-accesorios');
    if (!container) return;

    const textoBoquilla = configActual.accesorio === 'boquilla-premium' ? 'Modelo BPT-3 (Premium)' : 'Modelo BPT-1 (Estándar)';
    const descBoquilla = configActual.accesorio === 'boquilla-premium' 
        ? 'Diseño avanzado con chorros de penetración frontal para desobstrucción severa.' 
        : 'Diseño hidrodinámico para limpieza general de arrastre.';
    const iconBoquilla = configActual.accesorio === 'boquilla-premium' ? 'fa-bolt' : 'fa-satellite-dish';

    const textoManguera = configActual.manguera === 'manguera-1' ? 'Manguera Hidrojet 1"' : 'Manguera Hidrojet 3/4"';
    const descManguera = configActual.manguera === 'manguera-1'
        ? 'Máximo flujo volumétrico para arrastre pesado de lodos densos.'
        : 'Alta resistencia con trenzado de seguridad reforzado para alta presión.';

    const textoBomba = configActual.bomba === 'bomba-industrial' ? 'Bomba Industrial 80 GPM' : 'Bomba Estándar 50 GPM';
    const descBomba = configActual.bomba === 'bomba-industrial' ? 'Alta presión para desazolve pesado.' : 'Flujo óptimo municipal.';

    container.innerHTML = `
        <div class="radical-dropdown-selector-group">
            <label class="radical-selector-label">Selección de boquillas</label>
            <div class="custom-premium-dropdown-wrapper">
                <div class="custom-dropdown-trigger" id="trigger-boquillas" onclick="toggleCustomDropdown('dropdown-boquillas', 'trigger-boquillas')">
                    <span id="label-boquillas">${configActual.accesorio ? textoBoquilla : 'Selecciona una opción...'}</span>
                    <i class="fa-solid fa-chevron-down custom-arrow"></i>
                </div>
                <div class="custom-dropdown-options-list" id="dropdown-boquillas">
                    <div class="custom-dropdown-option" onclick="selectCustomOption('boquilla-estandar', 'Modelo BPT-1 (Estándar)', 'boquillas', 'trigger-boquillas')">
                        Modelo BPT-1 (Estándar)
                    </div>
                    <div class="custom-dropdown-option" onclick="selectCustomOption('boquilla-premium', 'Modelo BPT-3 (Premium)', 'boquillas', 'trigger-boquillas')">
                        Modelo BPT-3 (Premium)
                    </div>
                </div>
            </div>
            <div class="radical-selector-desc-card ${configActual.accesorio ? '' : 'hidden-card'}" id="card-desc-boquillas">
                <div class="desc-card-icon"><i class="fa-solid ${iconBoquilla}" id="icon-boquillas"></i></div>
                <div class="desc-card-text">
                    <strong id="title-desc-boquillas">${textoBoquilla}</strong>
                    <p id="text-desc-boquillas">${descBoquilla}</p>
                </div>
            </div>
        </div>

        <div class="radical-dropdown-selector-group">
            <label class="radical-selector-label">Selección de mangueras</label>
            <div class="custom-premium-dropdown-wrapper">
                <div class="custom-dropdown-trigger" id="trigger-mangueras" onclick="toggleCustomDropdown('dropdown-mangueras', 'trigger-mangueras')">
                    <span id="label-mangueras">${configActual.manguera ? textoManguera : 'Selecciona una opción...'}</span>
                    <i class="fa-solid fa-chevron-down custom-arrow"></i>
                </div>
                <div class="custom-dropdown-options-list" id="dropdown-mangueras">
                    <div class="custom-dropdown-option" onclick="selectCustomOption('manguera-34', 'Manguera Hidrojet 3/4', 'mangueras', 'trigger-mangueras')">
                        Manguera Hidrojet 3/4"
                    </div>
                    <div class="custom-dropdown-option" onclick="selectCustomOption('manguera-1', 'Manguera Hidrojet 1', 'mangueras', 'trigger-mangueras')">
                        Manguera Hidrojet 1"
                    </div>
                </div>
            </div>
            <div class="radical-selector-desc-card ${configActual.manguera ? '' : 'hidden-card'}" id="card-desc-mangueras">
                <div class="desc-card-icon"><i class="fa-solid fa-gear"></i></div>
                <div class="desc-card-text">
                    <strong id="title-desc-mangueras">${textoManguera}</strong>
                    <p id="text-desc-mangueras">${descManguera}</p>
                </div>
            </div>
        </div>

        <div class="radical-dropdown-selector-group">
            <label class="radical-selector-label">Selección de bombas</label>
            <div class="custom-premium-dropdown-wrapper">
                <div class="custom-dropdown-trigger" id="trigger-bombas" onclick="toggleCustomDropdown('dropdown-bombas', 'trigger-bombas')">
                    <span id="label-bombas">${configActual.bomba ? textoBomba : 'Selecciona una opción...'}</span>
                    <i class="fa-solid fa-chevron-down custom-arrow"></i>
                </div>
                <div class="custom-dropdown-options-list" id="dropdown-bombas">
                    <div class="custom-dropdown-option" onclick="selectCustomOption('bomba-estandar', 'Bomba Estándar 50 GPM', 'bombas', 'trigger-bombas')">
                        Bomba Estándar 50 GPM
                    </div>
                    <div class="custom-dropdown-option" onclick="selectCustomOption('bomba-industrial', 'Bomba Industrial 80 GPM', 'bombas', 'trigger-bombas')">
                        Bomba Industrial 80 GPM
                    </div>
                </div>
            </div>
            <div class="radical-selector-desc-card ${configActual.bomba ? '' : 'hidden-card'}" id="card-desc-bombas">
                <div class="desc-card-icon"><i class="fa-solid fa-water"></i></div>
                <div class="desc-card-text">
                    <strong id="title-desc-bombas">${textoBomba}</strong>
                    <p id="text-desc-bombas">${descBomba}</p>
                </div>
            </div>
        </div>
    `;
}

window.toggleCustomDropdown = function(id, triggerId) {
    document.querySelectorAll('.custom-dropdown-options-list').forEach(el => {
        if(el.id !== id) el.classList.remove('open');
    });
    document.querySelectorAll('.custom-dropdown-trigger').forEach(el => {
        if(el.id !== triggerId) el.classList.remove('menu-active');
    });

    const targetMenu = document.getElementById(id);
    const targetTrigger = document.getElementById(triggerId);
    
    if (targetMenu && targetTrigger) {
        targetMenu.classList.toggle('open');
        targetTrigger.classList.toggle('menu-active');
    }
};

window.selectCustomOption = function(valor, texto, tipo, triggerId) {
    if (tipo === 'boquillas') {
        configActual.accesorio = valor;
        const triggerLabel = document.getElementById('label-boquillas');
        if (triggerLabel) triggerLabel.innerText = texto;
        
        const descTitle = document.getElementById('title-desc-boquillas');
        const descText = document.getElementById('text-desc-boquillas');
        const descIcon = document.getElementById('icon-boquillas');
        const cardBoquilla = document.getElementById('card-desc-boquillas');
        
        if (cardBoquilla) cardBoquilla.classList.remove('hidden-card');
        
        if (valor === 'boquilla-premium') {
            if (descTitle) descTitle.innerText = 'Modelo BPT-3 (Premium)';
            if (descText) descText.innerText = 'Diseño advanced con chorros de penetración frontal para desobstrucción severa.';
            if (descIcon) descIcon.className = 'fa-solid fa-bolt';
        } else {
            if (descTitle) descTitle.innerText = 'Modelo BPT-1 (Estándar)';
            if (descText) descText.innerText = 'Diseño hidrodinámico para limpieza general de arrastre.';
            if (descIcon) descIcon.className = 'fa-solid fa-satellite-dish';
        }
    } else if (tipo === 'mangueras') {
        configActual.manguera = valor;
        const triggerLabel = document.getElementById('label-mangueras');
        if (triggerLabel) triggerLabel.innerText = texto;

        const descTitle = document.getElementById('title-desc-mangueras');
        const descText = document.getElementById('text-desc-mangueras');
        const cardManguera = document.getElementById('card-desc-mangueras');
        
        if (cardManguera) cardManguera.classList.remove('hidden-card');
        
        if (valor === 'manguera-1') {
            if (descTitle) descTitle.innerText = 'Manguera Hidrojet 1"';
            if (descText) descText.innerText = 'Máximo flujo volumétrico para arrastre pesado de lodos densos.';
        } else {
            if (descTitle) descTitle.innerText = 'Manguera Hidrojet 3/4"';
            if (descText) descText.innerText = 'Alta resistencia con trenzado de seguridad reforzado para alta presión.';
        }
    } else if (tipo === 'bombas') {
        configActual.bomba = valor;
        const triggerLabel = document.getElementById('label-bombas');
        if (triggerLabel) triggerLabel.innerText = texto;

        const descTitle = document.getElementById('title-desc-bombas');
        const descText = document.getElementById('text-desc-bombas');
        const cardBomba = document.getElementById('card-desc-bombas');
        
        if (cardBomba) cardBomba.classList.remove('hidden-card');
        
        if (valor === 'bomba-industrial') {
            if (descTitle) descTitle.innerText = 'Bomba Industrial 80 GPM';
            if (descText) descText.innerText = 'Alta presión para desazolve pesado.';
        } else {
            if (descTitle) descTitle.innerText = 'Bomba Estándar 50 GPM';
            if (descText) descText.innerText = 'Flujo óptimo municipal.';
        }
    }
    
    actualizarPrecioDinamico();
    
    const menu = document.getElementById(triggerId.replace('trigger-', 'dropdown-'));
    const trigger = document.getElementById(triggerId);
    if (menu) menu.classList.remove('open');
    if (trigger) trigger.classList.remove('menu-active');
};

window.cambiarTabChasis = function(radioBtn) {
    configActual.chasis = radioBtn.value;
    
    // Remueve el brillo de todas las tarjetas y se lo agrega únicamente a la seleccionada
    document.querySelectorAll('.radical-chasis-selectable-card').forEach(card => {
        card.classList.remove('active-chasis-card');
    });
    radioBtn.closest('.radical-chasis-selectable-card').classList.add('active-chasis-card');
    
    actualizarPrecioDinamico();
};

window.cambiarTabExtra = function(checkboxBtn, extraName) {
    if (checkboxBtn.checked) {
        if (!configActual.extras.includes(extraName)) configActual.extras.push(extraName);
        checkboxBtn.closest('.radical-option-selectable-card').classList.add('active-option-card');
    } else {
        configActual.extras = configActual.extras.filter(e => e !== extraName);
        checkboxBtn.closest('.radical-option-selectable-card').classList.remove('active-option-card');
    }
    actualizarPrecioDinamico();
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
    
    const opcionesData = [
        { id: 'led', nombre: 'Luces LED' },
        { id: 'gps', nombre: 'Sistema GPS' },
        { id: 'camara', nombre: 'Cámara 360°' }
    ];

    let html = `<h3>Opciones Adicionales</h3>`;
    opcionesData.forEach(opt => {
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
                </div>
            </label>
        `;
    });
    container.innerHTML = html;
}

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
    }
};

document.addEventListener('click', function(e) {
    if (!e.target.closest('.custom-premium-dropdown-wrapper')) {
        document.querySelectorAll('.custom-dropdown-options-list').forEach(el => el.classList.remove('open'));
        document.querySelectorAll('.custom-dropdown-trigger').forEach(el => el.classList.remove('menu-active'));
    }
});

document.addEventListener('DOMContentLoaded', () => {
    renderAccesorios();
    actualizarSoloFotoYIndicadores();
    actualizarPrecioDinamico();
});