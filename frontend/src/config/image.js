import logOut from "../asset/logOut.png";
import cherry from "../asset/cherry5.jpg";
import loading from "../asset/loading.gif";
// import imageApi from '@/api/user/imageApi.js'

// function getRandomImage() {
//   return imageApi.getBackgroundImage(1, 10, 'userAvatars/', 0).then((res) => {
//     if (res.code === 200 && res.data?.length) {
//       const avatarts = [...res.data]
//       // 确保数组不为空
//       const randomIndex = Math.floor(Math.random() * avatarts.length)
//       return avatarts[randomIndex]
//     }
//     return null
//   })
// }

const imageCfg = {
  // random: getRandomImage,
  // login: 'https://www.helloimg.com/i/2025/01/15/6787d90f29c4f.jpg',
  login: cherry,
  loginFail: cherry,
  logOut: logOut,
  preLoading: loading,
};
export default imageCfg;
