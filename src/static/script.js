document.addEventListener('DOMContentLoaded', () => {
    const sections = document.querySelectorAll('.section');
    let currentSection = 0;

    window.addEventListener('wheel', (event) => {
        if (event.deltaY < 0) {
            // Scrolling up
            if (currentSection > 0) {
                currentSection--;
            }
        } else {
            // Scrolling down
            if (currentSection < sections.length - 1) {
                currentSection++;
            }
        }
        sections[currentSection].scrollIntoView({ behavior: 'smooth' });
    });
});
