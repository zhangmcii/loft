import dayjs from "@/config/dayjsCfg";

// 灰度日配置
export const grayscaleDays = [
  "04-04", // 清明节（可能浮动）
  "12-13", // 南京大屠杀国家公祭日
];

// 启用灰度滤镜
export function enableGrayscale() {
  const today = dayjs();
  const monthDay = today.format("MM-DD");

  if (grayscaleDays.includes(monthDay)) {
    document.documentElement.style.filter = "grayscale(100%)";
  }
}
