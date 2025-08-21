export default {
    // 地区码转为地区名称
  getCodeToName(code, areaList) {
    const provinceCode = code.substring(0, 2) + '0000'
    const cityCode = code.substring(0, 4) + '00'
    const countyCode = code
    // 获取省、市、区的名字
    const provinceName = areaList.province_list[provinceCode]
    const cityName = areaList.city_list[cityCode]
    const countyName = areaList.county_list[countyCode]
    // 拼接省市区名字
    return `${provinceName}/${cityName}/${countyName}`
  },
// 地区名称转为地区码
  getNameToCode(areaName, areaList) {
    const areaNames = areaName.split('/') // 将地区名字按'/'分割为数组
    let code = null

    // 查找省份地区码
    for (const [provinceCode, provinceName] of Object.entries(areaList.province_list)) {
      if (provinceName === areaNames[0]) {
        code = provinceCode.slice(0, 2)
        break
      }
    }
    if (code === null) return null // 如果省份不存在，则返回null

    // 查找城市地区码
    for (const [cityCode, cityName] of Object.entries(areaList.city_list)) {
      if (cityName === areaNames[1]) {
        code += cityCode.slice(2, 4) // 将省份码与城市码组合
        break
      }
    }
    if (code === null) return null // 如果城市不存在，则返回null
    // 查找区县地区码
    for (const [countyCode, countyName] of Object.entries(areaList.county_list)) {
      if (countyName === areaNames[2]) {
        code += countyCode.slice(4, 6) // 将城市码与区县码组合
        break
      }
    }
    return code // 返回完整的地区码
  }
}
