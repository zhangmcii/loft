export default {
  // 地区码转为地区名称
  getCodeToName(code, areaList) {
    const provinceCode = code.substring(0, 2) + "0000";
    const cityCode = code.substring(0, 4) + "00";
    const countyCode = code;

    const provinceName = areaList.province_list[provinceCode];
    const cityName = areaList.city_list[cityCode];
    const countyName = areaList.county_list[countyCode];

    let [p1, p2, p3] = [provinceName, cityName, countyName];

    // 去掉末尾的“省”、“市”、“区”等
    const trimSuffix = (str) =>
      str.replace(
        /省|市|区|特别行政区|回族自治区|壮族自治区|维吾尔自治区|自治区/g,
        ""
      );

    // 直辖市列表
    const municipalities = ["北京市", "上海市", "天津市", "重庆市"];

    // 自治区映射（只保留前两个字）
    const autonomousMap = {
      新疆维吾尔自治区: "新疆",
      内蒙古自治区: "内蒙古",
      广西壮族自治区: "广西",
      宁夏回族自治区: "宁夏",
      西藏自治区: "西藏",
    };

    // 港澳台
    const specialRegions = ["台湾省", "香港特别行政区", "澳门特别行政区"];

    // 1) 直辖市：取后两个部分
    if (municipalities.includes(p1)) {
      return `${trimSuffix(p2)} ${p3}`;
    }

    // 2) 港澳台：取前两个部分
    if (specialRegions.includes(p1)) {
      return `${trimSuffix(p1)} ${trimSuffix(p2)}`;
    }

    // 3) 自治区：使用缩写
    if (autonomousMap[p1]) {
      return `${autonomousMap[p1]} ${trimSuffix(p2)}`;
    }

    // 4) 普通省份：取前两部分
    return `${trimSuffix(p1)} ${trimSuffix(p2)}`;
  },

  // 地区名称转为地区码
  getNameToCode(areaName, areaList) {
    const areaNames = areaName.split("/"); // 将地区名字按'/'分割为数组
    let code = null;

    // 查找省份地区码
    for (const [provinceCode, provinceName] of Object.entries(
      areaList.province_list
    )) {
      if (provinceName === areaNames[0]) {
        code = provinceCode.slice(0, 2);
        break;
      }
    }
    if (code === null) return null; // 如果省份不存在，则返回null

    // 查找城市地区码
    for (const [cityCode, cityName] of Object.entries(areaList.city_list)) {
      if (cityName === areaNames[1]) {
        code += cityCode.slice(2, 4); // 将省份码与城市码组合
        break;
      }
    }
    if (code === null) return null; // 如果城市不存在，则返回null
    // 查找区县地区码
    for (const [countyCode, countyName] of Object.entries(
      areaList.county_list
    )) {
      if (countyName === areaNames[2]) {
        code += countyCode.slice(4, 6); // 将城市码与区县码组合
        break;
      }
    }
    return code; // 返回完整的地区码
  },
};
