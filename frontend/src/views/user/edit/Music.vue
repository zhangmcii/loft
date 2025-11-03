<script setup>
import PageHeadBack from "@/utils/components/PageHeadBack.vue";
import { ref, reactive, computed, onMounted } from "vue";

// 响应式数据
const musicInfoLoading = ref(false);
const musicInfo = ref([]);
const searchKeyword = ref("");
const currentPage = ref(1);
const pageSize = ref(10);
// 记录搜索前的页码，用于重置时恢复
const preSearchPage = ref(1);
// 实际用于搜索的关键词（点击搜索按钮后才生效）
const activeSearchKeyword = ref("");

const props = defineProps({
  // 音乐配置
  musicConfig: {
    type: Object,
    required: true,
    default: () => {
      return {
        server: "netease",
        type: "playlist",
        id: "3778678",
      };
    },
    validator: (value) => {
      return value.server && value.type && value.id;
    },
  },
});

// 计算属性：过滤后的音乐数据
const filteredMusicInfo = computed(() => {
  if (!activeSearchKeyword.value.trim()) {
    return musicInfo.value;
  }

  const keyword = activeSearchKeyword.value.toLowerCase().trim();
  return musicInfo.value.filter(
    (item) =>
      (item.title && item.title.toLowerCase().includes(keyword)) ||
      (item.author && item.author.toLowerCase().includes(keyword))
  );
});

// 计算属性：分页后的数据
const paginatedMusicInfo = computed(() => {
  const startIndex = (currentPage.value - 1) * pageSize.value;
  const endIndex = startIndex + pageSize.value;
  return filteredMusicInfo.value.slice(startIndex, endIndex);
});

// 计算属性：总页数
const totalPages = computed(() => {
  return Math.ceil(filteredMusicInfo.value.length / pageSize.value);
});

onMounted(() => {
  fetchMusicInfo();
});

// 获取音乐信息
const fetchMusicInfo = async () => {
  musicInfoLoading.value = true;
  try {
    console.log("开始请求音乐信息，配置:", props.musicConfig);
    const response = await fetch(
      `https://api.i-meto.com/meting/api?server=${props.musicConfig.server}&type=${props.musicConfig.type}&id=${props.musicConfig.id}`
    );
    if (!response.ok) {
      throw new Error(`网络请求失败: ${response.status}`);
    }
    const data = await response.json();
    console.log("音乐信息获取成功:", data);
    musicInfo.value = data;
    // 重置搜索和分页状态
    searchKeyword.value = "";
    currentPage.value = 1;
  } catch (error) {
    console.error("请求音乐信息失败:", error);
    // 设置默认音乐信息以防请求失败
    musicInfo.value = [
      {
        title: "音乐加载失败",
        author: "请检查网络连接",
        url: "",
        pic: "",
      },
    ];
  } finally {
    musicInfoLoading.value = false;
  }
};

// 分页切换处理
const handlePageChange = async (page) => {
  // 添加轻微延迟以模拟请求
  await new Promise((resolve) => setTimeout(resolve, 300));
  currentPage.value = page;
};

// 搜索处理
const handleSearch = async () => {
  // 记录搜索前的页码
  if (!activeSearchKeyword.value.trim()) {
    preSearchPage.value = currentPage.value;
  }

  // 添加轻微延迟以模拟请求
  await new Promise((resolve) => setTimeout(resolve, 300));

  // 设置实际搜索关键词
  activeSearchKeyword.value = searchKeyword.value;
  // 搜索时跳转到第一页
  currentPage.value = 1;
};

// 重置搜索
const handleResetSearch = async () => {
  // 添加轻微延迟以模拟请求
  await new Promise((resolve) => setTimeout(resolve, 300));

  searchKeyword.value = "";
  // 清空实际搜索关键词
  activeSearchKeyword.value = "";
  // 重置后回到搜索前的页码
  currentPage.value = preSearchPage.value;
};

// 选择音乐
const handleSelectMusic = (music) => {
  console.log("选择音乐:", music);
  // 这里可以添加选择音乐后的逻辑，比如触发事件等
  // emit('select', music);
};
</script>

<template>
  <PageHeadBack>
    <!-- 搜索区域 -->
    <div class="search-section">
      <el-input
        v-model="searchKeyword"
        placeholder="请输入歌曲名或作者进行搜索"
        clearable
        @clear="handleResetSearch"
        style="width: 300px; margin-right: 16px"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>

      <div class="search-buttons">
        <el-button
          type="primary"
          :disabled="!searchKeyword"
          @click="handleSearch"
        >
          <el-icon><Search /></el-icon>
          搜索
        </el-button>

        <el-button @click="handleResetSearch" :disabled="!searchKeyword">
          <el-icon><Refresh /></el-icon>
          重置
        </el-button>
      </div>
      <span class="search-result-info">
        共找到 {{ filteredMusicInfo.length }} 条结果
      </span>
    </div>

    <!-- 音乐列表 -->
    <el-table
      :data="paginatedMusicInfo"
      v-loading="musicInfoLoading"
      max-height="500"
      stripe
      border
      class="music-table"
    >
      <el-table-column prop="pic" label="封面" width="80" align="center">
        <template #default="scope">
          <el-image
            :src="scope.row.pic"
            style="width: 50px; height: 50px"
            fit="cover"
            :preview-src-list="scope.row.pic ? [scope.row.pic] : []"
            :preview-teleported="true"
            :hide-on-click-modal="true"
          >
            <template #error>
              <div class="image-error">
                <el-icon><Picture /></el-icon>
              </div>
            </template>
          </el-image>
        </template>
      </el-table-column>

      <el-table-column prop="title" label="歌曲名" min-width="150" />

      <el-table-column prop="author" label="作者" min-width="150" />

      <el-table-column label="操作" align="center" fixed="right">
        <template #default="scope">
          <el-button
            type="primary"
            size="small"
            @click="handleSelectMusic(scope.row)"
            :disabled="!scope.row.url"
          >
            选择
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页区域 -->
    <div class="pagination-section" v-if="filteredMusicInfo.length > 0">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="filteredMusicInfo.length"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        background
        @size-change="
          (size) => {
            pageSize = size;
            currentPage = 1;
          }
        "
        @current-change="handlePageChange"
      />
    </div>

    <!-- 空状态 -->
    <el-empty
      v-if="!musicInfoLoading && filteredMusicInfo.length === 0"
      description="暂无数据"
      :image-size="200"
    />
  </PageHeadBack>
</template>

<style lang="scss" scoped>
.search-section {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 4px;

  .el-button {
    width: 30%;
  }

  .search-result-info {
    margin-left: auto;
    color: #666;
    font-size: 14px;
  }
}

.music-table {
  margin-bottom: 16px;

  .image-error {
    width: 50px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #f5f7fa;
    border-radius: 4px;
    color: #c0c4cc;
  }
}

.pagination-section {
  display: flex;
  justify-content: center;
  padding: 16px 0;
}

@media (max-width: 768px) {
  .search-section {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;

    .search-result-info {
      margin-left: 0;
      text-align: center;
    }
  }
}
</style>
