document.addEventListener('DOMContentLoaded', () => {
    // Target forms that should persist their data (e.g., specific class)
    // For NISBadges, we want this to apply broadly to data-entry forms
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        // Skip login form for security reasons
        if (form.action.includes('login')) return;

        const formId = form.id || form.className || 'default-form';
        const basePath = window.location.pathname;
        
        // 1. Restore Data
        const inputs = form.querySelectorAll('input:not([type="file"]):not([type="hidden"]), select, textarea');
        
        inputs.forEach(input => {
            if (!input.name) return; // Need a name to serve as a key

            const storageKey = `${basePath}_${formId}_${input.name}`;
            const savedValue = sessionStorage.getItem(storageKey);

            if (savedValue !== null) {
                if (input.type === 'checkbox' || input.type === 'radio') {
                    input.checked = (savedValue === 'true');
                } else {
                    input.value = savedValue;
                }
            }

            // 2. Save Data on Input/Change
            const saveEvent = (input.tagName === 'SELECT' || input.type === 'checkbox' || input.type === 'radio') ? 'change' : 'input';
            
            input.addEventListener(saveEvent, () => {
                const valueToSave = (input.type === 'checkbox' || input.type === 'radio') ? input.checked : input.value;
                sessionStorage.setItem(storageKey, valueToSave);
            });
        });

        // 3. Clear Storage on Successful Submit
        form.addEventListener('submit', () => {
             inputs.forEach(input => {
                 if (!input.name) return;
                 const storageKey = `${basePath}_${formId}_${input.name}`;
                 sessionStorage.removeItem(storageKey);
             });
        });
    });
});
