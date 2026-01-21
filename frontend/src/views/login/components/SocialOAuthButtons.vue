<script setup>
import { computed } from "vue";

const props = defineProps({
  providers: {
    type: Array,
    default: () => [],
  },
  loading: {
    type: String,
    default: "",
  },
});

const emit = defineEmits(["start"]);

// 按需引入 svg 组件
import githubIcon from "@/asset/svg/github.svg?component";
import googleIcon from "@/asset/svg/google.svg?component";
import qqIcon from "@/asset/svg/qqchat.svg?component";
import wechatIcon from "@/asset/svg/wechat.svg?component";

const iconMap = {
  github: githubIcon,
  google: googleIcon,
  qq: qqIcon,
  wechat: wechatIcon,
  wechat_open: wechatIcon,
  wechat_mini: wechatIcon,
};

const renderProviders = computed(() =>
  (props.providers || []).map((item) => {
    const IconComp = iconMap[item.provider];
    return {
      ...item,
      IconComp,
      label: item.name || item.provider,
    };
  })
);

function handleClick(provider) {
  emit("start", provider);
}
</script>

<template>
  <div class="oauth-block" v-if="renderProviders.length">
    <el-divider>其他登录方式</el-divider>
    <div class="oauth-row">
      <button
        v-for="item in renderProviders"
        :key="item.provider"
        class="oauth-chip"
        :disabled="loading === item.provider"
        @click="handleClick(item.provider)"
      >
        <span class="icon" v-if="item.IconComp">
          <component :is="item.IconComp" class="svg" />
        </span>
        <span class="fallback" v-else>{{ item.label?.[0] || "?" }}</span>
        <span class="label">{{ item.label }}</span>
        <span class="spinner" v-if="loading === item.provider"></span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.oauth-block {
  width: 100%;
  margin: 10px 0 4px;
}

.oauth-row {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.oauth-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 999px;
  background: #ffffff;
  cursor: pointer;
  transition: transform 0.12s ease, box-shadow 0.12s ease,
    border-color 0.12s ease;
  min-width: 110px;
  height: 40px;
}

.icon {
  width: 20px;
  height: 20px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.svg {
  width: 100%;
  height: 100%;
}

.fallback {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #f3f4f6;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: #374151;
}

.label {
  color: #111827;
  font-size: 13px;
  font-weight: 500;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.9s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.oauth-chip:disabled {
  opacity: 0.72;
  cursor: not-allowed;
}

.oauth-chip:not(:disabled):hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.06);
  border-color: #d1d5db;
}

.oauth-chip:not(:disabled):active {
  transform: translateY(0);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.04);
}
</style>
