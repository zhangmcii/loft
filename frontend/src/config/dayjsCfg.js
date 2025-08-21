import dayjs from 'dayjs'

import zhCN from 'dayjs/locale/zh-cn'
// dayjs语言配置为中文
dayjs.locale(zhCN)

import relativeTime from 'dayjs/plugin/relativeTime'
// 引入RelativeTime插件
dayjs.extend(relativeTime)

// 设置时区
import utc  from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone' 
dayjs.extend(utc)
dayjs.extend(timezone)

import updateLocale from 'dayjs/plugin/updateLocale'
dayjs.extend(updateLocale)

dayjs.updateLocale('zh-cn', {
  relativeTime: {
    future: '%s后',
    past: '%s前',
    s: '几秒',
    m: '1分钟',
    mm: '%d分钟',
    h: '1小时',
    hh: '%d小时',
    dd: '%d天',
    M: '1个月',
    MM: '%d月',
    y: '1年',
    yy: '%d年'
  }
})

export default dayjs