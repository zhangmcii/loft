import { defineStore } from "pinia";

const MAX_HISTORY = 8;

export const useSearchHistoryStore = defineStore("searchHistory", {
  state: () => ({
    items: {},
  }),
  actions: {
    getUserKey(userId) {
      return String(userId || "guest");
    },
    getHistory(userId) {
      return this.items[this.getUserKey(userId)] || [];
    },
    addHistory(userId, keyword) {
      const normalized = String(keyword || "").trim();
      if (!normalized) return;
      const key = this.getUserKey(userId);
      const current = this.items[key] || [];
      const next = [
        normalized,
        ...current.filter(
          (item) => item.toLowerCase() !== normalized.toLowerCase()
        ),
      ].slice(0, MAX_HISTORY);
      this.items[key] = next;
    },
    clearHistory(userId) {
      delete this.items[this.getUserKey(userId)];
    },
  },
  persist: {
    key: "postSearchHistory",
    storage: localStorage,
  },
});
