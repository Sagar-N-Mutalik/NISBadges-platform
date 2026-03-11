/*
 * NISBadges — Fixed floating Save button for list_editable admin pages.
 *
 * Strategy: find the native Django "_save" submit input at the bottom of the
 * changelist form, create a floating clone at the top-right, and on click
 * simply trigger .click() on the native button — the most reliable cross-
 * browser way to submit a form with the correct button name/value.
 */
(function () {
    'use strict';

    function injectFloatingSave() {
        // Only run on pages that have the list_editable save button
        var nativeSave = document.querySelector('#changelist-form input[name="_save"]');
        if (!nativeSave) return;

        // Already injected (e.g. Turbo-style navigation)
        if (document.getElementById('floating-save-bar')) return;

        var btn = document.createElement('button');
        btn.id = 'floating-save-bar';
        btn.type = 'button';   // type=button prevents accidental double submission
        btn.innerHTML = '&#x1F4BE;&nbsp; Save Changes';

        btn.addEventListener('click', function () {
            // Trigger the native save button — preserves Django's form submission flow
            nativeSave.click();
        });

        document.body.appendChild(btn);
    }

    // Run after full DOM parse
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', injectFloatingSave);
    } else {
        injectFloatingSave();   // already parsed
    }
})();
