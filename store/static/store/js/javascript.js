// javascript.js

// Function load specific module
function loadPageModule(scriptPath) {
    import(scriptPath)
        .then(module => {
            console.log(`Loaded script: ${scriptPath}`); 
            if (module.initPage) {
                console.log(`Initializing script: ${scriptPath}`); 
                module.initPage();
            }
        })
        .catch(err => console.error("Error loading the page module:", err));
}

(() => {
    const path = window.location.pathname;
    console.log(`Current path: ${path}`); 

    switch (true) {
        case path === '/profile/' || path === '/profile.html': 
            loadPageModule('/static/store/js/profile.js');
            break;
        case /\/category\/.*\/product\/\d+/.test(path):
            loadPageModule('/static/store/js/product_view.js');
            break;
        case path === '/cart/' || path === '/cart.html':
            loadPageModule('/static/store/js/cart.js');
            break;
        case path === '/checkout/' || path === '/checkout.html':
            loadPageModule('/static/store/js/checkout.js');
            break;
        // Add more page if need it
        default:
            console.log('No specific page script to load.');
    }
})();





