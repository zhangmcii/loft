import { defineStore } from "pinia";

export const useComposeDraftStore = defineStore("composeDraft", {
  state: () => ({
    drafts: {},
  }),
  actions: {
    getNewDraftKey(userId, mode) {
      return `new:${userId}:${mode}`;
    },
    getEditDraftKey(userId, postId) {
      return `edit:${userId}:${postId}`;
    },
    getDraft(key) {
      return this.drafts[key] || null;
    },
    saveDraft(key, payload) {
      this.drafts[key] = payload;
    },
    removeDraft(key) {
      delete this.drafts[key];
    },
    clearUserDrafts(userId) {
      const prefix = `:${userId}:`;
      Object.keys(this.drafts).forEach((key) => {
        if (key.includes(prefix)) {
          delete this.drafts[key];
        }
      });
    },
  },
  persist: {
    key: "composeDraft",
    storage: localStorage,
  },
});
