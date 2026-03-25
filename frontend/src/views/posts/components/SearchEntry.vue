<template>
  <div class="search-entry">
    <div class="search-inline-entry" @click="openSearch">
      <div class="entry-copy">
        <span class="entry-title">搜索文章</span>
        <span class="entry-hint">按标题、正文或作者关键词查找</span>
      </div>
      <span class="entry-action">进入</span>
    </div>
  </div>
</template>

<script>
export default {
  name: "SearchEntry",
  methods: {
    openSearch() {
      this.$router.push("/posts/search");
    },
  },
};
</script>

<style lang="scss" scoped>
@use "./PostReadingTokens.scss" as tokens;

.search-entry {
  position: relative;
  margin-bottom: 18px;
}

.search-inline-entry {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  min-height: 50px;
  padding: 0 0 14px;
  border-bottom: 1px solid tokens.$reading-border;
  background: #fff;
  cursor: pointer;
  transition: border-color 0.2s ease, color 0.2s ease;

  &:hover {
    border-color: tokens.$reading-border-strong;

    .entry-title,
    .entry-action {
      color: tokens.$reading-text-primary;
    }
  }
}

.entry-copy {
  display: flex;
  align-items: baseline;
  gap: 14px;
  min-width: 0;
  flex: 1 1 auto;
}

.entry-title {
  font-size: 15px;
  font-weight: 500;
  letter-spacing: 0.01em;
  color: tokens.$reading-text-primary;
  white-space: nowrap;
}

.entry-hint {
  font-size: 12px;
  line-height: 1.6;
  letter-spacing: 0.01em;
  color: tokens.$reading-text-tertiary;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.entry-action {
  flex-shrink: 0;
  font-size: 13px;
  font-weight: 500;
  color: tokens.$reading-text-secondary;
  line-height: 1.2;
  text-decoration: underline;
  text-decoration-color: transparent;
  text-underline-offset: 3px;
  transition: color 0.2s ease, text-decoration-color 0.2s ease;

  .search-inline-entry:hover & {
    text-decoration-color: tokens.$reading-border;
  }
}

@media (max-width: 768px) {
  .search-entry {
    margin-bottom: 16px;
  }

  .search-inline-entry {
    min-height: auto;
    align-items: flex-start;
    padding: 0 0 12px;
    gap: 12px;
  }

  .entry-copy {
    flex-direction: column;
    align-items: flex-start;
    gap: 2px;
  }

  .entry-hint {
    white-space: normal;
    overflow: visible;
    text-overflow: clip;
  }
}
</style>
