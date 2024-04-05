document.addEventListener('DOMContentLoaded', function() {
    const propop = document.querySelector('.pfp');
    const prodisplay = document.querySelector('.propop');
    propop.addEventListener('click', () => {
        if (prodisplay.style.display == 'none') {
            prodisplay.style.display = 'flex';
        }
        else {
            prodisplay.style.display = 'none';
        }
    });
})