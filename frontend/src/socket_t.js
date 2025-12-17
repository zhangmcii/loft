import { io } from "socket.io-client";

/**
 * ⚠️ 改这里
 * 如果你 nginx 转发的是 4290：
 *   https://xxx.com  或 http://127.0.0.1:4290
 * 如果你直接暴露 docker 5001：
 *   http://127.0.0.1:5001
 */
// const SOCKET_URL = "https://106.53.219.192:4289";
const SOCKET_URL = "https://191718.com";

const token =
  "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NTg4MTY3NSwianRpIjoiZDAxNzdhYTMtOWM1Yi00NzYxLThlNDAtOTdlMDY0MDlkZjMzIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MTAwLCJuYmYiOjE3NjU4ODE2NzUsImNzcmYiOiJmZDU3Yzk4Yi0zMmNiLTRiNWQtOWEyZC04NzBiY2I0ZjMwZmMifQ.pJoR-aHLeToIUKFY4IBheu2Vg1A1zABSib9VPCbOJOg";

const socket = io(SOCKET_URL, {
  path: "/socket.io",
  query: { token: token },
  transports: ["websocket"],
  withCredentials: true,
  reconnectionAttempts: 5,
  reconnectionDelay: 5000,
  pingTimeout: 30000,
  pingInterval: 60000,
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
