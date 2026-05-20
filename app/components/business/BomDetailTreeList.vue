<template>
  <view class="tree-wrapper">
    <wd-collapse v-model="activeNames">
      <wd-collapse-item
        v-for="item in detailList"
        :key="item.id"
        :name="String(item.id)"
        :title="item.material_name || item.material_code || `详情 ${item.id}`"
      >
        <view class="detail-card">
          <view class="detail-row">
            <text class="label">物料编码</text>
            <text class="value">{{ item.material_code || '-' }}</text>
          </view>
          <view class="detail-row">
            <text class="label">数量</text>
            <text class="value">{{ item.quantity }}</text>
          </view>
          <view class="detail-row">
            <text class="label">子物料 BOM</text>
            <text class="value">{{ formatSubBomDisplay(item) }}</text>
          </view>
          <view class="detail-actions">
            <wd-button size="small" type="danger" plain @click="$emit('delete', item)">删除</wd-button>
          </view>
        </view>
      </wd-collapse-item>
    </wd-collapse>

    <view v-if="detailList.length === 0" class="empty-wrapper">
      <wd-status-tip image="search" tip="暂无详情项" />
    </view>
  </view>
</template>

<script>
/**
 * BOM 详情可折叠树列表
 * @description 展示 BOM 详情项，支持展开收起与删除事件透出
 */
export default {
  name: 'BomDetailTreeList',

  props: {
    /**
     * 详情列表
     */
    detailList: {
      type: Array,
      default: () => []
    }
  },

  emits: ['delete'],

  data() {
    return {
      /** @type {Array<string>} 当前展开项 */
      activeNames: []
    }
  },

  methods: {
    /**
     * 子物料 BOM 展示文案
     * @param {Object} item - 详情项
     * @returns {string}
     */
    formatSubBomDisplay(item) {
      if (!item?.sub_bom) {
        return '无（叶子物料）'
      }
      const version = item.sub_bom_version || '-'
      const code = item.material_code || item.material_name || '-'
      return `${version} (${code})`
    }
  },

  watch: {
    /**
     * 详情变化时默认展开全部
     * @param {Array} list - 详情列表
     */
    detailList: {
      immediate: true,
      handler(list) {
        this.activeNames = (list || []).map((item) => String(item.id))
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.tree-wrapper {
  background-color: $uni-bg-color-white;
  border-radius: 16rpx;
  overflow: hidden;
}

.detail-card {
  padding: 16rpx 0;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12rpx 8rpx;
}

.label {
  color: $uni-text-color-grey;
  font-size: 24rpx;
}

.value {
  color: $uni-text-color;
  font-size: 26rpx;
}

.detail-actions {
  margin-top: 12rpx;
  display: flex;
  justify-content: flex-end;
}

.empty-wrapper {
  padding: 24rpx;
}
</style>
