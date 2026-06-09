// For v 2.5.0
function scrollToInput() {
    const input = document.getElementById("chat_input");
    if (input) {
        input.scrollIntoView({ behavior: "smooth", block: "center" });
        input.focus();
    }
}

function createFloatingScrollButton() {
    const existing = document.getElementById('floating-scroll-btn');
    if (existing) existing.remove();

    const wrapper = document.createElement('div');
    wrapper.id = 'floating-scroll-btn';

    const btnUp = document.createElement('button');
    btnUp.id = 'scroll-up-btn';
    btnUp.innerHTML = '↑';
    //btnUp.onclick = () => window.scrollTo({ top: 0, behavior: 'smooth' });
	btnUp.onclick = () => window.scrollBy({ top: -(window.innerHeight * 0.95), behavior: 'smooth' });

    const btnDown = document.createElement('button');
    btnDown.id = 'scroll-down-btn';
    btnDown.innerHTML = '↓';
    //btnDown.onclick = scrollToInput;
	btnDown.onclick = () => window.scrollBy({ top: window.innerHeight * 0.95, behavior: 'smooth' });

    wrapper.appendChild(btnUp);
    wrapper.appendChild(btnDown);
    document.body.appendChild(wrapper);
}

function updateScrollButtonVisibility() {
    const btn = document.getElementById('floating-scroll-btn');
    if (!btn) return;
    const input = document.getElementById("chat_input");
    if (!input) return;
    const rect = input.getBoundingClientRect();
    const visible = rect.top < window.innerHeight && rect.bottom > 0 && rect.bottom < window.innerHeight - 70;
    btn.classList.toggle('hidden', visible);
}

window.addEventListener('load', () => {
    setTimeout(() => {
        createFloatingScrollButton();
        window.addEventListener('scroll', updateScrollButtonVisibility, { passive: true });
        window.addEventListener('resize', updateScrollButtonVisibility);
        const chatBox = document.getElementById('chat_box');
        if (chatBox) {
            const observer = new MutationObserver(addCopyButtons);
            observer.observe(chatBox, { childList: true, subtree: true });
            addCopyButtons();
        }
    }, 800);
});