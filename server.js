const express = require('express');
const http = require('http');
const { WebSocketServer } = require('ws');
const app = express();
app.use(express.static('.'));
app.get('/health', (_req, res) => res.json({ ok: true, service: 'sanew-stars-server' }));
const server = http.createServer(app);
const wss = new WebSocketServer({ server, path: '/play' });
const rooms = new Map();
wss.on('connection', (socket) => {
  const id = Math.random().toString(36).slice(2, 9);
  socket.playerId = id;
  socket.room = 'arena';
  if (!rooms.has(socket.room)) rooms.set(socket.room, new Map());
  const room = rooms.get(socket.room);
  room.set(id, { id, x: 200 + Math.random() * 300, y: 160 + Math.random() * 220, name: 'Боец' });
  socket.send(JSON.stringify({ type: 'welcome', id, players: [...room.values()] }));
  socket.on('message', (raw) => {
    let data;
    try { data = JSON.parse(raw.toString()); } catch { return; }
    if (data.type === 'move' && Number.isFinite(data.x) && Number.isFinite(data.y)) {
      const p = room.get(id);
      if (!p) return;
      p.x = Math.max(0, Math.min(3000, data.x));
      p.y = Math.max(0, Math.min(3000, data.y));
      p.name = typeof data.name === 'string' ? data.name.slice(0, 18) : 'Боец';
    }
    if (data.type === 'attack') {
      for (const peer of wss.clients) if (peer.readyState === 1 && peer !== socket && peer.room === socket.room) peer.send(JSON.stringify({ type: 'effect', playerId: id, effect: 'attack' }));
    }
  });
  socket.on('close', () => {
    room.delete(id);
    for (const peer of wss.clients) if (peer.readyState === 1 && peer.room === socket.room) peer.send(JSON.stringify({ type: 'leave', id }));
    if (!room.size) rooms.delete(socket.room);
  });
});
setInterval(() => {
  for (const [roomName, players] of rooms) {
    const payload = JSON.stringify({ type: 'state', players: [...players.values()] });
    for (const peer of wss.clients) if (peer.readyState === 1 && peer.room === roomName) peer.send(payload);
  }
}, 50);
const port = process.env.PORT || 3000;
server.listen(port, '0.0.0.0', () => console.log('Sanew Stars server on ' + port));