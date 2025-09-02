<template>
  <div class="vapp-fullscreen-background">
    <el-page-header :style="{ color: backColor }" @back="$router.back()" title="返回" />

    <el-switch
      v-model="isUserPage"
      :loading="loading.switch"
      size="large"
      style="--el-switch-on-color: #424242; --el-switch-off-color: #424242"
      inline-prompt
      active-text="主页"
      inactive-text="文章"
      @change="handleSwitchChange"
      :before-change="beforeSwitch"
    />
    <div class="area-container">
      <div class="avatar" style="margin-top: 1rem">
        <el-image
          fit="cover"
          style="border-radius: 50%; width: 120px; height: 120px"
          alt="用户图像"
          :src="user.image"
          :preview-src-list="srcList"
        />
      </div>

      <div v-show="isUserPage">
        <!-- tags -->
        <el-card class="tags-container" v-if="user.tags.length > 0">
          <div class="card-title"></div>
          <div class="tags">
            <el-tag
              class="golang"
              v-for="item in user.tags"
              :key="item"
              size="small"
              round
              @click="playTagAnimation"
            >
              {{ item }}
            </el-tag>
          </div>
        </el-card>
        <div class="user-info-container">
          <el-row :gutter="10">
            <el-col :span="12">
              <el-card class="user-info" shadow="never">
                <div class="card-title">
                  <span>个人信息</span>
                  <el-button
                    round
                    size="small"
                    style="margin-left: 5px"
                    v-if="isCurrentUser"
                    @click="editProfile"
                    >编辑资料</el-button
                  >
                  <el-button
                    type="danger"
                    round
                    size="small"
                    v-if="currentUser.isAdmin"
                    @click="editProfileAdmin"
                    >编辑资料 [管理员]</el-button
                  >
                </div>
                <el-skeleton
                  :rows="5"
                  animated
                  :loading="loading.userData"
                  :throttle="skeletonThrottle"
                >
                  <template #default>
                    <el-row v-if="user.nickname">
                      <el-col :xs="6" :xl="4">昵称</el-col>
                      <el-col :xs="8" :xl="10">{{ user.nickname }}</el-col>
                    </el-row>
                    <el-row>
                      <el-col :xs="6" :xl="4">账号</el-col>
                      <el-col :xs="16" :xl="10">{{ user.username }}</el-col>
                    </el-row>
                    <el-row v-if="user.location">
                      <el-col :xs="6" :xl="4">所在地</el-col>
                      <el-col :xs="16" :xl="10">{{ location }}</el-col>
                    </el-row>
                    <el-row v-if="user.sex">
                      <el-col :xs="6" :xl="4">性别</el-col>
                      <el-col :xs="15" :xl="10">{{ user.sex }}</el-col>
                    </el-row>
                    <el-row>
                      <el-col :xs="6" :xl="4">生日</el-col>
                      <el-col :xs="15" :xl="10">{{ member_since }}</el-col>
                    </el-row>
                    <el-row>
                      <el-col :xs="8" :xl="4">上线时间</el-col>
                      <el-col :xs="8" :xl="10" :offset="2">{{ from_now }}</el-col>
                    </el-row>
                  </template>
                </el-skeleton>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card class="fans" shadow="never">
                <el-skeleton animated :loading="loading.userData" :throttle="skeletonThrottle">
                  <template #template>
                    <div
                      style="display: flex; justify-items: space-between; gap: 15px; height: 47px"
                    >
                      <el-skeleton-item variant="text" class="item" />
                      <el-skeleton-item variant="text" class="item" />
                    </div>
                  </template>
                  <template #default>
                    <el-row>
                      <el-col :span="6">
                        <el-statistic
                          title="粉丝"
                          :value="user.followers_count"
                          @click="followerDetail"
                        />
                      </el-col>
                      <el-col :span="6">
                        <el-statistic
                          title="关注"
                          :value="user.followed_count"
                          @click="followedDetail"
                        />
                      </el-col>
                      <el-col :span="6">
                        <el-statistic
                          title="动态"
                          :value="user.posts_count || 0"
                        />
                      </el-col>
                      <el-col :span="6">
                        <el-statistic
                          title="获赞"
                          :value="user.likes_count || 0"
                        />
                      </el-col>
                    </el-row>
                  </template>
                </el-skeleton>
              </el-card>
              <el-card class="user-wisdom" shadow="never">
                <div class="card-title">
                  <span>个性签名</span>
                </div>
                <!-- 打字机 -->
                <typewriter class="typewriter" :content="user.about_me"></typewriter>
              </el-card>
            </el-col>
          </el-row>
        </div>

        <!-- 新增功能区域 -->
        <div class="enhanced-sections">
          <!-- 徽章成就区域 -->
          <el-card class="badges-section glass" v-if="user.badges && user.badges.length > 0">
            <div class="card-title">
              <span>徽章成就</span>
            </div>
            <div class="badges-grid">
              <div class="badge-item" v-for="badge in user.badges" :key="badge.id">
                <div class="badge-icon">{{ badge.icon }}</div>
                <div class="badge-info">
                  <span class="badge-name">{{ badge.name }}</span>
                  <span class="badge-desc">{{ badge.description }}</span>
                </div>
              </div>
            </div>
          </el-card>

          <!-- 兴趣标签区域 -->
          <el-card class="interests-section glass" v-if="user.interests && user.interests.length > 0">
            <div class="card-title">
              <span>我的标签</span>
            </div>
            <div class="interests-tags">
              <el-tag 
                class="interest-tag" 
                v-for="tag in user.interests" 
                :key="tag"
                size="small"
                round
              >
                {{ tag }}
              </el-tag>
            </div>
          </el-card>

          <!-- 最近动态预览 -->
          <el-card class="activities-section glass" v-if="user.recentActivities && user.recentActivities.length > 0">
            <div class="card-title">
              <span>最近动态</span>
            </div>
            <div class="activities-list">
              <div class="activity-item" v-for="activity in user.recentActivities.slice(0, 3)" :key="activity.id">
                <div class="activity-time">{{ formatTime(activity.time) }}</div>
                <div class="activity-content">{{ activity.content }}</div>
              </div>
            </div>
          </el-card>

          <!-- 数据统计区域 -->
          <el-card class="statistics-section glass">
            <div class="card-title">
              <span>数据统计</span>
            </div>
            <div class="stats-grid">
              <div class="stats-item">
                <div class="stats-value">{{ user.profile_views || 0 }}</div>
                <div class="stats-label">主页访问</div>
              </div>
              <div class="stats-item">
                <div class="stats-value">{{ user.total_likes || 0 }}</div>
                <div class="stats-label">总获赞数</div>
              </div>
              <div class="stats-item">
                <div class="stats-value">{{ user.active_days || 0 }}</div>
                <div class="stats-label">活跃天数</div>
              </div>
              <div class="stats-item">
                <div class="stats-value">{{ user.interaction_rate || '0%' }}</div>
                <div class="stats-label">互动率</div>
              </div>
            </div>
          </el-card>
        </div>

        <ButtonAnimate
          content="喜欢的电影"
          :isActive="activeInterest === 'movie'"
          @click="setActive('movie')"
        />
        <ButtonAnimate
          content="喜爱的书籍"
          :isActive="activeInterest === 'book'"
          @click="setActive('book')"
        />
        <interest :showInterest="activeInterest" :interest="user.interest" />
        <el-card class="socialLinks" v-if="!socialCount">
          <socialLinks :links="user.social_account" />
        </el-card>

        <!-- <div class="hamburger" @click="but = !but">
        <van-icon name="wap-nav" size="24" v-show="!but" />
        <van-icon name="cross" size="24" v-show="but" />
      </div> -->
        <div class="bottom"></div>
      </div>
      <!-- 文章区  -->
      <div v-show="!isUserPage" class="posts-container">
        <SkeletonUtil :loading="loading.userData" :row="5" :count="1" :showAvatar="false">
          <PostPreview
            v-for="item in posts"
            :key="item.id"
            :post="item"
            :containerStyle="{ marginBottom: '10px' }"
            @click="$router.push(`/postDetail/${item.id}`)"
            v-slide-in
          >
            <template #image>
              <PostImage :postImages="item.post_images" @click.stop="" />
            </template>
          </PostPreview>
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="10"
            layout="total, prev, pager, next"
            :total="posts_count"
            @current-change="handleCurrentChange"
            :hide-on-single-page="true"
            :pager-count="5"
          />
          <el-empty :image-size="200" description="生活总归带点荒谬" v-if="posts.length === 0" />
        </SkeletonUtil>
      </div>
      <div class="block" v-if="!isCurrentUser && !loading.skeleton"></div>
      <div class="footer" v-if="!isCurrentUser && !loading.skeleton">
        <el-button color="#d1edc4" round class="chat" @click="openChat">
          <template #icon>
            <el-icon><i-ep-ChatRound /></el-icon>
          </template>
          私信
        </el-button>
        <div>
          <el-button
            color="#faecd8"
            round
            class="follow"
            v-if="isFollowOtherUser"
            @click="unFollowUser"
          >
            <template #icon>
              <el-icon>
                <i-ep-Switch v-if="isFollowEachOther" />
                <i-ep-Check v-else-if="isFollowOtherUser" />
              </el-icon>
            </template>
            取消关注
          </el-button>
          <el-button
            color="#faecd8"
            round
            class="follow"
            v-else
            :loading="loading.follow"
            @click="followUser"
          >
            <template #icon>
              <el-icon><i-ep-Plus /></el-icon>
            </template>
            关注
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script src="./userData.js"></script>

