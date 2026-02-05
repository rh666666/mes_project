<template>
  <view
    class="md-icon"
    :style="iconStyle"
    v-html="svgContent"
  />
</template>

<script>
import iconMap from './MdIcon.json'

/**
 * Material Design 图标组件
 * @component
 * @description 使用内嵌 SVG 图标替代 uni-icons
 */
export default {
  name: 'MdIcon',

  props: {
    /**
     * 图标类型
     * @type {string}
     */
    type: {
      type: String,
      required: true
    },

    /**
     * 图标尺寸
     * @type {number}
     * @default 48
     */
    size: {
      type: Number,
      default: 48
    },

    /**
     * 图标颜色
     * @type {string}
     */
    color: {
      type: String,
      default: ''
    }
  },

  computed: {
    /**
     * SVG 图标内容映射
     * @returns {string}
     */
    svgContent() {
      const iconColor = this.color || '#000000';
      const svgTemplate = iconMap[this.type] || iconMap['home'];
      // 使用 ${iconColor} 占位符替换为实际颜色
      return svgTemplate.replace(/\$\{iconColor\}/g, iconColor);
    },

    /**
     * 图标样式
     * @returns {Object}
     */
    iconStyle() {
      return {
        width: `${this.size}rpx`,
        height: `${this.size}rpx`,
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center'
      };
    }
  }
};
</script>

<style lang="scss" scoped>
.md-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  vertical-align: middle;

  :deep(svg) {
    width: 100%;
    height: 100%;
  }
}
</style>
