<template>
  <view class="page">
    <!-- 搜索和筛选区域 -->
    <view class="filter-section">
      <wd-search
        v-model="searchKeyword"
        placeholder="搜索设备名称"
        @search="onSearch"
        @clear="onClearSearch"
      />

      <!-- 状态筛选 -->
      <view class="status-filter">
        <wd-tabs v-model="selectedStatus">
          <wd-tab title="全部" name="all" />
          <wd-tab
            v-for="status in statusOptions"
            :key="status.value"
            :title="status.label"
            :name="status.value"
          />
        </wd-tabs>
      </view>

      <!-- 结果统计 -->
      <view v-if="!isLoading" class="results-stats">
        <text class="stats-text">共 {{ deviceList.length }} 台设备</text>
        <wd-tag v-if="searchKeyword || (selectedStatus && selectedStatus !== 'all')" type="primary" size="small">已筛选</wd-tag>
      </view>
    </view>

    <!-- 设备列表 -->
    <scroll-view
      scroll-y
      class="device-list"
      :refresher-enabled="scrollTop <= 10"
      :refresher-triggered="isRefreshing"
      @refresherrefresh="onRefresh"
      @scrolltolower="onLoadMore"
      @scroll="onScroll"
    >
      <wd-cell-group>
        <wd-cell
          v-for="(device, index) in deviceList"
          :key="device.id"
          :title="device.name"
          :label="device.code"
          clickable
          @click="onDeviceClick(device)"
        >
          <template #value>
            <wd-tag
              :color="getStatusColor(device.status)"
              size="small"
              round
            >
              {{ getStatusLabel(device.status) }}
            </wd-tag>
          </template>
        </wd-cell>
      </wd-cell-group>

      <wd-loadmore :state="loadMoreState" />

      <wd-status-tip v-if="deviceList.length === 0 && !isLoading" image="search" tip="暂无设备数据" />
    </scroll-view>

    <!-- 加载状态 -->
    <view v-if="isLoading || isRefreshing" class="loading-overlay">
      <wd-loading />
    </view>

    <!-- FAB 按钮 -->
    <view class="fab-container" @click="onCreateDevice">
      <wd-button round type="primary">
        <wd-icon name="add" size="24" color="#fff" />
      </wd-button>
    </view>
  </view>
</template>

<script>
import deviceApi, { DeviceStatus, DeviceStatusLabel } from '@/api/device.js'

/**
 * 设备状态颜色映射
 * @readonly
 * @type {Object.<string, string>}
 */
const StatusColorMap = {
  [DeviceStatus.IDLE]: '#07c160',
  [DeviceStatus.RUNNING]: '#1989fa',
  [DeviceStatus.ERROR]: '#ee0a24'
}

/**
 * 设备管理页面（管理员专属）
 * @description 提供设备列表查看、创建、编辑和删除功能，点击跳转到独立编辑页面
 */
