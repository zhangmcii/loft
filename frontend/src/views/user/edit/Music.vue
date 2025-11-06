<script setup>
import PageHeadBack from "@/utils/components/PageHeadBack.vue";
import { useCurrentUserStore } from "@/stores/user";
import { cloneDeep } from "@pureadmin/utils";
import editApi from "@/api/user/editApi.js";
import { clearObj } from "@/utils/common.js";
import { ref, reactive, computed, onMounted } from "vue";

const user = useCurrentUserStore();

const userData = reactive({
  localUserInfo: {
    id: "",
    music: {
      name: "",
      artist: "",
      url: "",
      pic: "",
      lrc: "",
    },
  },
});

userData.localUserInfo = cloneDeep(user.userInfo);

// 响应式数据
const musicInfoLoading = ref(false);
const audioLoading = ref(false);
const setMusicLoading = ref(false);

const musicInfo = ref([]);
const searchKeyword = ref("");
const currentPage = ref(1);
const pageSize = ref(10);
// 实际用于搜索的关键词（点击搜索按钮后才生效）
const activeSearchKeyword = ref("");

// 音频播放相关
const audioPlayer = ref(null);
const isPlaying = ref(false);
const currentPlayingIndex = ref(-1);
const tableHeight = ref("500");
const h1 = ref(null);
const h2 = ref(null);
const h3 = ref(null);

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
        // id: "434592911",
      };
    },
    validator: (value) => {
      return value.server && value.type && value.id;
    },
  },
});

