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
		color: $uni-text-color;
		background-color: $uni-bg-color;
		-webkit-font-smoothing: antialiased;
		-moz-osx-font-smoothing: grayscale;
	}

	/* 页面基础样式 */
	.page {
		display: flex;
		flex-direction: column;
		min-height: 100vh;
		background-color: $uni-bg-color;
		padding-bottom: calc(100rpx + env(safe-area-inset-bottom));
		box-sizing: border-box;
	}

	.content {
		flex: 1;
		padding: 32rpx;
	}
</style>
