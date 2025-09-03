检测表单修改本质就是：原始值和当前值是否相等。 相等说明未修改，不相等就是修改了
场景： 表单页的按钮在修改前后内容相同时需要变为禁用状态，因为没必要再次提交相同的内容。
检测一个或多个输入框内容发生变化

应用内很多页面有这种需求，比如昵称页，签名页，社交账号页修改(昵称、签名、社交账号内容前后未变化时按钮禁用)等。
这些页面的代码逻辑基本相同：定义一个变化标志变量，根据对比值修改前后是否相同来选择禁用按钮。每个页面都要写这样的逻辑，会有 3 个页面重复的逻辑代码，如果有更多的页， 会造成多余的逻辑。
能不能有一个函数，参数是传入需要跟踪的变量，返回一个变化标志变量呢？

xxx

// 监听整个对象的所有字段
const { isChange, changedFields } = useChange(formData, 'userInfo')

// 只监听特定字段
const { isChange, changedFields } = useChange(formData, 'userInfo', ['name', 'age'])

// 使用变更详情
watch(changedFields, (fields) => {
console.log('变更的字段：', Object.keys(fields))
})

监听单值变化：
const data = ref('123')
useChange(data)

const data = reactive({
type: 1,
localUserInfo: {
nickname: '',
about_me: '',
social_account: {
qq: '',
wechat: '',
bilibili: '',
github: '',
twitter: '',
email: ''
}
}
})
监听 reactive 对象某个字段：
useChange(data, 'localUserInfo.nickname')

监听 reactive 对象中嵌套对象整个对象的所有字段变化：
useChange(data, 'localUserInfo.social_account')

监听 reactive 对象中嵌套对象中特点对象变化，比如 bilibili 字段的变化：
useChange(data, 'localUserInfo.social_account',['bilibili'])
