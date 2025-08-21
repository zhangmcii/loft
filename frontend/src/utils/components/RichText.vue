<script>
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
export default {
  props: {
    bodyInit: {
      default: null
    },
    bodyHtmlInit: {
      default: null
    }
  },
  components: { Editor, Toolbar },
  data() {
    return {
      editor: null,
      body: null,
      bodyHtml: null,
      toolbarConfig: {},
      editorConfig: { placeholder: '书写片段,温润流年。' },
      mode: 'default'
    }
  },
  mounted() {
    this.toolbarConfig.excludeKeys = ['group-image', 'group-video','insertTable','fullScreen']
  },
  methods: {
    onCreated(editor) {
      this.editor = Object.seal(editor)
      if (this.bodyInit) this.editor.insertText(this.bodyInit)
      if (this.bodyHtmlInit) this.editor.setHtml(this.bodyHtmlInit)
      // 监听内容变化
      editor.on('change', () => {
        this.body = this.editor.getText()
        this.$emit('content_change', { body: this.body, bodyHtml: this.bodyHtml })
      })
    },
    clean() {
      this.body = ''
      this.bodyHtml = ''
    }
  },
  beforeUnmount() {
    const editor = this.editor
    if (editor == null) return
    // 组件销毁时，及时销毁编辑器
    editor.destroy()
  }
}
</script>

<template>
  <div style="border: 1px solid #ccc">
    <Toolbar
      style="border-bottom: 1px solid #ccc"
      :editor="editor"
      :defaultConfig="toolbarConfig"
      :mode="mode"
    />
    <Editor
      style="height: 300px; overflow-y: hidden"
      v-model="bodyHtml"
      :defaultConfig="editorConfig"
      :mode="mode"
      @onCreated="onCreated"
    />
  </div>
</template>
