<script>
	export default {
		onLaunch: function() {
			console.log('App Launch')
		},
		onShow: function() {
			console.log('App Show')
		},
		onHide: function() {
			console.log('App Hide')
		}
	}
</script>

<style lang="scss">
	/* 全局样式重置 */
	* {
		margin: 0;
		padding: 0;
		box-sizing: border-box;
	}

	body {
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
		font-size: $uni-font-size-base;
		line-height: 1.5;
		color: $uni-md-text-primary;
		background-color: $uni-md-background;
		-webkit-font-smoothing: antialiased;
		-moz-osx-font-smoothing: grayscale;
	}

	/* 基础样式定义 */
	.page {
		display: flex;
		flex-direction: column;
		min-height: 100vh;
		background-color: $uni-md-background;
		padding-bottom: calc(100rpx + env(safe-area-inset-bottom));
		box-sizing: border-box;
	}

	.content {
		flex: 1;
		padding: $uni-md-space-md;
	}

	/* 通用标题样式 */
	.title {
		font-size: $uni-font-size-title;
		font-weight: 600;
		color: $uni-md-text-primary;
		margin-bottom: $uni-md-space-sm;
	}

	.subtitle {
		font-size: $uni-font-size-subtitle;
		font-weight: 500;
		color: $uni-md-text-secondary;
		margin-bottom: $uni-md-space-md;
	}

	/* 通用按钮样式 */
	.btn {
		@include uni-md-button;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		font-size: $uni-font-size-base;
		font-weight: 500;
		border: none;
		outline: none;
		cursor: pointer;
		transition: all $uni-md-animation-fast ease;
	}

	.btn-primary {
		@include uni-md-button($uni-md-color-primary);
	}

	.btn-secondary {
		@include uni-md-button($uni-md-color-secondary);
	}

	.btn-outline {
		background-color: transparent;
		color: $uni-md-color-primary;
		border: 1px solid $uni-md-color-primary;
		box-shadow: none;

		&:hover {
			background-color: rgba($uni-md-color-primary, 0.05);
		}
	}

	/* 通用卡片样式 */
	.card {
		@include uni-md-card;
		margin-bottom: $uni-md-space-md;
	}

	/* 通用输入框样式 */
	.input {
		@include uni-md-input;
		width: 100%;
		font-size: $uni-font-size-base;
	}

	/* 通用列表样式 */
	.list {
		background-color: $uni-md-surface;
		border-radius: $uni-md-radius-medium;
		overflow: hidden;
	}

	.list-item {
		padding: $uni-md-space-md;
		border-bottom: 1px solid $uni-md-divider;
		transition: background-color $uni-md-animation-fast ease;

		&:last-child {
			border-bottom: none;
		}

		&:hover {
			background-color: rgba($uni-md-color-primary, 0.02);
		}
	}

	/* 通用分割线样式 */
	.divider {
		height: 1px;
		background-color: $uni-md-divider;
		margin: $uni-md-space-md 0;
	}

	/* 通用加载状态样式 */
	.loading {
		display: flex;
		align-items: center;
		justify-content: center;
		padding: $uni-md-space-lg;
		color: $uni-md-text-secondary;
	}

	/* 通用错误提示样式 */
	.error {
		padding: $uni-md-space-md;
		background-color: rgba($uni-color-error, 0.1);
		color: $uni-color-error;
		border-radius: $uni-md-radius-small;
		margin-bottom: $uni-md-space-md;
	}

	/* 通用成功提示样式 */
	.success {
		padding: $uni-md-space-md;
		background-color: rgba($uni-color-success, 0.1);
		color: $uni-color-success;
		border-radius: $uni-md-radius-small;
		margin-bottom: $uni-md-space-md;
	}

	/* 响应式设计 */
	@media (max-width: 768px) {
		.content {
			padding: $uni-md-space-sm;
		}

		.title {
			font-size: calc(#{$uni-font-size-title} * 0.9);
		}

		.subtitle {
			font-size: calc(#{$uni-font-size-subtitle} * 0.9);
		}
	}

	/* 过渡动画效果 */
	.fade-enter-active,
	.fade-leave-active {
		transition: opacity $uni-md-animation-normal ease;
	}

	.fade-enter-from,
	.fade-leave-to {
		opacity: 0;
	}

	.slide-up-enter-active,
	.slide-up-leave-active {
		transition: all $uni-md-animation-normal ease;
	}

	.slide-up-enter-from {
		transform: translateY(20rpx);
		opacity: 0;
	}

	.slide-up-leave-to {
		transform: translateY(-20rpx);
		opacity: 0;
	}

	.slide-down-enter-active,
	.slide-down-leave-active {
		transition: all $uni-md-animation-normal ease;
	}

	.slide-down-enter-from {
		transform: translateY(-20rpx);
		opacity: 0;
	}

	.slide-down-leave-to {
		transform: translateY(20rpx);
		opacity: 0;
	}

	.scale-enter-active,
	.scale-leave-active {
		transition: all $uni-md-animation-fast ease;
	}

	.scale-enter-from,
	.scale-leave-to {
		transform: scale(0.95);
		opacity: 0;
	}

	/* 页面加载动画 */
	.page-loading {
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: 100vh;
		background-color: $uni-md-background;
	}

	.loading-spinner {
		width: 80rpx;
		height: 80rpx;
		border: 8rpx solid $uni-md-surface-variant;
		border-top: 8rpx solid $uni-md-color-primary;
		border-radius: 50%;
		animation: spin $uni-md-animation-normal linear infinite;
	}

	@keyframes spin {
		0% { transform: rotate(0deg); }
		100% { transform: rotate(360deg); }
	}

	/* 按钮点击动画 */
	.btn {
		&:active {
			animation: button-press $uni-md-animation-fast ease-in-out;
		}
	}

	@keyframes button-press {
		0% {
			transform: scale(1);
		}
		50% {
			transform: scale(0.96);
		}
		100% {
			transform: scale(1);
		}
	}

	/* 列表项动画 */
	.list-item {
		transition: all $uni-md-animation-fast ease;

		&:hover {
			background-color: rgba($uni-md-color-primary, 0.05);
		}

		&:active {
			transform: scale(0.98);
		}
	}

	/* 输入框动画 */
	.form-input {
		transition: all $uni-md-animation-fast ease;

		&:focus {
			transform: translateY(-2rpx);
			box-shadow: 0 2rpx 8rpx rgba($uni-md-color-primary, 0.1);
		}
	}

	/* 卡片动画 */
	.card {
		transition: all $uni-md-animation-normal ease;

		&:hover {
			transform: translateY(-4rpx);
			box-shadow: $uni-md-shadow-md;
		}
	}
</style>