<style lang="scss" scoped>
:root {
  --leleo-background-image-url: none;
}
.vapp-fullscreen-background {
  position: position;
  height: 100%;
  width: 100%;
  top: 0;
  left: 0;
  z-index: -1;
}
/* 添加一个::before伪元素降低背景图片的亮度，而不会影响background元素的其他内容 */
.vapp-fullscreen-background::before {
  content: '';
  background-image: var(--leleo-background-image-url);
  transition: background-image 0.8s ease;
  background-size: cover;
  background-position: center;
  position: absolute;
  height: 100%;
  width: 100%;
  z-index: -1;
  /* 调整亮度值  */
  filter: brightness(85%);
}
.el-page-header {
  position: fixed;
  top: 56px;
  left: 10px;
  z-index: 99;
}

.el-switch {
  position: fixed;
  right: 0;
  z-index: 99;
}
.area-container {
  overflow-y: auto;
  overflow-x: hidden;
  // 确保撑满视口
  height: 100vh;
  // 保证内容在背景之上
  z-index: 1;
}
.avatar {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 1rem;
}

//设置为毛玻璃样式
.glass {
  backdrop-filter: blur(15px);
  border-radius: 5%;
  color: #ffffff;
  /* 确保背景透明，显示毛玻璃效果 */
  background-color: transparent;
  /* 移除默认边框 */
  border: none;
}
.tags-container {
  @extend .glass;
  max-width: 270px;
  margin: 10px auto; /* 左右边距自动 */
  .tags {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
  }
}
:deep(.el-card__body) {
  padding: 8px;
}
.user-info-container {
  width: 90%;
  margin: 0 auto;
}
.user-info {
  @extend .glass;
  min-height: 190px;
  .card-title {
    margin-bottom: 10px;
    color: #fff;
    font-size: 20px;
  }
  font-size: 12px;
  // color: #e3d4d4;
  color: #fff;
  letter-spacing: 0.05em;
  margin-bottom: 10px;
}

