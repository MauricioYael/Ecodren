document.addEventListener('DOMContentLoaded', () => {
    const btnTabExperiencia = document.querySelector(".cap-tab-btn[onclick*='experiencia']");
    const btnTabDisponibles = document.querySelector(".cap-tab-btn[onclick*='disponibles']");

    const colExperiencia = document.getElementById("sec-experiencia");
    const colDisponibles = document.getElementById("sec-disponibles");
    const secDiploma = document.getElementById("sec-diploma");
    const mainContainer = document.querySelector(".cap-main-container");

    const btnVerTodosExp = document.querySelector(".cap-col-experience .cap-view-all");
    const btnVerTodosCursos = document.querySelector(".cap-all-courses-footer .cap-link-all-courses");

    function esMovil() {
        return window.innerWidth <= 768;
    }

    function resetearFiltrosVista() {
        document.querySelectorAll('.cap-tab-btn').forEach(btn => btn.classList.remove('active'));
        
        if (colExperiencia) colExperiencia.style.display = 'block';
        if (colDisponibles) colDisponibles.style.display = 'block';
        if (secDiploma) secDiploma.style.display = 'block';

        if (mainContainer) {
            mainContainer.style.gridTemplateColumns = esMovil() ? '1fr' : '1.1fr 0.9fr';
        }
    }

    window.switchCapTab = function(tabName, btnElement) {
        resetearFiltrosVista();

        if (btnElement) {
            document.querySelectorAll('.cap-tab-btn').forEach(b => b.classList.remove('active'));
            btnElement.classList.add('active');
        }

        if (tabName === 'experiencia') {
            if (colDisponibles) colDisponibles.style.display = 'none';
            if (mainContainer) mainContainer.style.gridTemplateColumns = '1fr';
            if (colExperiencia) colExperiencia.scrollIntoView({ behavior: 'smooth', block: 'start' });

        } else if (tabName === 'disponibles') {
            if (colExperiencia) colExperiencia.style.display = 'none';
            if (mainContainer) mainContainer.style.gridTemplateColumns = '1fr';
            if (colDisponibles) colDisponibles.scrollIntoView({ behavior: 'smooth', block: 'start' });

        } else if (tabName === 'diploma') {
            if (secDiploma) {
                secDiploma.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
    };

    if (btnVerTodosExp) {
        btnVerTodosExp.addEventListener('click', (e) => {
            e.preventDefault();
            switchCapTab('experiencia', btnTabExperiencia);
        });
    }

    if (btnVerTodosCursos) {
        btnVerTodosCursos.addEventListener('click', (e) => {
            e.preventDefault();
            switchCapTab('disponibles', btnTabDisponibles);
        });
    }

    const prevArrow = document.querySelector('.cap-carousel-arrow.prev-arrow');
    const nextArrow = document.querySelector('.cap-carousel-arrow.next-arrow');
    const cardsTrack = document.querySelector('.cap-cards-track');

    if (cardsTrack && prevArrow && nextArrow) {
        nextArrow.addEventListener('click', () => {
            cardsTrack.scrollBy({ left: 280, behavior: 'smooth' });
        });

        prevArrow.addEventListener('click', () => {
            cardsTrack.scrollBy({ left: -280, behavior: 'smooth' });
        });
    }

    let calendarInstance = null;

    window.abrirModalCalendario = function (e) {
    if (e) e.preventDefault();
    const modal = document.getElementById('modalCalendarioOverlay');
    if (!modal) return;

    modal.style.display = 'flex';

    if (!calendarInstance) {
        const calendarEl = document.getElementById('calendar-container');
        if (calendarEl && typeof FullCalendar !== 'undefined') {
            calendarInstance = new FullCalendar.Calendar(calendarEl, {
                initialView: 'dayGridMonth',
                locale: 'es',
                headerToolbar: {
                    left: 'prev,next today',
                    center: 'title',
                    right: 'dayGridMonth,listMonth'
                },
                buttonText: {
                    today: 'Hoy',
                    month: 'Mes',
                    list: 'Lista'
                },
                events: '/api/calendario-cursos/',
                eventColor: '#0f5429',
                eventTextColor: '#bffd00',
                eventClick: function (info) {
                    const props = info.event.extendedProps;
                    if (confirm(`📘 ${info.event.title}\n⏱ Duración: ${props.duracion}\n💰 Costo: ${props.precio}\n\n¿Deseas agregar este curso al carrito?`)) {
                        if (typeof agregarAlCarrito === 'function') {
                            agregarAlCarrito(info.event.id, info.event.title, props.precio, props.img);
                            cerrarModalCalendario();
                        }
                    }
                }
            });
            calendarInstance.render();
        }
    } else {
        calendarInstance.refetchEvents();
    }

    // Ajusta el tamaño de la cuadrícula al mostrar el modal
    setTimeout(() => {
        if (calendarInstance) calendarInstance.updateSize();
    }, 50);
};

    window.cerrarModalCalendario = function () {
        const modal = document.getElementById('modalCalendarioOverlay');
        if (modal) modal.style.display = 'none';
    };

    const modalOverlay = document.getElementById('modalCalendarioOverlay');
    if (modalOverlay) {
        modalOverlay.addEventListener('click', function (e) {
            if (e.target === this) {
                cerrarModalCalendario();
            }
        });
    }

    document.addEventListener('click', function (e) {
        const btn = e.target.closest('.btn-inscribir-curso');
        if (btn) {
            e.preventDefault();
            const d = btn.dataset;
            if (typeof agregarAlCarrito === 'function') {
                agregarAlCarrito(d.id, d.titulo, d.precio, d.img);
            }
        }
    });
});