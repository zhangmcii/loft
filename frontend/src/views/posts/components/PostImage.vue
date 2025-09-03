<script>
export default {
  props: {
    postImages: {
      type: Array,
      default() {
        return [];
      },
    },
  },
  computed: {
    gridTemplateColumns() {
      const count = this.postImages.length;
      if (count === 1) return "1fr";
      if (count === 2 || count === 4) return "1fr 1fr";
      return "1fr 1fr 1fr";
    },
    containerWidth() {
      const count = this.postImages.length;
      if (count === 1) return "220px";
      if (count === 2 || count === 4) return "320px";
      return "370px";
    },
  },
};
</script>

<template>
  <div class="container" :style="{ width: containerWidth }">
    <div class="preview" :style="{ gridTemplateColumns }">
      <photo-provider :photo-closable="true" :should-transition="true">
        <photo-consumer
          v-for="(url, index) in postImages"
          :intro="url"
          :key="url"
          :src="url"
        >
          <el-image alt="文章图片" :src="url" lazy fit="cover">
            <template #error>
              <div class="image-slot">
                <el-icon><i-ep-picture /></el-icon>
              </div>
            </template>
          </el-image>
        </photo-consumer>
      </photo-provider>
    </div>
  </div>
</template>
<style lang="scss" scoped>
.container {
  .preview {
    display: grid;
    gap: 5px;
    width: 100%;
    margin: 0 auto;
    .el-image {
      width: 100%;
      aspect-ratio: 1;
      .image-slot {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        height: 100%;
        background: var(--el-fill-color-light);
        color: var(--el-text-color-secondary);
        font-size: 14px;
        .el-icon {
          font-size: 30px;
        }
      }
    }
  }
}
</style>
