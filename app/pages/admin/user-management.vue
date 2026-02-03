<template>
  <view class="page">
    <UserManagement />
  </view>
</template>

<script>
import UserManagement from '@/components/admin/UserManagement.vue'

/**
 * 用户管理页面（管理员专属）
 * @description 管理员用户管理入口页面
 */
export default {
  components: {
    UserManagement
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