.el-statistic {
  width: 30px;
  text-align: center;
}
:deep(.el-statistic__head) {
  font-size: 0.9rem;
  color: #fff;
}
:deep(.el-statistic__number) {
  font-size: 1rem;
  color: #fff;
}

.fans {
  @extend .glass;
}
.user-wisdom {
  @extend .glass;
  margin-top: 5px;
  max-height: 120px;
}

.el-tag {
  background-color: transparent;
  margin: 4px;
  padding: 0px 10px;
  border: 1px solid rgb(216.8, 235.6, 255);
  border-color: rgba(0, 0, 0, 0.12);
}
:deep(.el-tag__content) {
  color: #ffffff;
  font-family: Roboto, sans-serif;
}

// 点击tag的动画
.golang {
  transition: all 0.2s ease-in-out;
  position: relative;
  opacity: 1;
  overflow: hidden;
}

.golang:before {
  content: '';
  background-color: rgba(255, 255, 255, 0.5);
  height: 100%;
  width: 3em;
  display: block;
  position: absolute;
  top: 0;
  left: -4.5em;
  transform: skewX(-45deg) translateX(0);
  transition: none;
}

// 如果一个标签中同时使用了这两个类,
// 则响应此样式规则。
.golang.animate:before {
  transform: skewX(-45deg) translateX(260px);
  transition: all 0.7s ease-in-out;
}
.typewriter {
  margin: 12px;
}
.interest-card {
  max-width: 90%;
  margin: 0 auto; /* 左右边距自动 */
  padding: 2px;
}
.socialLinks {
  @extend .glass;
  max-width: 270px;
  margin: 0px auto; /* 左右边距自动 */
}
.socialLinks :deep(.el-card__body) {
  padding: 2px;
}

