<template>
  <div class="creative-assist">
    <div class="assist-header">
      <span class="assist-hint">🙂 没灵感？</span>
    </div>
    <div class="assist-buttons">
      <!-- <el-button
        size="small"
        :loading="loadingStates.joke"
        :disabled="isLoading"
        @click="generateFromData(jokeData, 'joke', '已为你推荐一条笑话')"
      >
        <el-icon style="color: #ff9800; margin-right: 4px"><i-ep-Sunny /></el-icon>
        笑话
      </el-button> -->
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
      <!-- <el-button
        size="small"
        :loading="loadingStates.quote"
        :disabled="isLoading"
        @click="generateFromData(quoteData, 'quote', '已为你推荐一条励志语录')"
      >
        <el-icon style="color: #9c27b0; margin-right: 4px"><i-ep-Notebook /></el-icon>
        励志语录
      </el-button> -->
    </div>
  </div>
</template>

<script>
import jokes from "@/api/joke/jokes.json";
import pickupLines from "@/api/joke/pickupLines.json";
import thursdayTexts from "@/api/joke/thursday.json";
import quotes from "@/api/joke/quotes.json";

export default {
  name: "CreativeAssist",
  emits: ["contentGenerated"],
  data() {
    return {
      jokeData: jokes,
      pickupLineData: pickupLines,
      thursdayData: thursdayTexts,
      quoteData: quotes,
      loadingStates: {
        joke: false,
        pickupLine: false,
        thursday: false,
        quote: false,
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
      // ElMessage.success(successMessage);
      this.$emit("contentGenerated", content);
    },
  },
};
</script>

<style lang="scss" scoped>
.creative-assist {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: #fafafa;
  border-radius: 6px;

  .assist-header {
    .assist-hint {
      color: #999;
      font-size: 12px;
    }
  }

  .assist-buttons {
    display: flex;
    gap: 6px;

    .el-button {
      padding: 4px 10px;
      font-size: 12px;
      height: auto;
      border-radius: 4px;
      border: 1px solid #eee;
      color: #666;
      background: #fff;
      transition: all 0.2s;

      &:hover:not(:disabled) {
        background: #f5f5f5;
        border-color: #ddd;
      }
    }
  }
}
</style>