export default {
  data() {
    return {
      /** @type {Array} 设备列表 */
      deviceList: [],
      /** @type {boolean} 是否正在加载 */
      isLoading: false,
      /** @type {boolean} 是否正在刷新 */
      isRefreshing: false,
      /** @type {boolean} 是否正在加载更多 */
      isLoadingMore: false,
      /** @type {string} 搜索关键词 */
      searchKeyword: '',
      /** @type {string} 选中的状态筛选 */
      selectedStatus: 'all',
      /** @type {number|null} 搜索防抖定时器 */
      searchDebounceTimer: null,
      /** @type {number} 当前页码 */
      currentPage: 1,
      /** @type {number} 每页数量 */
      pageSize: 10,
      /** @type {number} 总数量 */
      total: 0,
      /** @type {boolean} 是否还有更多数据 */
      hasMore: true,
      /** @type {number} 滚动位置 */
      scrollTop: 0,
      /** @type {Array} 状态选项列表 */
      statusOptions: [
        { value: DeviceStatus.IDLE, label: DeviceStatusLabel[DeviceStatus.IDLE] },
        { value: DeviceStatus.RUNNING, label: DeviceStatusLabel[DeviceStatus.RUNNING] },
        { value: DeviceStatus.ERROR, label: DeviceStatusLabel[DeviceStatus.ERROR] }
      ],
      /** @type {boolean} 是否是首次加载 */
      isFirstLoad: true
    }
  },

  computed: {
    /**
     * 加载更多状态
     * @returns {string}
     */
    loadMoreState() {
      if (this.isLoadingMore) return 'loading'
      if (!this.hasMore && this.deviceList.length > 0) return 'finished'
      return 'default'
    }
  },

  watch: {
    /**
     * 监听状态筛选变化
     */
    selectedStatus(newVal, oldVal) {
      if (newVal !== oldVal) {
        this.loadDeviceList()
      }
    }
  },

  onLoad() {
    this.loadDeviceList()
  },

  onShow() {
    if (!this.isFirstLoad) {
      this.loadDeviceList()
    }
    this.isFirstLoad = false
  },

  onUnload() {
    if (this.searchDebounceTimer) {
      clearTimeout(this.searchDebounceTimer)
    }
  },

  methods: {
    /**
     * 获取状态颜色
     * @param {string} status - 状态值
     * @returns {string} 颜色值
     */
    getStatusColor(status) {
      return StatusColorMap[status] || '#969799'
    },

    /**
     * 获取状态标签
     * @param {string} status - 状态值
     * @returns {string} 状态标签
     */
    getStatusLabel(status) {
      return DeviceStatusLabel[status] || status
    },

    /**
     * 加载设备列表
     * @async
     * @param {boolean} [isLoadMore=false] - 是否是加载更多
     */
    async loadDeviceList(isLoadMore = false) {
      if (isLoadMore) {
        this.isLoadingMore = true
      } else {
        this.isLoading = true
        this.currentPage = 1
        this.hasMore = true
      }

      try {
        const params = {
          page: this.currentPage,
          limit: this.pageSize
        }
        if (this.searchKeyword) {
          params.name = this.searchKeyword
        }
        if (this.selectedStatus && this.selectedStatus !== 'all') {
          params.status = this.selectedStatus
        }

        const res = await deviceApi.getDeviceList(params)
        if (res.code === 2000) {
          const newData = res.data || []
          this.total = res.total || 0

          if (isLoadMore) {
            this.deviceList = [...this.deviceList, ...newData]
          } else {
            this.deviceList = newData
          }

          this.hasMore = this.deviceList.length < this.total
        } else {
          uni.showToast({
            title: res.msg || '获取设备列表失败',
            icon: 'none'
          })
        }
      } catch (error) {
        console.error('获取设备列表失败:', error)
        uni.showToast({
          title: error.msg || '获取设备列表失败',
          icon: 'none'
        })
      } finally {
        this.isLoading = false
        this.isRefreshing = false
        this.isLoadingMore = false
      }
    },

    /**
     * 刷新设备列表
     */
    onRefresh() {
      this.isRefreshing = true
      this.currentPage = 1
      this.hasMore = true
      this.loadDeviceList(false)
    },

    /**
     * 加载更多数据
     */
    async onLoadMore() {
      if (!this.hasMore || this.isLoadingMore || this.isLoading) {
        return
      }
      this.currentPage++
      await this.loadDeviceList(true)
    },

    /**
     * 搜索处理（防抖）
     */
    onSearch() {
      if (this.searchDebounceTimer) {
        clearTimeout(this.searchDebounceTimer)
      }
      this.searchDebounceTimer = setTimeout(() => {
        this.loadDeviceList()
      }, 300)
    },

    /**
     * 清除搜索
     */
    onClearSearch() {
      this.searchKeyword = ''
      this.loadDeviceList()
    },

    /**
     * 点击创建设备按钮 - 跳转到创建页面
     */
    onCreateDevice() {
      uni.navigateTo({
        url: '/pages/admin/device/edit'
      })
    },

    /**
     * 点击设备项 - 跳转到编辑页面
     * @param {Object} device - 设备对象
     */
    onDeviceClick(device) {
      uni.navigateTo({
        url: `/pages/admin/device/edit?id=${device.id}`
      })
    },

    /**
     * 滚动事件处理
     * @param {Object} e - 滚动事件对象
     */
    onScroll(e) {
      this.scrollTop = e.detail.scrollTop
    }
  }
}
</script>

<style lang="scss" scoped>
.page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: $uni-bg-color;
}

.filter-section {
  padding: 24rpx;
  background-color: $uni-bg-color-white;
  border-bottom: 1px solid $uni-border-color;
  position: sticky;
  top: var(--window-top, 0);
  z-index: 100;
}

.status-filter {
  margin-top: 24rpx;
}

.results-stats {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-top: 24rpx;
  padding-top: 24rpx;
  border-top: 1px solid $uni-border-color;
}

.stats-text {
  font-size: 24rpx;
  color: $uni-text-color-grey;
}

.device-list {
  flex: 1;
  overflow-y: auto;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(255, 255, 255, 0.8);
  z-index: 1000;
}

.fab-container {
  position: fixed;
  right: 32rpx;
  bottom: calc(32rpx + env(safe-area-inset-bottom));
  z-index: 100;

  :deep(.wd-button) {
    min-width: 96rpx !important;
    max-width: 96rpx !important;
    width: 96rpx !important;
    height: 96rpx !important;
    padding: 0 !important;
    border-radius: 50% !important;
  }
}

</style>