// 计算属性：过滤后的音乐数据
const filteredMusicInfo = computed(() => {
  if (!activeSearchKeyword.value || !activeSearchKeyword.value.trim()) {
    return musicInfo.value;
  }

  const keyword = activeSearchKeyword.value.toLowerCase().trim();
  return musicInfo.value.filter(
    (item) =>
      (item?.name && item.name.toLowerCase().includes(keyword)) ||
      (item?.artist && item.artist.toLowerCase().includes(keyword))
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
  calTableHeight();
});

// 获取音乐信息
const fetchMusicInfo = async () => {
  musicInfoLoading.value = true;
  try {
    console.log("开始请求音乐信息，配置:", props.musicConfig);
    const response = await fetch(
      // `https://api.i-meto.com/meting/api?server=${props.musicConfig.server}&type=${props.musicConfig.type}&id=${props.musicConfig.id}`
      `https://api.qijieya.cn/meting/?server=${props.musicConfig.server}&type=${props.musicConfig.type}&id=${props.musicConfig.id}`
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
        name: "音乐加载失败",
        artist: "请检查网络连接",
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
};

// 选择音乐
const handleSelectMusic = async (music) => {
  // 存储上次选择的音乐
  userData.localUserInfo.music = music;
  await saveMusic();
  user.setUserInfo(userData.localUserInfo);
};

// 取消选择音乐
const handleCancelSelect = async () => {
  // 将已选择的音乐设置为空对象
  userData.localUserInfo.music = clearObj(userData.localUserInfo.music);
  await saveMusic();
  user.setUserInfo(userData.localUserInfo);
};

// 检查是否为已选择的音乐
const isSelected = (music) => {
  if (!music || !userData.localUserInfo?.music) return false;

  return (
    userData.localUserInfo.music.name === music.name &&
    userData.localUserInfo.music.artist === music.artist
  );
};

// 播放/暂停音乐
const togglePlay = async (music, index) => {
  if (!music?.url) return;

  if (currentPlayingIndex.value === index && isPlaying.value) {
    // 暂停当前播放
    audioPlayer.value.pause();
    isPlaying.value = false;
  } else {
    // 显示加载状态
    audioLoading.value = true;

    // 停止之前的播放
    if (audioPlayer.value) {
      audioPlayer.value.pause();
    }

    // 创建新的音频元素
    audioPlayer.value = new Audio(music.url);

    // 设置事件监听
    audioPlayer.value.addEventListener("ended", () => {
      isPlaying.value = false;
      currentPlayingIndex.value = -1;
    });

    audioPlayer.value.addEventListener("canplay", () => {
      audioPlayer.value.play();
      isPlaying.value = true;
      currentPlayingIndex.value = index;
      audioLoading.value = false;
    });

    audioPlayer.value.addEventListener("error", () => {
      audioLoading.value = false;
      console.error("音频加载失败");
    });

    // 开始播放
    audioPlayer.value.load();
  }
};

async function saveMusic() {
  try {
    setMusicLoading.value = true;

    if (!user?.userInfo?.id) {
      throw new Error("用户信息不完整，无法保存音乐设置");
    }

    await editApi.editUser(user.userInfo.id, {
      music: userData.localUserInfo.music,
    });
  } catch (error) {
    console.error("保存音乐设置失败:", error);
    // 可以在这里添加用户提示
  } finally {
    setMusicLoading.value = false;
  }
}

const calTableHeight = async () => {
  const h1Height = h1.value?.offsetHeight || 0;
  const h2Height = h2.value?.offsetHeight || 0;
  const h3Height = h3.value?.offsetHeight || 0;
  tableHeight.value = `calc(100vh - ${h1Height}px - ${h2Height}px - ${h3Height}px - 95px - var(--el-main-padding) * 2)`;
};
</script>

<template>
  <PageHeadBack>
    <!-- 搜索区域 -->
    <div class="search-section" ref="h1">
      <el-input
        v-model="searchKeyword"
        placeholder="请输入歌曲名或作者进行搜索"
        clearable
        @keyup.enter="handleSearch"
        @clear="handleResetSearch"
        style="width: 300px; margin-right: 16px"
      >
        <template #prefix>
          <el-icon><i-ep-Search /></el-icon>
        </template>
      </el-input>

      <div class="search-buttons">
        <el-button
          type="primary"
          :disabled="!searchKeyword"
          @click="handleSearch"
        >
          <el-icon><i-ep-Search /></el-icon>
          搜索
        </el-button>

        <el-button @click="handleResetSearch" :disabled="!searchKeyword">
          <el-icon><i-ep-Refresh /></el-icon>
          清空
        </el-button>
      </div>
    </div>

    <!-- 上次已选择音乐提示 -->
    <div
      class="selected-music-section"
      v-if="userData.localUserInfo.music && userData.localUserInfo.music.name"
      ref="h2"
    >
      <div class="selected-music-header">
        <el-icon><i-ep-Star /></el-icon>
        <span>已选择的音乐</span>
      </div>

      <div class="selected-music-row">
        <div class="music-cover">
          <el-image
            :src="userData.localUserInfo.music.pic"
            style="width: 60px; height: 60px; border-radius: 4px"
            fit="cover"
            :preview-src-list="
              userData.localUserInfo.music.pic
                ? [userData.localUserInfo.music.pic]
                : []
            "
            :preview-teleported="true"
            :hide-on-click-modal="true"
          >
            <template #error>
              <div class="image-error">
                <el-icon><i-ep-Picture /></el-icon>
              </div>
            </template>
          </el-image>
        </div>

        <div class="music-info">
          <div class="music-title">
            {{ userData.localUserInfo.music.name }}
          </div>
          <div class="music-author">
            {{ userData.localUserInfo.music.artist }}
          </div>
        </div>

        <div class="music-actions">
          <el-button type="danger" size="small" @click="handleCancelSelect">
            取消选择
          </el-button>
        </div>
      </div>
    </div>

    <!-- 音乐列表 -->
    <el-table
      :data="paginatedMusicInfo"
      v-loading="musicInfoLoading"
      :height="tableHeight"
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
                <el-icon><i-ep-Picture /></el-icon>
              </div>
            </template>
          </el-image>
        </template>
      </el-table-column>

      <el-table-column prop="name" label="歌曲名" min-width="150" />

      <el-table-column prop="artist" label="作者" min-width="80" />

      <el-table-column label="预览" align="center">
        <template #default="scope">
          <el-button
            circle
            size="small"
            :type="
              currentPlayingIndex === scope.$index && isPlaying
                ? 'danger'
                : 'primary'
            "
            @click="togglePlay(scope.row, scope.$index)"
            :disabled="!scope.row.url || audioLoading"
            :loading="audioLoading && currentPlayingIndex === scope.$index"
          >
            <el-icon v-if="currentPlayingIndex === scope.$index && isPlaying">
              <i-ep-VideoPause />
            </el-icon>
            <el-icon
              v-else-if="currentPlayingIndex !== scope.$index || !isPlaying"
            >
              <i-ep-VideoPlay />
            </el-icon>
          </el-button>
        </template>
      </el-table-column>

      <el-table-column label="操作" align="center" fixed="right">
        <template #default="scope">
          <el-button
            :type="isSelected(scope.row) ? 'danger' : 'primary'"
            size="small"
            @click="
              isSelected(scope.row)
                ? handleCancelSelect()
                : handleSelectMusic(scope.row)
            "
            :loading="setMusicLoading && isSelected(scope.row) === false"
            :disabled="!scope.row.url"
          >
            {{ isSelected(scope.row) ? "取消选择" : "选择" }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页区域 -->
    <div class="pagination-section" ref="h3">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="filteredMusicInfo.length"
        layout="total, prev, pager, next"
        :pager-count="5"
        :hide-on-single-page="true"
        size="small"
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

.selected-music-section {
  margin-bottom: 16px;
  padding: 16px;
  background-color: #fff8e1;
  border: 1px solid #ffe082;
  border-radius: 4px;

  .selected-music-header {
    display: flex;
    align-items: center;
    margin-bottom: 16px;
    color: #f57c00;
    font-weight: 600;
    font-size: 14px;

    .el-icon {
      margin-right: 8px;
      font-size: 16px;
    }
  }

  .selected-music-row {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 12px;
    background-color: #fff;
    border-radius: 4px;
    border: 1px solid #e8e8e8;

    .music-cover {
      flex-shrink: 0;
    }

    .music-info {
      flex: 1;

      .music-title {
        font-size: 16px;
        font-weight: 600;
        color: #333;
        margin-bottom: 4px;
      }

      .music-author {
        font-size: 14px;
        color: #666;
      }
    }

    .music-actions {
      flex-shrink: 0;
    }
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

  .selected-music-section {
    .selected-music-content {
      flex-direction: column;
      align-items: flex-start;
      gap: 12px;

      .music-info {
        width: 100%;
      }
    }
  }
}
</style>
