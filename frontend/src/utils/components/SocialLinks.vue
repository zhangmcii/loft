<template>
  <!-- 社交链接 -->
  <div class="social">
    <div class="link">
      <a
        :href="value[0].url"
        target="_blank"
        @mouseenter="socialTip = value[0].tip"
        @mouseleave="socialTip = '通过这里联系我吧'"
      >
        <img class="icon" :src="value[0].icon" height="20" />
      </a>
      <template v-for="item in value.slice(1)" :key="item.name">
        <a
          v-if="item.url"
          target="_blank"
          @mouseenter="socialTip = item.tip"
          @mouseleave="socialTip = '通过这里联系我吧'"
          @click="openDialog(item)"
        >
          <img class="icon" :src="item.icon" height="20" />
        </a>
      </template>
    </div>
    <span class="tip">{{ socialTip }}</span>
  </div>
</template>

<script setup>
import socialLinks from '@/config/socialLinks.json'
import { ref, computed } from 'vue'
import { showConfirmDialog } from 'vant'
import { copy } from '@/utils/common.js'

const props = defineProps({
  // 社交链接配置
  links: {
    type: Object,
    default() {
      return { github: '', email: '', qq: '', wechat: '', bilibili: '', twitter: '' }
    }
  }
})
const value = computed(() => {
  return socialLinks.map((item) => ({
    ...item,
    url: props.links[item.name.toLowerCase()]
  }))
})
// 社交链接提示
const socialTip = ref('通过这里联系我吧')

function openDialog(item) {
  showConfirmDialog({
    title: ` ${item.name} 地址`,
    message: item.url,
    confirmButtonText: '复制链接',
    cancelButtonText: '取消',
    closeOnClickOverlay: true
  })
    .then(() => {
      copy(item.url)
    })
    .catch(() => {
      // on cancel
    })
}
</script>

<style lang="scss" scoped>
.social {
  margin: 0px auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 460px;
  width: 100%;
  height: 42px;
  background-color: transparent;
  border-radius: 6px;
  backdrop-filter: blur(0);
  animation: fade 0.5s;
  transition:
    background-color 0.3s,
    backdrop-filter 0.3s;
  @media (max-width: 840px) {
    max-width: 100%;
    justify-content: center;
    .link {
      justify-content: space-evenly !important;
      width: 80%;
    }
    .tip {
      display: none !important;
    }
  }

  .link {
    display: flex;
    align-items: center;
    justify-content: center;
    a {
      display: inherit;
      .icon {
        margin: 0 12px;
        transition: transform 0.3s;
        &:hover {
          transform: scale(1.1);
        }
        &:active {
          transform: scale(1);
        }
      }
    }
  }
  .tip {
    display: none;
    margin-right: 12px;
    animation: fade 0.5s;
  }
  @media (min-width: 768px) {
    &:hover {
      background-color: #00000040;
      backdrop-filter: blur(5px);
      .tip {
        display: block;
      }
    }
  }
}
</style>
