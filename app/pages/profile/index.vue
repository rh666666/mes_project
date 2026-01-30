<template>
  <view class="page">
    <view class="content">
      <!-- 登录表单模板 -->
      <view class="login-container">

        
        <view class="login-form">
          <view class="form-item">
            <text class="form-label">账号</text>
            <input 
              class="form-input" 
              type="text" 
              placeholder="请输入账号"
            />
          </view>
          
          <view class="form-item">
            <text class="form-label">密码</text>
            <input 
              class="form-input" 
              type="password" 
              placeholder="请输入密码"
            />
          </view>
          
          <view class="form-actions">
            <view class="remember-forgot">
              <label class="checkbox-label">
                <checkbox />
                <text>记住我</text>
              </label>
              <text class="forgot-password">忘记密码？</text>
            </view>
            
            <button class="login-btn">登录</button>
          </view>
        </view>
      </view>
    </view>
    <BottomNavBar :current-path="currentPath" @nav-change="onNavChange"></BottomNavBar>
  </view>
</template>

<script>
  import BottomNavBar from '@/components/BottomNavBar.vue';

  export default {
    components: {
      BottomNavBar
    },
    data() {
      return {
        currentPath: '/pages/profile/index'
      };
    },
    onLoad() {},
    methods: {
      onNavChange(item) {
        console.log('导航切换到:', item);
      }
    }
  };
</script>

<style lang="scss">
  .page {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    background-color: $uni-bg-color-grey;
    padding-bottom: calc(100rpx + env(safe-area-inset-bottom));
    box-sizing: border-box;
  }

  .content {
    flex: 1;
    padding: 40rpx;
  }

  .login-container {
    max-width: 500px;
    margin: 0 auto;
    padding: 40rpx;
    background-color: $uni-bg-color;
    border-radius: 12rpx;
    box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.08);
  }



  .login-form {
    margin-bottom: 32rpx;
  }

  .form-item {
    margin-bottom: 28rpx;
  }

  .form-label {
    display: block;
    font-size: 24rpx;
    font-weight: 500;
    color: $uni-text-color;
    margin-bottom: 12rpx;
  }

  .form-input {
    width: 100%;
    height: 80rpx;
    padding: 0 24rpx;
    background-color: $uni-bg-color;
    border: 1rpx solid $uni-border-color;
    border-radius: 8rpx;
    font-size: 24rpx;
    color: $uni-text-color;
    box-sizing: border-box;
  }

  .form-input::placeholder {
    color: $uni-text-color-placeholder;
  }

  .form-actions {
    margin-top: 40rpx;
  }

  .remember-forgot {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 32rpx;
  }

  .checkbox-label {
    display: flex;
    align-items: center;
    gap: 8rpx;
    font-size: 22rpx;
    color: $uni-text-color-grey;
  }

  .forgot-password {
    font-size: 22rpx;
    color: $uni-color-primary;
  }

  .login-btn {
    width: 100%;
    height: 80rpx;
    background-color: $uni-color-primary;
    color: white;
    border: none;
    border-radius: 8rpx;
    font-size: 28rpx;
    font-weight: 500;
  }

  .login-btn::after {
    border: none;
  }

  .placeholder-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40rpx;
  }

  .placeholder-title {
    font-size: 48rpx;
    font-weight: 600;
    color: $uni-text-color;
    margin-bottom: 20rpx;
  }

  .placeholder-desc {
    font-size: 28rpx;
    color: $uni-text-color-grey;
  }
</style>