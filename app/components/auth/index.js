/**
 * 认证组件模块
 * @module components/auth
 * @description 提供登录、注册相关的UI组件
 */

import AuthContainer from './AuthContainer.vue'
import LoginForm from './LoginForm.vue'
import RegisterForm from './RegisterForm.vue'

/**
 * 认证容器组件
 * @type {VueComponent}
 * @description 认证页面的外层容器，提供统一的背景和布局
 */

/**
 * 登录表单组件
 * @type {VueComponent}
 * @description 包含用户名、密码输入和登录按钮的表单组件
 */

/**
 * 注册表单组件
 * @type {VueComponent}
 * @description 包含用户名、密码、确认密码和协议勾选的表单组件
 */

export {
  AuthContainer,
  LoginForm,
  RegisterForm
}

export default {
  AuthContainer,
  LoginForm,
  RegisterForm
}
