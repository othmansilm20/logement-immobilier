document.addEventListener("DOMContentLoaded", function () {
    const loader = document.getElementById("siteLoader");

    if (loader) {
        window.setTimeout(function () {
            loader.classList.add("hidden");
        }, 1100);
    }

    const header = document.getElementById("dropdownHeader");
    const list = document.getElementById("dropdownList");
    const selectedText = document.getElementById("selectedOption");
    const hiddenInput = document.getElementById("userType");
    const registerRole = document.getElementById("registerRole");

    const extraOptions = document.getElementById("extraOptions");
    const registerLink = document.getElementById("registerLink");

    if (!header || !list || !selectedText || !hiddenInput) {
        console.log("Erreur : éléments du dropdown introuvables");
        return;
    }

    header.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        list.classList.toggle("active");
    });

    const items = list.querySelectorAll("li");

    items.forEach(function (item) {
        item.addEventListener("click", function (e) {
            e.preventDefault();
            e.stopPropagation();

            const value = item.getAttribute("data-value");

            selectedText.textContent = item.textContent;
            hiddenInput.value = value;
            if (registerRole) registerRole.value = value;

            list.classList.remove("active");

            handleRoleChange(value);
        });
    });

    document.addEventListener("click", function () {
        list.classList.remove("active");
    });

    const EMAIL_SUGGESTIONS = {
        visiteur: "youssef@example.com",
        proprietaire: "karim@example.com",
        admin: "admin@example.com",
    };

    function handleRoleChange(role) {
        if (role === "admin") {
            if (extraOptions) extraOptions.style.display = "none";
            if (registerLink) registerLink.style.display = "none";
        } else {
            if (extraOptions) extraOptions.style.display = "flex";
            if (registerLink) registerLink.style.display = "block";
        }

        const usernameInput = document.getElementById("username");
        if (usernameInput && EMAIL_SUGGESTIONS[role]) {
            usernameInput.placeholder = EMAIL_SUGGESTIONS[role];
        }
    }

    if (registerRole) registerRole.value = hiddenInput.value;
    handleRoleChange(hiddenInput.value);

    const demoButtons = document.querySelectorAll(".demo-fill-btn");
    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");

    demoButtons.forEach(function (btn) {
        btn.addEventListener("click", function () {
            const role = btn.getAttribute("data-role");
            const email = btn.getAttribute("data-email");
            const password = btn.getAttribute("data-password");

            if (usernameInput) usernameInput.value = email;
            if (passwordInput) passwordInput.value = password;

            const item = list.querySelector('li[data-value="' + role + '"]');
            if (item) {
                selectedText.textContent = item.textContent;
                hiddenInput.value = role;
                if (registerRole) registerRole.value = role;
                handleRoleChange(role);
            }
        });
    });
});
const loginForm = document.getElementById("loginForm");
const registerForm = document.getElementById("registerForm");

const showRegister = document.getElementById("showRegister");
const showLogin = document.getElementById("showLogin");

if (showRegister) {
    showRegister.addEventListener("click", function (e) {
        e.preventDefault();

        const hiddenInput = document.getElementById("userType");
        const registerRole = document.getElementById("registerRole");
        if (hiddenInput && registerRole) registerRole.value = hiddenInput.value;

        loginForm.style.display = "none";
        registerForm.style.display = "block";
    });
}

if (showLogin) {
    showLogin.addEventListener("click", function (e) {
        e.preventDefault();

        registerForm.style.display = "none";
        loginForm.style.display = "block";
    });
}
