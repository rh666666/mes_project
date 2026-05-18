<template>
  <view class="page">
    <view class="content">
      <!-- 技能信息 -->
      <view class="section-header">
        <text class="section-title">基本信息</text>
      </view>
      <wd-cell-group>
        <wd-input
          v-model="form.code"
          label="技能编码"
          placeholder="请输入技能编码"
          :maxlength="100"
          clearable
        />
        <wd-input
          v-model="form.name"
          label="技能名称"
          placeholder="请输入技能名称"
          :maxlength="100"
          clearable
        />
        <wd-picker
          v-model="form.type"
          label="技能类型"
          placeholder="请选择技能类型"
          :columns="typeColumns"
        />
      </wd-cell-group>
    </view>

    <!-- 底部操作区 -->
    <view class="actions">
      <wd-button type="primary" size="large" :loading="isSaving" @click="onSave">
        {{ isSaving ? '保存中...' : '保存' }}
      </wd-button>
      <wd-button
        v-if="!isCreating"
        type="danger"
        size="large"
        plain
        @click="onDelete"
      >
        删除技能
      </wd-button>
    </view>
  </view>
</template>

<script>
import skillApi, { SkillType, SkillTypeLabel } from '@/api/skill'
import { hideAppLoading, showAppLoading } from '@/utils/loading.js'

/**
 * 技能编辑/创建页面
 * @component
 * @description 提供技能信息的编辑和创建功能
 */
export default {
  name: 'SkillEdit',

  data() {
    return {
      /** @type {boolean} 是否是创建模式 */
      isCreating: false,
      /** @type {number|null} 技能ID（编辑模式） */
      skillId: null,
      /** @type {Object} 表单数据 */
      form: {
        code: '',
        name: '',
        type: SkillType.USER
      },
      /** @type {boolean} 是否正在保存 */
      isSaving: false,
      /** @type {Array} 技能类型选项列表 */
      typeColumns: [
        { value: SkillType.USER, label: SkillTypeLabel[SkillType.USER] },
        { value: SkillType.DEVICE, label: SkillTypeLabel[SkillType.DEVICE] }
      ]
    }
  },

  onLoad(options) {
    if (options.id) {
      this.isCreating = false
      this.skillId = parseInt(options.id)
      this.loadSkillDetail()
    } else {
      this.isCreating = true
      this.skillId = null
      this.form.type = SkillType.USER
    }
  },

  methods: {
    /**
     * 加载技能详情
     * @async
     */
    async loadSkillDetail() {
      showAppLoading({ title: '加载中...' })
      try {
        const res = await skillApi.getSkillDetail(this.skillId)
        if (res.code === 2000) {
          const skill = res.data
          this.form = {
            code: skill.code || '',
            name: skill.name || '',
            type: skill.type || SkillType.USER
          }
        } else {
          uni.showToast({
            title: res.msg || '获取技能信息失败',
            icon: 'none'
          })
        }
      } catch (error) {
        console.error('获取技能详情失败:', error)
        uni.showToast({
          title: error.msg || '获取技能信息失败',
          icon: 'none'
        })
      } finally {
        hideAppLoading()
      }
    },

    /**
     * 保存技能
     * @async
     */
    async onSave() {
      if (!this.form.code.trim()) {
        uni.showToast({
          title: '请输入技能编码',
          icon: 'none'
        })
        return
      }
      if (!this.form.name.trim()) {
        uni.showToast({
          title: '请输入技能名称',
          icon: 'none'
        })
        return
      }
      if (!this.form.type) {
        uni.showToast({
          title: '请选择技能类型',
          icon: 'none'
        })
        return
      }

      this.isSaving = true

      try {
        let res
        const data = {
          code: this.form.code.trim(),
          name: this.form.name.trim(),
          type: this.form.type
        }

        if (this.isCreating) {
          res = await skillApi.createSkill(data)
        } else {
          res = await skillApi.updateSkill(this.skillId, data)
        }

        if (res.code === 2000) {
          uni.showToast({
            title: this.isCreating ? '创建成功' : '保存成功',
            icon: 'success'
          })
          uni.navigateBack()
        } else {
          uni.showToast({
            title: res.msg || (this.isCreating ? '创建失败' : '保存失败'),
            icon: 'none'
          })
        }
      } catch (error) {
        console.error(this.isCreating ? '创建技能失败:' : '保存技能失败:', error)
        uni.showToast({
          title: error.msg || (this.isCreating ? '创建失败' : '保存失败'),
          icon: 'none'
        })
      } finally {
        this.isSaving = false
      }
    },

    /**
     * 显示删除确认弹窗
     */
    onDelete() {
      uni.showModal({
        title: '确认删除',
        content: `确定要删除技能 "${this.form.name}" 吗？此操作不可恢复。`,
        confirmText: '删除',
        confirmColor: '#ee0a24',
        success: (res) => {
          if (res.confirm) {
            this.onConfirmDelete()
          }
        }
      })
    },

    /**
     * 确认删除
     * @async
     */
    async onConfirmDelete() {
      if (!this.skillId) return

      showAppLoading({ title: '删除中...' })
      try {
        const res = await skillApi.deleteSkill(this.skillId)
        if (res.code === 2000) {
          uni.showToast({
            title: '删除成功',
            icon: 'success'
          })
          uni.navigateBack()
        } else {
          uni.showToast({
            title: res.msg || '删除失败',
            icon: 'none'
          })
        }
      } catch (error) {
        console.error('删除技能失败:', error)
        uni.showToast({
          title: error.msg || '删除失败',
          icon: 'none'
        })
      } finally {
        hideAppLoading()
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.page {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: $uni-bg-color;
  box-sizing: border-box;
}

.content {
  flex: 1;
  padding: 24rpx;
}

.section-header {
  margin: 32rpx 0 24rpx;
}

.section-title {
  font-size: 26rpx;
  font-weight: 400;
  color: $uni-text-color-grey;
}



.actions {
  padding: 24rpx;
  background-color: $uni-bg-color-white;
  border-top: 1px solid $uni-border-color;
  display: flex;
  flex-direction: column;
  gap: 24rpx;

  :deep(.wd-button) {
    width: 100%;
  }
}
</style>
