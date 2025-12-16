import { io }  from "socket.io-client";

/**
 * ⚠️ 改这里
 * 如果你 nginx 转发的是 4290：
 *   https://xxx.com  或 http://127.0.0.1:4290
 * 如果你直接暴露 docker 5001：
 *   http://127.0.0.1:5001
 */
// const SOCKET_URL = "https://106.53.219.192:4289";
const SOCKET_URL = "https://191718.com";

const token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NTg5NTI0MSwianRpIjoiZmFlMGU4NWYtYmQ4My00MTQ1LTliYjktZTk3YjU2MzgwYjE5IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6OTksIm5iZiI6MTc2NTg5NTI0MSwiY3NyZiI6ImY1Mzg4ODkyLWI1MjAtNDMwOC1iYjA0LTRhNjZmZTk3ZTA4ZSJ9.IdxfikDQQ7j8vYodQhHtDlBuntScJkOlCPlfTogwmuE"

const socket = io(SOCKET_URL, {
  path: "/socket.io",
  transports: ["websocket"], // 强制 websocket，绕过 polling
  timeout: 5000,
  reconnectionAttempts: 3,
  auth: { Authorization: token },
  query: { token: token },
});

socket.on("connect", () => {
  console.log("✅ 已连接 Socket.IO");
  console.log("socket.id =", socket.id);
});

socket.on("connect_error", (err) => {
  console.error("❌ 连接失败");
  console.error("原因:", err.message);
});

socket.on("disconnect", (reason) => {
  console.warn("⚠️ 断开连接:", reason);
});

/**
 * 如果你后端有推送 new_notification
 */
socket.on("new_notification", (data) => {
  console.log("📩 收到推送:", data);
});
