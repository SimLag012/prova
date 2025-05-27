let lastData = null;

function fetchUpdates() {
    fetch('/lobby/_info')
        .then(response => response.json())
        .then(data => {
            if (JSON.stringify(data) !== JSON.stringify(lastData)) {
                // Aggiorna la lista delle stanze senza ricaricare tutta la pagina
                updateLobby(data.rooms);
            }
            lastData = data;
        })
        .catch(() => {});
}

function updateLobby(rooms) {
    const ul = document.querySelector('ul');
    ul.innerHTML = '';
    if (Object.keys(rooms).length === 0) {
        ul.innerHTML = '<li>Nessuna stanza disponibile</li>';
    } else {
        for (const [room_id, room] of Object.entries(rooms)) {
            ul.innerHTML += `<li>ID: ${room_id} | Host: ${room.host_id} | Stato: ${room.status} | Giocatori: ${room.players.join(', ')}</li>`;
        }
    }
}

if (window.location.pathname === '/lobby') {
    setInterval(fetchUpdates, 3000);
}

function fetchRoomUpdates() {
    // Prende l'id stanza dalla url
    const match = window.location.pathname.match(/\/room\/([A-Z0-9]+)/);
    if (!match) return;
    const roomId = match[1];
    fetch(`/room/${roomId}/_info`)
        .then(response => response.json())
        .then(data => {
            if (JSON.stringify(data) !== JSON.stringify(lastData)) {
                window.location.reload();
            }
            lastData = data;
        })
        .catch(() => {});
}

if (window.location.pathname.startsWith('/room/')) {
    setInterval(fetchRoomUpdates, 3000);
}