.hamburger {
  width: 56px;
  height: 27px;
  margin: 0px auto;
  background-color: #00000033;
  display: flex;

  // 线条垂直居中
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
.bottom {
  height: 1500px;
  width: 100%;
}
.posts-container {
  margin: 0px 20px;
}

//  //
.PhotoConsumer {
  width: 100%;
}
.pre-image {
  width: 100%;
  height: 40px;
  font-size: 0.9rem;
  margin-top: 2px;
}
.upload {
  width: 100%;
  text-align: center;
  height: 33px;
}

.select-image {
  width: 100%;
  font-size: 0.9rem;
}
.el-divider {
  margin: 2px 0px 2px 0px;
}
.item {
  width: 20%;
  margin-top: 20px;
}

.skeleton-item {
  width: v-bind(skeletonItemWidth);
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.block {
  margin-bottom: 33px;
}
.footer {
  position: fixed;
  bottom: 0px;
  padding: 10px;
  height: 40px;
  width: 95%;
  margin: 0px auto;
  display: flex;
  justify-content: space-between;
  div,
  .chat {
    width: 48%;
    height: 40px;
  }
  .follow {
    width: 100%;
    height: 40px;
  }
}

// 新增功能区域样式
.enhanced-sections {
  width: 90%;
  margin: 0 auto;
  
  .el-card {
    margin-bottom: 10px;
    transition: all 0.3s ease;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
  }
}

// 徽章成就样式
.badges-section {
  .badges-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    
    .badge-item {
      display: flex;
      align-items: center;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 8px;
      padding: 6px 10px;
      transition: all 0.3s ease;
      
      &:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: scale(1.05);
      }
      
      .badge-icon {
        font-size: 16px;
        margin-right: 6px;
      }
      
      .badge-info {
        display: flex;
        flex-direction: column;
        
        .badge-name {
          font-size: 12px;
          font-weight: 500;
          color: #fff;
        }
        
        .badge-desc {
          font-size: 10px;
          color: rgba(255, 255, 255, 0.7);
        }
      }
    }
  }
}

// 兴趣标签样式
.interests-section {
  .interests-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    
    .interest-tag {
      background: rgba(255, 255, 255, 0.1);
      border: 1px solid rgba(255, 255, 255, 0.3);
      color: #fff;
      transition: all 0.3s ease;
      
      &:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: translateY(-1px);
      }
    }
  }
}

// 最近动态样式
.activities-section {
  .activities-list {
    .activity-item {
      padding: 8px 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      
      &:last-child {
        border-bottom: none;
      }
      
      .activity-time {
        font-size: 10px;
        color: rgba(255, 255, 255, 0.6);
        margin-bottom: 4px;
      }
      
      .activity-content {
        font-size: 12px;
        color: #fff;
        line-height: 1.4;
      }
    }
  }
}

// 数据统计样式
.statistics-section {
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    
    .stats-item {
      text-align: center;
      padding: 8px;
      background: rgba(255, 255, 255, 0.05);
      border-radius: 6px;
      transition: all 0.3s ease;
      
      &:hover {
        background: rgba(255, 255, 255, 0.1);
      }
      
      .stats-value {
        font-size: 16px;
        font-weight: 600;
        color: #fff;
        margin-bottom: 2px;
      }
      
      .stats-label {
        font-size: 10px;
        color: rgba(255, 255, 255, 0.7);
      }
    }
  }
}

// 响应式布局优化
@media (min-width: 768px) {
  .enhanced-sections {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
    width: 95%;
    
    .badges-section,
    .interests-section {
      grid-column: span 1;
    }
    
    .activities-section,
    .statistics-section {
      grid-column: span 1;
    }
  }
  
  .statistics-section .stats-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (min-width: 1024px) {
  .user-info-container {
    width: 95%;
  }
  
  .enhanced-sections {
    width: 95%;
  }
}
</style>
