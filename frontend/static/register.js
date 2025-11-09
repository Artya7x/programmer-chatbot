document.getElementById("register-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("username").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirm-password").value;

    const errorMsg = document.getElementById("error-msg");
    const successMsg = document.getElementById("success-msg");

    errorMsg.textContent = "";
    successMsg.textContent = "";

    if (password !== confirmPassword) {
        errorMsg.textContent = "Passwords do not match.";
        return;
    }

    try {
        const response = await fetch("/api/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, email, password })
        });

        // Read raw text first
        const responseText = await response.text();
        console.log("Raw server response:", responseText);

        // Try to parse JSON safely
        let data;
        try {
            data = JSON.parse(responseText);
        } catch {
            data = { detail: responseText };
        }

        if (!response.ok) {
            throw new Error(data.detail || "Registration failed.");
        }

        successMsg.textContent = "Registration successful! Redirecting...";
        setTimeout(() => (window.location.href = "/login"), 1000);

    } catch (err) {
        console.error("Error during register:", err);
        errorMsg.textContent = err.message;
    }

});