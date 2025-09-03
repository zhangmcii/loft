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
  data() {
    return {};
  },
  methods: {},
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
            style="--el-skeleton-circle-size: 40px"
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
              style="--el-skeleton-circle-size: 40px"
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
:deep(.el-card__body) {
  padding: 5px 20px;
}
.skeleton-container {
  display: flex;
  gap: 10px;
}
.item {
  width: 80%;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.container {
  display: flex;
  flex-direction: column;
  .container-head {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    .container-head-left {
      display: flex;
      justify-content: space-between;
      width: 30%;
      align-items: center;
    }
  }
  .container-content {
    width: 100%;
    padding: 15px 20px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
}
.block {
  width: 100%;
  height: 5px;
  background-color: #f5f7fa;
  margin: 5px 0px;
}
</style>
