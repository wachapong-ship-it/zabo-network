// =========================
// Navigation
// =========================

function showSection(id) {

    document.querySelectorAll('section').forEach(sec => {
        sec.classList.add('hidden');
    });

    if (id === 'login' || id === 'register') {
        document.getElementById('auth').classList.remove('hidden');

        document.getElementById('login').classList.add('hidden');
        document.getElementById('register').classList.add('hidden');

        document.getElementById(id).classList.remove('hidden');
    }

    if (id === 'marketplace') {
        document.getElementById('marketplace-section').classList.remove('hidden');
        loadProducts();
    }

    if (id === 'transport') {
        document.getElementById('transport-section').classList.remove('hidden');
        loadTransports();
    }
}


// =========================
// Register
// =========================

async function registerUser() {

    try {

        const data = {
            username: document.getElementById('reg-username').value.trim(),
            email: document.getElementById('reg-email').value.trim(),
            password: document.getElementById('reg-password').value,
            role: document.getElementById('reg-role').value
        };

        const res = await fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await res.json();

        alert(result.message || result.error);

    } catch (err) {

        console.error(err);
        alert("Registration failed");

    }
}


// =========================
// Login
// =========================

async function loginUser() {

    try {

        const data = {
            username: document.getElementById('login-username').value.trim(),
            password: document.getElementById('login-password').value
        };

        const res = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await res.json();

       if (res.ok) {
    alert("Login Successful");

    loadProfile();

    showSection('marketplace');
}

         else {

            alert(result.error || "Login Failed");

        }

    } catch (err) {

        console.error(err);
        alert("Login failed");

    }
}


// =========================
// Load Products
// =========================

async function loadProducts() {

    try {

        const res = await fetch('/api/products');

        const products = await res.json();

        const container =
            document.getElementById('product-cards');

        if (!container) return;

        container.innerHTML = '';

        products.forEach(product => {

            const card =
                document.createElement('div');

            card.className =
                'product-card';

            const image =
                product.image
                    ? `/static/uploads/${product.image}`
                    : 'https://via.placeholder.com/400x250';

            card.innerHTML = `
                <img src="${image}" alt="${product.name}">

                <div class="product-content">

                    <h3>${product.name}</h3>

                    <div class="product-price">
                        ₹${product.price}
                    </div>

                    <div>
                        📦 Stock: ${product.quantity}
                    </div>

                    <div class="product-location">
                        📍 ${product.location || "Nagaland"}
                    </div>

                    <div class="product-buttons">

                        <button class="buy-btn">
                            View Details
                        </button>

                        <button class="save-btn">
                            ❤️ Save
                        </button>

                    </div>

                </div>
            `;

            container.appendChild(card);

        });

    } catch (err) {

        console.error(err);

    }
}


// =========================
// Create Product
// =========================

async function createProduct() {

    try {

        const formData = new FormData();

        formData.append(
            'name',
            document.getElementById('prod-name').value
        );

        formData.append(
            'category',
            document.getElementById('prod-cat').value
        );

        formData.append(
            'price',
            document.getElementById('prod-price').value
        );

        formData.append(
            'quantity',
            document.getElementById('prod-qty').value
        );

        formData.append(
            'location',
            document.getElementById('prod-location').value
        );

        formData.append(
            'description',
            document.getElementById('prod-desc').value
        );

        const image =
            document.getElementById('prod-image').files[0];

        if (image) {
            formData.append('image', image);
        }

        const res = await fetch('/api/products', {
            method: 'POST',
            body: formData
        });

        const result = await res.json();

        alert(result.message || result.error);

        loadProducts();

    } catch (err) {

        console.error(err);
        alert("Failed creating product");

    }
}


// =========================
// Load Transports
// =========================

async function loadTransports() {

    try {

        const res = await fetch('/api/transports');

        const transports = await res.json();

        const ul =
            document.getElementById('transports-ul');

        if (!ul) return;

        ul.innerHTML = '';

        transports.forEach(t => {

            const li =
                document.createElement('li');

            li.textContent =
                `${t.vehicle} from ${t.current_location} to ${t.destination}`;

            ul.appendChild(li);

        });

    } catch (err) {

        console.error(err);

    }
}


// =========================
// Create Transport
// =========================

async function createTransport() {

    try {

        const data = {
            vehicle: document.getElementById('trans-vehicle').value,
            capacity: document.getElementById('trans-cap').value,
            current_location: document.getElementById('trans-from').value,
            destination: document.getElementById('trans-to').value,
            available_date: document.getElementById('trans-date').value
        };

        const res = await fetch('/api/transports', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await res.json();

        alert(result.message || result.error);

        loadTransports();

    } catch (err) {

        console.error(err);
        alert("Transport creation failed");

    }
}


// =========================
// Logout
// =========================

async function logout() {

    try {

        await fetch('/api/logout', {
            method: 'POST'
        });

        alert('Logged Out');

        showSection('login');

    } catch (err) {

        console.error(err);

    }
}


// =========================
// Startup
// =========================

document.addEventListener('DOMContentLoaded', function () {

    const registerBtn =
        document.getElementById('register-btn');

    if (registerBtn) {
        registerBtn.addEventListener(
            'click',
            registerUser
        );
    }

    const loginBtn =
        document.getElementById('login-btn');

    if (loginBtn) {
        loginBtn.addEventListener(
            'click',
            loginUser
        );
    }

    const productBtn =
        document.getElementById('create-prod-btn');

    if (productBtn) {
        productBtn.addEventListener(
            'click',
            createProduct
        );
    }

    const transportBtn =
        document.getElementById('create-trans-btn');

    if (transportBtn) {
        transportBtn.addEventListener(
            'click',
            createTransport
        );
    }

    showSection('login');

});
async function loadProfile() {

    try {

        const res =
            await fetch('/api/current-user');

        const user =
            await res.json();

        if (user.logged_in) {

            document.getElementById(
                'profile-name'
            ).textContent = user.username;

            document.getElementById(
                'profile-role'
            ).textContent = user.role;
        }

    } catch(err) {

        console.log(err);

    }

}