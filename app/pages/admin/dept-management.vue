<template>
  <view class="page">
    <DeptManagement />
  </view>
</template>

<script>
import DeptManagement from '@/components/admin/DeptManagement.vue'

/**
 * 部门管理页面（管理员专属）
 * @description 管理员部门管理入口页面
 */
export default {
  components: {
    DeptManagement
  }
}
</script>

<style lang="scss">
.page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: $uni-md-background;
}
</style>
