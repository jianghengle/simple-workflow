<template>
  <div class="mt-4">
    <div class="field">
      <label class="label">{{label}}</label>
      <div v-if="localValue">
        <file-display v-for="(f, i) in localValue" :key="'fd-' + i" :fileValue="f" :fileIndex="i" :readonly="readonly" @file-deleted="onFileDeleted" />
      </div>
      <file-upload v-if="!readonly" @file-uploaded="onFileUploaded" />
    </div>
  </div>
</template>

<script>
import FileUpload from '@/components/form/FileUpload'
import FileDisplay from '@/components/form/FileDisplay'

export default {
  name: 'files-field',
  components: {
    FileUpload,
    FileDisplay
  },
  props: ['name', 'label', 'value', 'readonly'],
  data () {
    return {
      localValue: null,
    }
  },
  watch: {
    value: function (val) {
      this.setLocalValue()
    },
    localValue: function (val) {
      if (!this.readonly) {
        this.$emit('value-changed', [this.name, this.localValue])
      }
    },
  },
  methods: {
    setLocalValue () {
      var localValueJson = JSON.stringify(this.value)
      if (localValueJson != JSON.stringify(this.localValue)) {
        this.localValue = JSON.parse(localValueJson)
      }
    },
    onFileUploaded (val) {
      if (!this.localValue) {
        this.localValue = []
      }
      this.localValue.push(val)
    },
    onFileDeleted (fileIndex) {
      if (!this.readonly) {
        this.localValue.splice(fileIndex, 1)
      }
    },
  },
  mounted () {
    this.setLocalValue()
  },
}
</script>
