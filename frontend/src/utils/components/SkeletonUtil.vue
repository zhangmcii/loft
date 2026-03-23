<script>
export default {
  props: {
    loading: {
      type: Boolean,
      default: false,
    },
    throttle: {
      type: Object,
      default() {
        return { leading: 300, trailing: 300, initVal: true };
      },
    },
    showAvatar: {
      type: Boolean,
      default: true,
    },
    row: {
      type: Number,
      default: 4,
    },
    count: {
      type: Number,
      default: 3,
    },
    cardStyle: {
      type: Object,
      default() {
        return {};
      },
    },
    useNew: {
      type: Boolean,
      default: false,
    },
  },
};
</script>

<template>
  <el-skeleton
    v-if="!useNew"
    animated
    :loading="loading"
    :count="count"
    :throttle="throttle"
  >
    <template #template>
      <el-card shadow="hover" :style="cardStyle">
        <div class="skeleton-container">
          <el-skeleton-item
            variant="circle"
            style="--el-skeleton-circle-size: 30px"
            v-if="showAvatar"
          />
          <div class="item">
            <el-skeleton-item variant="text" style="width: 40%" />
            <el-skeleton-item
              variant="text"
              v-for="item in row - 2"
              :key="item"
            />
            <el-skeleton-item variant="text" style="width: 60%" />
          </div>
        </div>
      </el-card>
    </template>
    <slot></slot>
  </el-skeleton>

  <!-- 适配新版首页文章预览界面 -->
  <el-skeleton
    animated
    :loading="loading"
    :count="count"
    :throttle="throttle"
    v-else
  >
    <template #template>
      <div class="container">
        <div class="container-head">
          <div class="container-head-left">
            <el-skeleton-item
              variant="circle"
              style="--el-skeleton-circle-size: 30px"
              v-if="showAvatar"
            />
            <el-skeleton-item variant="text" style="width: 60%" />
          </div>
          <el-skeleton-item variant="text" style="width: 15%" />
        </div>

        <div class="container-content">
          <el-skeleton-item variant="text" style="width: 40%" />
          <el-skeleton-item
            variant="text"
            v-for="item in row - 2"
            :key="item"
          />
          <el-skeleton-item variant="text" style="width: 60%" />
        </div>

        <div class="block"></div>
      </div>
    </template>
    <slot></slot>
  </el-skeleton>
</template>
<style lang="scss" scoped>
@use "@/views/posts/components/PostReadingTokens.scss" as tokens;

:deep(.el-card__body) {
  padding: 5px 20px;
}

:deep(.el-skeleton__item) {
  --el-skeleton-color: #f4f4f4;
  --el-skeleton-to-color: #fafafa;
}

:deep(.el-skeleton__circle) {
  border: 1px solid tokens.$reading-border;
}

.skeleton-container {
  display: flex;
  gap: 10px;
}

.item {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 80%;
}

.container {
  display: flex;
  flex-direction: column;
  padding: 0 0 26px;
  border-bottom: 1px solid tokens.$reading-border;

  &-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    min-height: 42px;
    margin-bottom: 12px;

    &-left {
      display: flex;
      align-items: center;
      gap: 12px;
      width: 42%;
    }
  }

  &-content {
    display: flex;
    flex-direction: column;
    gap: 10px;
    width: 100%;
    padding: 0;
  }
}

.block {
  width: 100%;
  height: 12px;
  margin: 16px 0 0;
  background-color: transparent;
}
</style>
