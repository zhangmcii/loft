<script>
export default {
  props: {
    toc: {
      type: Array,
      required: true,
    },
    activeId: {
      type: String,
      default: "",
    },
    mode: {
      type: String,
      default: "drawer",
    },
  },
  data() {
    return {
      show: false,
    };
  },
  methods: {
    scrollToHeading(id) {
      this.$emit("navigate", id);
      const el = document.getElementById(id);
      if (el) {
        el.scrollIntoView({ behavior: "smooth" });
      }
    },
    toggleVisible() {
      this.show = !this.show;
    },
  },
};
</script>

<template>
  <div class="toc" :class="`toc--${mode}`">
    <template v-if="mode === 'inline'">
      <div v-if="toc.length > 0" class="toc-panel">
        <div class="toc-title">目录</div>
        <div class="toc-content">
          <div
            v-for="item in toc"
            :key="item.id"
            class="toc-item"
            :class="{ active: activeId === item.id }"
            :style="{
              paddingLeft: `${(item.level - 1) * 12}px`,
              fontSize: `${18 - item.level * 1}px`,
            }"
            @click="scrollToHeading(item.id)"
          >
            {{ item.text }}
          </div>
        </div>
      </div>
    </template>

    <template v-else>
      <el-button
        v-if="toc.length > 0"
        class="toc-trigger"
        @click="toggleVisible"
      >
        <span class="font-icon">目录</span>
      </el-button>

      <el-drawer
        v-model="show"
        title="目录"
        direction="rtl"
        size="280px"
        :destroy-on-close="false"
        :modal="true"
      >
        <div class="toc-content">
          <div
            v-for="item in toc"
            :key="item.id"
            class="toc-item"
            :class="{ active: activeId === item.id }"
            :style="{
              paddingLeft: `${(item.level - 1) * 12}px`,
              fontSize: `${18 - item.level * 1}px`,
            }"
            @click="scrollToHeading(item.id)"
          >
            {{ item.text }}
          </div>
        </div>
      </el-drawer>
    </template>
  </div>
</template>

<style lang="scss">
.toc {
  position: fixed;
  top: 150px;
  right: 20px;
  z-index: 999;

  .font-icon {
    font-size: 12px;
    letter-spacing: 0.06em;
  }
}

.toc--inline {
  position: static;
  top: auto;
  right: auto;

  .toc-panel {
    padding: 16px 0 0;
    background: #fff;
    border-top: 1px solid #ececec;
  }

  .toc-title {
    padding-bottom: 10px;
    margin-bottom: 12px;
    font-size: 12px;
    letter-spacing: 0.14em;
    color: #777;
    border-bottom: 1px solid #ececec;
  }
}

.toc-trigger {
  min-width: 42px;
  height: 42px;
  padding: 0 14px;
  border-radius: 999px;
  border: 1px solid #dcdcdc;
  background: #fff;
  color: #111;
  box-shadow: none;
}

.toc-content {
  flex: 1;
  overflow-y: auto;

  .toc-item {
    margin-bottom: 8px;
    color: #666;
    font-weight: normal;
    cursor: pointer;
    transition: color 0.2s ease;

    &.active {
      color: #111;
      font-weight: 600;
    }

    &:hover {
      color: #111;
    }
  }
}

.toc :deep(.el-drawer__header) {
  margin-bottom: 0;
  padding: 18px 20px 12px;
  border-bottom: 1px solid #ececec;
}

.toc :deep(.el-drawer__title) {
  color: #111;
  font-weight: 500;
}

.toc :deep(.el-drawer__body) {
  padding: 16px 20px 20px;
}
</style>
