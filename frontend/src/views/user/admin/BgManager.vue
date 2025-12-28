<template>
  <ImageManager
    title="管理背景图片"
    upload-title="背景图片"
    :upload-path="uploadPath"
    :load-images-method="loadImagesMethod"
  />
</template>

<script>
import ImageManager from "./ImageManager.vue";
import imageApi from "@/api/user/imageApi.js";
import { useCurrentUserStore } from "@/stores/user";

export default {
  name: "BackgroundImageManager",
  components: {
    ImageManager,
  },
  computed: {
    uploadPath() {
      const currentUser = useCurrentUserStore();
      return currentUser.userBackgroundUrl;
    },
    loadImagesMethod() {
      // 返回一个包装函数，处理特殊的参数
      return (currentPage, size) => {
        return imageApi.getBackgroundImage(
          currentPage,
          size,
          "userBackground/static",
          1
        );
      };
    },
  },
};
</script>
