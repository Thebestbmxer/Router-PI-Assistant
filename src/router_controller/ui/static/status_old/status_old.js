async function updateStatus() {
    try {
        const response = await fetch(
            "/api/router/status",
            {
                cache: "no-store"
            }
        );

        const data = await response.json();
        updateConnectionState(data);

    } catch (error) {

        updateConnectionState({
            connected: false,
            message: "Unable to contact the Router PI."
        });

    }
}
function updateConnectionState(data) {
    const indicator = document.getElementById("connection-indicator");
    const connectionText = document.getElementById("connection-text");
    const icon = document.getElementById("ssh-status-icon");
    const status = document.getElementById("ssh-status");
    const message = document.getElementById("ssh-message");

    if (data.connected) {
        indicator.classList.add("connected");
        indicator.classList.remove("disconnected");

        connectionText.textContent = "ONLINE";

        icon.classList.add("connected");
        icon.classList.remove("disconnected");

        icon.textContent = "✓";

        status.textContent = "Connected";

        message.textContent =
            "The Raspberry Pi is authenticated to the router using SSH.";

    } else {
        indicator.classList.remove("connected");
        indicator.classList.add("disconnected");

        connectionText.textContent = "OFFLINE";

        icon.classList.remove("connected");
        icon.classList.add("disconnected");

        icon.textContent = "×";

        status.textContent = "Disconnected";

        message.textContent =
            data.message || "The router SSH connection is unavailable.";
    }

    setText(
        "router-address",
        data.address
    );

    setText(
        "router-port",
        data.ssh_port
    );

    setText(
        "router-mac",
        data.mac_address
    );

    setText(
        "router-firmware",
        data.firmware
    );
}

function setText(id, value) {
    const element = document.getElementById(id);

    if (!element) return;

    element.textContent =
        value === null ||
            value === undefined ||
            value === ""
            ? "—"
            : value;
}

updateStatus();

setInterval(
    updateStatus,
    5000
);
