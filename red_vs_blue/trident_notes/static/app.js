document.addEventListener("DOMContentLoaded", () => {
  const textarea = document.querySelector("textarea[name='body']");
  const submit = document.querySelector(".comment-form button");

  textarea?.addEventListener("input", () => {
    submit.disabled = textarea.value.trim().length === 0;
  });
});
