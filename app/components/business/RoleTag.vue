<template>
  <wd-tag :type="tagType" :size="size">{{ displayText }}</wd-tag>
</template>

<script>
/**
 * 角色标签组件
 * 用于展示用户角色，如管理员、普通用户等
 * 基于 wd-tag 组件封装
 */

export default {
  name: 'RoleTag',

  props: {
    /** 角色类型 */
    role: {
      type: String,
      required: true
    },
    /** 尺寸 */
    size: {
      type: String,
      default: 'medium'
    },
    /** 自定义显示文本 */
    customText: {
      type: String,
      default: ''
    }
  },

  computed: {
    /**
     * 角色显示文本映射
     * @returns {string}
     */
    displayText() {
      if (this.customText) {
        return this.customText
      }
      const roleTextMap = {
        admin: '管理员',
        user: '普通用户',
        vip: 'VIP用户',
        guest: '访客'
      }
      return roleTextMap[this.role] || this.role
    },

    /**
     * 角色对应的标签类型
     * @returns {string}
     */
    tagType() {
      const typeMap = {
        admin: 'danger',
        user: 'primary',
        vip: 'warning',
        guest: 'default'
      }
      return typeMap[this.role] || 'default'
    }
  }
}
</script>
