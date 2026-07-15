const form = document.querySelector("#login-form");
const errorBox = document.querySelector("#error-box");

form?.addEventListener("submit", async (event) => {
  event.preventDefault();
  errorBox.textContent = "";

  const button = form.querySelector("button");
  button.disabled = true;
  button.textContent = "Verifica in corso...";

  try {
    const response = await fetch(window.LOGIN_API_URL, {
      method: "POST",
      body: new FormData(form)
    });

    const data = await response.json();

    if (!response.ok || !data.ok) {
      errorBox.textContent = data.message || "Accesso negato.";
      return;
    }

    window.location.href = data.redirect;
  } catch {
    errorBox.textContent = "Servizio temporaneamente non disponibile.";
  } finally {
    button.disabled = false;
    button.innerHTML = 'Accedi al sistema <span>→</span>';
  }
});
