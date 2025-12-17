
class MessageManager {
  constructor() {
    this.messageMap = new Map();
    this.clearDelay = 3000;
  }

  showMessage(message, type = "info", options = {}) {
    const key = `${type}`;
    if (this.messageMap.has(key)) return;

    this.messageMap.set(key, true);
    const instance = ElMessage({
      message,
      type,
      ...options,
    });

    setTimeout(() => {
      this.messageMap.delete(key);
    }, this.clearDelay);

    return instance;
  }

  success(message, options = {}) {
    return this.showMessage(message, "success", options);
  }

  error(message, options = {}) {
    return this.showMessage(message, "error", options);
  }

  warning(message, options = {}) {
    return this.showMessage(message, "warning", options);
  }

  info(message, options = {}) {
    return this.showMessage(message, "info", options);
  }
}

export const message = new MessageManager();
export default message;
