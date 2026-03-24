<script>
import PageHeadBack from "@/utils/components/PageHeadBack.vue";
import PageScroll from "@/utils/components/PageScroll.vue";
import ICP from "@/utils/components/ICP.vue";
import homeIcon from "@/asset/svg/homeIcon.svg?component";

export default {
  name: "About",
  components: {
    PageHeadBack,
    homeIcon,
    PageScroll,
    ICP,
  },
  data() {
    return {
      appInfo: {
        name: "随想阁楼",
        version: "1.0.0",
      },
    };
  },
};
</script>

<template>
  <PageHeadBack>
    <PageScroll max-height="calc(100vh - var(--app-header-height))">
      <div class="about-page">
        <!-- 头部区域 -->
        <div class="about-header">
          <div class="app-logo">
            <homeIcon class="logo-icon" />
          </div>
          <h1 class="app-name">{{ appInfo.name }}</h1>
          <p class="app-version">版本 {{ appInfo.version }}</p>
        </div>

        <!-- 关于我们文案 -->
        <div class="about-content">
          <p class="about-text">
            这是一个个人作品，一个安静的角落，用来记录技术探索、生活感悟和创作思考。
          </p>
          <p class="about-text">
            没有商业目标，没有增长压力，只是单纯地享受创造的过程，和偶尔相遇的共鸣。
          </p>
          <p class="about-text">
            如果你有任何建议或问题，欢迎通过邮件联系：
            <a href="mailto:zmc_li@foxmail.com" class="contact-link"
              >zmc_li@foxmail.com</a
            >
          </p>
        </div>

        <!-- 底部信息 -->
        <ICP />
      </div>
    </PageScroll>
  </PageHeadBack>
</template>

<style lang="scss" scoped>
.about-page {
  min-height: calc(100vh - var(--app-header-height));
  background-color: #fff;
  display: flex;
  flex-direction: column;
}

/* 头部区域 */
.about-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48px 20px 32px;
  text-align: center;
}

.app-logo {
  margin-bottom: 16px;

  .logo-icon {
    width: 72px;
    height: 72px;
    color: #333;
  }
}

.app-name {
  font-size: 20px;
  font-weight: 500;
  color: #1a1a1a;
  margin: 0 0 6px;
}

.app-version {
  font-size: 13px;
  color: #999;
  margin: 0;
}

/* 内容区域 */
.about-content {
  flex: 1;
  padding: 0 24px;
}

.about-text {
  font-size: 15px;
  line-height: 1.8;
  color: #333;
  margin: 0 0 16px;

  &:last-child {
    margin-top: 50px;
    margin-bottom: 0;
  }
}

.contact-link {
  color: #0066cc;
  text-decoration: none;

  &:hover {
    text-decoration: underline;
  }
}

/* PC端适配 */
@media (min-width: 768px) {
  .about-page {
    max-width: 600px;
    margin: 0 auto;
  }

  .about-header {
    padding-top: 64px;
  }

  .app-logo .logo-icon {
    width: 80px;
    height: 80px;
  }

  .about-content {
    padding: 0 32px;
  }

  .about-text {
    font-size: 15px;
  }
}
</style>
