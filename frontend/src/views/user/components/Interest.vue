<script>
import InterestPage from "@/views/user/components/InterestPage.vue";
export default {
  props: {
    interest: {
      type: Object,
      default() {
        return {
          movies: [],
          books: [],
        };
      },
    },
    showInterest: {
      type: String,
      default: "",
    },
    showButton: {
      type: Boolean,
      default: false,
    },
  },
  components: {
    InterestPage,
  },
  data() {
    return {
      activeName: "first",
      name: ["苦尽甘来遇见你", "我的大叔", "黑化律师"],
      preList: [],
    };
  },
  watch: {},
  computed: {},
  mounted() {},
  methods: {},
};
</script>

<template>
  <div class="container">
    <InterestPage :interest="interest.movies" v-if="showInterest == 'movie'" />
    <InterestPage :interest="interest.books" v-if="showInterest == 'book'" />
  </div>
</template>
<style lang="scss" scoped>
.container {
  position: relative;
  height: 170px;
}
</style>
