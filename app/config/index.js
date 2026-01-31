/**
 * 应用配置模块
 * @module config
 * @description 管理应用的环境配置，包括API地址、存储前缀、功能开关等
 */

import developmentConfig from './development.json'
import productionConfig from './production.json'

const env = process.env.NODE_ENV || 'development'
const config = env === 'production' ? productionConfig : developmentConfig

/**
 * 应用配置对象
 * @typedef {Object} AppConfig
 * @property {string} env - 当前环境
 * @property {Object} api - API配置
 * @property {string} api.baseURL - API基础地址
 * @property {number} api.timeout - 请求超时时间
 * @property {number} api.retry - 重试次数
 * @property {Object} storage - 存储配置
 * @property {string} storage.prefix - 存储键前缀
 * @property {Object} features - 功能开关
 * @property {boolean} features.enableLog - 是否启用日志
 * @property {boolean} features.enableMock - 是否启用Mock
 * @property {boolean} features.enableSentry - 是否启用Sentry
 */

/**
 * 获取完整配置对象
 * @returns {AppConfig} 应用配置对象
 * @example
 * const config = getConfig()
 * console.log(config.api.baseURL)
 */
export const getConfig = () => config

/**
 * 获取API基础地址
 * @returns {string} API基础地址
 * @example
 * const baseURL = getApiBaseURL()
 * // 开发环境: http://localhost:8000
 * // 生产环境: https://api.example.com
 */
export const getApiBaseURL = () => config.api.baseURL

/**
 * 获取带前缀的存储键
 * @param {string} key - 原始键名
 * @returns {string} 带前缀的存储键
 * @example
 * const storageKey = getStorageKey('access_token')
 * // 开发环境: mes_dev_access_token
 * // 生产环境: mes_access_token
 */
export const getStorageKey = (key) => `${config.storage.prefix}${key}`

/**
 * 是否为调试模式
 * @returns {boolean} 是否为开发环境
 * @example
 * if (isDebug()) {
 *   console.log('调试信息')
 * }
 */
export const isDebug = () => config.env === 'development'

/**
 * 检查功能是否启用
 * @param {string} feature - 功能名称
 * @returns {boolean} 功能是否启用
 * @example
 * if (isFeatureEnabled('enableLog')) {
 *   console.log('日志已启用')
 * }
 */
export const isFeatureEnabled = (feature) => config.features[feature] || false

export default config
