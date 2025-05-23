/**
 * Displays a toast notification.
 * @param {string} message The message to display.
 * @param {boolean} [isError=false] Whether the toast indicates an error.
 * @param {number} [duration=3000] How long the toast should be visible in milliseconds.
 */
function showGlobalToast(message, isError = false, duration = 3000) {
    const existingToast = document.getElementById('globalToast');
    if (existingToast) {
        existingToast.remove();
    }

    const toast = document.createElement('div');
    toast.id = 'globalToast';
    toast.className = `fixed bottom-5 right-5 text-white py-3 px-5 rounded-lg shadow-xl text-sm z-50 transition-all duration-300 ease-in-out transform translate-y-10 opacity-0`;
    
    if (isError) {
        toast.classList.add('bg-red-600');
    } else {
        toast.classList.add('bg-green-600');
    }
    
    const messageParagraph = document.createElement('p');
    messageParagraph.textContent = message;
    toast.appendChild(messageParagraph);
    
    document.body.appendChild(toast);

    // Animate in
    setTimeout(() => {
        toast.classList.remove('translate-y-10', 'opacity-0');
        toast.classList.add('translate-y-0', 'opacity-100');
    }, 10); // Small delay to allow CSS transition to apply

    // Animate out and remove
    setTimeout(() => {
        toast.classList.add('opacity-0', 'translate-y-10');
        setTimeout(() => {
            toast.remove();
        }, 300); // Allow fade out animation
    }, duration);
}
