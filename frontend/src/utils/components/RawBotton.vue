<template>
  <button class="emoji-button1">按钮</button>
</template>
<script>
export default {
  props: {
    showEmoji: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {}
  },
  methods: {}
}
</script>
<style scoped>
.emoji-button1 {
  display: inline-block;
  font-size: 1rem;
  background-color: transparent;
  border-radius: 50%;
  border: none;
  cursor: pointer;
  position: relative;
  transition: all 0.5s;
}
.emoji-button1:hover {
  transform: scale(1.2);
}
</style>
