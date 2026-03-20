<template>
  <div class="publish-entry">
    <div class="publish-inline-entry" @click="openCompose">
      <div class="entry-copy">
        <span class="entry-title">写点什么</span>
        <span class="entry-hint">开始写作</span>
      </div>
      <span class="entry-action">→</span>
    </div>
  </div>
</template>

<script>
export default {
  name: "PublishEntry",
  methods: {
    openCompose() {
      this.$router.push("/compose");
    },
  },
};
</script>

<style lang="scss" scoped>
.publish-entry {
  position: relative;
  margin-bottom: 18px;
}

.publish-inline-entry {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  min-height: 46px;
  padding: 0 16px;
  border: 1px solid #e3e3e3;
  border-radius: 10px;
  background: #fff;
  cursor: pointer;
  transition: border-color 0.2s ease, background-color 0.2s ease;

  &:hover {
    border-color: #111;
    background: #fafafa;
  }

  .entry-copy {
    display: flex;
    align-items: baseline;
    gap: 10px;
    min-width: 0;
  }

  .entry-title {
    font-size: 14px;
    font-weight: 500;
    letter-spacing: 0.01em;
    color: #111;
  }

  .entry-hint {
    font-size: 12px;
    line-height: 1;
    letter-spacing: 0.01em;
    color: #777;
  }

  .entry-action {
    flex-shrink: 0;
    font-size: 14px;
    color: #555;
    line-height: 1;
  }
}

@media (max-width: 768px) {
  .publish-inline-entry {
    min-height: 44px;
    padding: 0 14px;
    gap: 12px;
  }
}
</style>
