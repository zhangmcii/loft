<template>
  <div class="creative-assist">
    <!-- <div class="assist-header">
      <span class="assist-hint">🙂 没灵感？</span>
    </div> -->
    <div class="assist-buttons">
      <el-button
        size="small"
        :loading="loadingStates.pickupLine"
        :disabled="isLoading"
        @click="
          generateFromData(
            pickupLineData,
            'pickupLine',
            '已为你推荐一条土味情话'
          )
        "
      >
        <!-- <el-icon style="color: #e91e63; margin-right: 4px"><i-ep-ChatDotRound /></el-icon> -->
        土味情话
      </el-button>
      <el-button
        size="small"
        :loading="loadingStates.thursday"
        :disabled="isLoading"
        @click="
          generateFromData(
            thursdayData,
            'thursday',
            '已为你推荐一条疯狂星期四文案'
          )
        "
      >
        疯狂星期四
      </el-button>
    </div>
  </div>
</template>

<script>
import pickupLines from "@/api/joke/pickupLines.json";
import thursdayTexts from "@/api/joke/thursday.json";

export default {
  name: "CreativeAssist",
  emits: ["contentGenerated"],
  data() {
    return {
      pickupLineData: pickupLines,
      thursdayData: thursdayTexts,
      loadingStates: {
        pickupLine: false,
        thursday: false,
      },
    };
  },
  computed: {
    isLoading() {
      return Object.values(this.loadingStates).some((state) => state);
    },
  },
  methods: {
    async generateFromData(data, loadingKey, successMessage) {
      this.loadingStates[loadingKey] = true;
      await new Promise((resolve) => setTimeout(resolve, 300));

      const randomIndex = Math.floor(Math.random() * data.length);
      const content = data[randomIndex].content;

      this.loadingStates[loadingKey] = false;
      this.$emit("contentGenerated", content);
    },
  },
};
</script>

<style lang="scss" scoped>
@use "./PostReadingTokens.scss" as tokens;

.creative-assist {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  padding: 12px 0 0;
  background: transparent;
  border: none;

  .assist-header {
    .assist-hint {
      color: #777;
      font-size: 12px;
      letter-spacing: 0.03em;
    }
  }

  .assist-buttons {
    display: flex;
    gap: 6px;

    .el-button {
      height: auto;
      padding: 4px 10px;
      font-size: 12px;
      color: tokens.$reading-text-secondary;
      background: #fff;
      border: 1px solid tokens.$reading-border;
      border-radius: 999px;
      box-shadow: none;
      transition: color 0.2s ease, border-color 0.2s ease,
        background-color 0.2s ease;

      &:hover:not(:disabled) {
        background: tokens.$reading-fill-softer;
        border-color: tokens.$reading-border-strong;
        color: tokens.$reading-text-primary;
      }

      &:disabled {
        background: transparent;
        border-color: tokens.$reading-border;
        color: tokens.$reading-text-quaternary;
      }
    }
  }
}
</style>
