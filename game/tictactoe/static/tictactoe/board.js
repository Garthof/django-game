function show_status_message(message) {
    const status_area = document.getElementById("status_area");
    const status_message = document.getElementById("status_message");

    status_area.removeAttribute("hidden");
    status_message.innerText = message;
}

function hide_status_message() {
    const status_area = document.getElementById("status_area");
    const status_message = document.getElementById("status_message");

    status_area.setAttribute("hidden", "true");
    status_message.innerText = "";
}

document.body.addEventListener("htmx:afterRequest", (event) => {
    if (event.detail.failed) {
        if (event.detail.xhr) {
            show_status_message(event.detail.xhr.responseText);
        } else {
            console.error("Unexpected HTMX error", evt.detail);
            show_status_message("Unexpected error, check your connection and try to refresh the page.");
        }

        window.setTimeout(hide_status_message, 5000);
    }
})