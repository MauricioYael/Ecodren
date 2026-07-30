document.addEventListener('DOMContentLoaded', () => {
 
    const filterTabs = document.querySelectorAll('.filter-tab');
    const secVideos   = document.getElementById('sec-videos');
    const secNoticias = document.getElementById('sec-noticias');
 
    const secciones = {
        todos:    [secVideos, secNoticias],
        videos:   [secVideos],
        noticias: [secNoticias],
        guias:    []          
    };
 
    filterTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            filterTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
 
            const filtro = tab.dataset.filter;
 
            if (filtro === 'guias') {
                document.querySelector('.resources-download-cta-section')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                // Abre el modal automáticamente al presionar la pestaña
                document.getElementById('modal-guias-docs')?.classList.add('open');
                return;
            }
 
            [secVideos, secNoticias].forEach(sec => {
                if (!sec) return;
                const mostrar = filtro === 'todos' || secciones[filtro]?.includes(sec);
                sec.style.display = mostrar ? '' : 'none';
            });
        });
    });
 
    const searchInput = document.querySelector('.resources-search-wrapper input');
    if (searchInput) {
        let debounceTimer;
        searchInput.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                const query = searchInput.value.trim().toLowerCase();
                buscarEnRecursos(query);
            }, 280);
        });
    }
 
    function buscarEnRecursos(query) {
        if (!query) {
            document.querySelectorAll('.radical-resource-card').forEach(card => {
                card.closest('[data-hidden-by-search]')?.removeAttribute('data-hidden-by-search');
                card.style.display = '';
            });
            return;
        }
        document.querySelectorAll('.radical-resource-card').forEach(card => {
            const texto = card.textContent.toLowerCase();
            card.style.display = texto.includes(query) ? '' : 'none';
        });
    }
 
    const sortSelect = document.querySelector('.filter-select-sort');
    if (sortSelect) {
        sortSelect.addEventListener('change', () => {
            console.log('[Recursos] Ordenar por:', sortSelect.value);
        });
    }
 
    const btnDocs = document.querySelector('.btn-go-to-docs');
    const modalGuias = document.getElementById('modal-guias-docs');
    const closeGuiasBtn = document.getElementById('close-guias-modal');

    if (btnDocs && modalGuias) {
        btnDocs.addEventListener('click', (e) => {
            e.preventDefault();
            modalGuias.classList.add('open');
        });
    }

    // Cerrar modal con la (X)
    if (closeGuiasBtn && modalGuias) {
        closeGuiasBtn.addEventListener('click', () => {
            modalGuias.classList.remove('open');
        });
    }

    // Cerrar modal haciendo clic afuera
    if (modalGuias) {
        modalGuias.addEventListener('click', (e) => {
            if (e.target === modalGuias) {
                modalGuias.classList.remove('open');
            }
        });
    }
 
    document.querySelectorAll('.btn-resource-card-action').forEach(btn => {
        btn.addEventListener('click', e => {
            e.stopPropagation();
            showToast('Próximamente disponible.', 'info');
        });
    });
 
});
const memoriaScrollCarrusel = {};

// Inicializa las barritas dinámicamente según la cantidad de tarjetas reales
function inicializarPillsIndicadoras(gridId, indicatorsId) {
    const grid = document.getElementById(gridId);
    const container = document.getElementById(indicatorsId);
    if (!grid || !container) return;

    const tarjetas = grid.querySelectorAll('.radical-resource-card');
    container.innerHTML = ''; // Limpiamos

    tarjetas.forEach((_, index) => {
        const bar = document.createElement('span');
        bar.className = `indicator-bar${index === 0 ? ' active' : ''}`;
        container.appendChild(bar);
    });

    // Vinculamos el evento scroll nativo para que las barritas reaccionen en tiempo real si el usuario arrastra o usa flechas
    grid.addEventListener('scroll', () => {
        const tarjeta = grid.querySelector('.radical-resource-card');
        if (!tarjeta) return;
        
        const anchoTarjeta = tarjeta.offsetWidth + 24;
        // Calculamos en qué índice de tarjeta está parado el carrusel actualmente
        const indiceActivo = Math.round(grid.scrollLeft / anchoTarjeta);
        
        const bars = container.querySelectorAll('.indicator-bar');
        bars.forEach((bar, idx) => {
            if (idx === indiceActivo) {
                bar.classList.add('active');
            } else {
                bar.classList.remove('active');
            }
        });
    });
}

function ejecutarScrollCarrusel(gridId, direccion) {
    const grid = document.getElementById(gridId);
    if (!grid) return;

    const tarjeta = grid.querySelector('.radical-resource-card');
    const distanciaScroll = tarjeta ? tarjeta.offsetWidth + 24 : 300; 

    if (direccion === 'derecha') {
        const posicionActual = grid.scrollLeft;
        const posicionAnterior = memoriaScrollCarrusel[gridId] || 0;
        const maxScrollLeft = grid.scrollWidth - grid.clientWidth;

        if (posicionActual >= maxScrollLeft - 5 || (posicionActual === posicionAnterior && posicionActual > 0)) {
            grid.scrollTo({ left: 0, behavior: 'smooth' });
            memoriaScrollCarrusel[gridId] = 0;
        } else {
            memoriaScrollCarrusel[gridId] = posicionActual;
            grid.scrollBy({ left: distanciaScroll, behavior: 'smooth' });
        }
    } else {
        if (grid.scrollLeft <= 5) {
            grid.scrollTo({ left: grid.scrollWidth, behavior: 'smooth' });
        } else {
            grid.scrollBy({ left: -distanciaScroll, behavior: 'smooth' });
        }
        setTimeout(() => { memoriaScrollCarrusel[gridId] = grid.scrollLeft; }, 350);
    }
}

// Inicialización de las barritas al cargar la página
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        inicializarPillsIndicadoras('videos-carousel-grid', 'indicators-videos');
        inicializarPillsIndicadoras('noticias-carousel-grid', 'indicators-noticias');
    }, 200);
});

// Asignación de ventanas globales para los botones HTML
window.scrollVideoDerecha = () => ejecutarScrollCarrusel('videos-carousel-grid', 'derecha');
window.scrollVideoIzquierda = () => ejecutarScrollCarrusel('videos-carousel-grid', 'izquierda');
window.scrollNoticiasDerecha = () => ejecutarScrollCarrusel('noticias-carousel-grid', 'derecha');
window.scrollNoticiasIzquierda = () => ejecutarScrollCarrusel('noticias-carousel-grid', 'izquierda');

window.scrollNoticiasDerecha = function() {
    const grid = document.getElementById('noticias-carousel-grid');
    if (grid) {
        const tarjeta = grid.querySelector('.radical-resource-card');
        // Sumamos el ancho exacto del contenedor de la tarjeta + 24px del gap flex dinámico
        const distanciaScroll = tarjeta ? tarjeta.offsetWidth + 24 : 300;
        
        grid.scrollBy({
            left: distanciaScroll,
            behavior: 'smooth'
        });
    }
};

