document.addEventListener('DOMContentLoaded', function () {
    const terminalContainer = document.getElementById('terminal');
    if (!terminalContainer) {
        console.log("Terminal container not found, skipping initialization.");
        return;
    }

    const term = new Terminal({
        cursorBlink: true,
        theme: {
            background: '#000000',
            foreground: '#00ff00',
        }
    });

    // Check if a WebSocket connection for the terminal is already open
    // This is a simple check; a more robust solution might involve a global registry
    if (!window.terminalSocket || window.terminalSocket.readyState === WebSocket.CLOSED) {
        const socket = new WebSocket('ws://' + window.location.host + '/ws/terminal');

        term.open(terminalContainer);

        socket.onopen = function(event) {
            console.log("Terminal WebSocket connection established.");
            term.write('Welcome to the AGI Force Terminal!\n\r');
        };

        socket.onmessage = function(event) {
            term.write(event.data);
        };

        socket.onerror = function(error) {
            console.error("Terminal WebSocket error:", error);
            term.write('\n\r\u001b[31mConnection error. Please check the server.\u001b[0m\n\r');
        };

        socket.onclose = function(event) {
            console.log("Terminal WebSocket connection closed.");
            term.write('\n\r\u001b[33mConnection closed.\u001b[0m\n\r');
        };

        term.onData(data => {
            if (socket.readyState === WebSocket.OPEN) {
                socket.send(data);
            }
        });

        window.terminalSocket = socket;
    } else {
        console.log("Terminal WebSocket connection already exists.");
        // If you want to re-attach to an existing terminal, you would need more complex logic here.
        // For now, we just log it.
    }
});