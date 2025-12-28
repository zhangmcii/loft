<template>
  <ImageManager
    title="管理公共图像"
    upload-title="公共图像"
    :upload-path="uploadPath"
    :load-images-method="loadImagesMethod"
  />
</template>

<script>
import ImageManager from "./ImageManager.vue";
import imageApi from "@/api/user/imageApi.js";
import { useCurrentUserStore } from "@/stores/user";

export default {
  name: "AvatarsManager",
  components: {
    ImageManager,
  },
  computed: {
    uploadPath() {
      const currentUser = useCurrentUserStore();
      return currentUser.userAvatars;
    },
    loadImagesMethod() {
      return imageApi.getPublicImages;
    },
  },
};
</script>
