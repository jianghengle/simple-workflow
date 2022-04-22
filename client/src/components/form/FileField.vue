<template>
  <div class="mt-4">
    <div class="field">
      <label class="label">{{label}}</label>
      <file-display v-if="localValue" :fileValue="localValue" :readonly="readonly" @file-deleted="onFileDeleted" />
      <file-upload v-if="!readonly" @file-uploaded="onFileUploaded" />
    </div>
  </div>
</template>

<script>
import FileUpload from '@/components/form/FileUpload'
import FileDisplay from '@/components/form/FileDisplay'

export default {
  name: 'file-field',
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
      this.localValue = val
    },
    onFileDeleted () {
      this.localValue = null
    },
  },
  mounted () {
    this.setLocalValue()
  },
}
</script>
