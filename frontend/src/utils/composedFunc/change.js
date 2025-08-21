import { ref, watch, isReactive, toRaw } from 'vue'

// 深度比较两个对象是否相等
function isDeepEqual(a, b) {
  // 处理原始值、null和undefined
  if (a === b) return true
  if (a === null || b === null) return a === b
  if (typeof a !== 'object' || typeof b !== 'object') return false

  // 处理数组
  if (Array.isArray(a) && Array.isArray(b)) {
    if (a.length !== b.length) return false
    return a.every((item, index) => isDeepEqual(item, b[index]))
  }

  // 处理对象
  const keysA = Object.keys(a)
  const keysB = Object.keys(b)
  if (keysA.length !== keysB.length) return false

  return keysA.every((key) => isDeepEqual(a[key], b[key]))
}

// 获取嵌套属性值
function getValue(obj, path) {
  if (!path) return obj?.value ?? obj
  return path.split('.').reduce((acc, cur) => acc?.[cur], obj)
}

/**
 * 监听对象或值的变化，支持深度检测
 * @param {Object|any} origin - 源对象
 * @param {String} keyPath - 嵌套路径
 * @param {Array} [watchFields] - 需要监听的字段列表，为空则监听所有字段
 * @returns {Object} - 返回包含isChange和changedFields的响应式对象
 */
export function useChange(origin, keyPath, watchFields = []) {
  const sourceValue = ref(getValue(origin, keyPath))
  // toRaw() 根据一个 Vue 创建的代理返回其原始对象
  // JSON.stringify() 将一个 JavaScript 对象或值转换为 JSON 字符
  // JSON.parse() 用来解析 JSON 字符串
  const initialValue = JSON.parse(JSON.stringify(toRaw(sourceValue.value)))
  const isChange = ref(false)
  const changedFields = ref({})

  // 监听源值变化
  watch(
    () => getValue(origin, keyPath),
    (newVal) => {
      if (isReactive(newVal)) {
        // 深度对象处理
        const fieldsToCheck = watchFields.length > 0 ? watchFields : Object.keys(newVal)
        let hasChanged = false
        const changes = {}

        fieldsToCheck.forEach((field) => {
          const newValue = newVal[field]
          const oldValue = initialValue[field]

          if (!isDeepEqual(newValue, oldValue)) {
            hasChanged = true
            changes[field] = {
              oldValue,
              newValue
            }
          }
        })

        isChange.value = hasChanged
        changedFields.value = changes
      } else {
        // 原始值处理
        isChange.value = newVal !== initialValue
      }
    },
    { immediate: true, deep: true }
  )

  return {
    isChange,
    changedFields
  }
}
