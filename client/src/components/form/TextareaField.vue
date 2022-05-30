<template>
  <div class="mt-4">
    <div class="field">
      <label class="label">{{label}}</label>
      <div class="control">
        <textarea class="textarea" :class="{'my-disbaled-field': readonly}" :placeholder="placeholder" v-model="localValue" :readonly="readonly" :disabled="readonly"></textarea>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'textarea-field',
  props: ['name', 'label', 'value', 'placeholder', 'readonly'],
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
      if (this.localValue != this.value) {
        this.localValue = String(this.value)
      }
    },
  },
  mounted () {
    this.setLocalValue()
  },
}
</script>

<style scoped>

</style>>
