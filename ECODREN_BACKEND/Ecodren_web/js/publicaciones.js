document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const categoriaUrl = urlParams.get('categoria') || 'todos';

    function filtrarPublicaciones(categoria) {
        document.querySelectorAll('.filter-tab').forEach(tab => {
            if (tab.getAttribute('data-category') === categoria) {
                tab.classList.add('active');
            } else {
                tab.classList.remove('active');
            }
        });

        const tarjetas = document.querySelectorAll('.bento-card');
        tarjetas.forEach(tarjeta => {
            const categoriaTarjeta = tarjeta.getAttribute('data-category');
            if (categoria === 'todos' || categoriaTarjeta === categoria) {
                tarjeta.style.display = '';
            } else {
                tarjeta.style.display = 'none';
            }
        });
    }

    filtrarPublicaciones(categoriaUrl);

    document.querySelectorAll('.filter-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            const cat = tab.getAttribute('data-category');
            filtrarPublicaciones(cat);
            window.history.pushState({}, '', `publicaciones.html?categoria=${cat}`);
        });
    });
});