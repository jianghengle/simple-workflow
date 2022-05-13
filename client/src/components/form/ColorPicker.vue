<template>
  <div class="mt-4">
    <div class="field">
      <label class="label">{{label}}</label>
      <div class="control my-color-picker">

        <swatches-picker v-model="localValue" />

      </div>
    </div>
  </div>
</template>

<script>
import Swatches from 'vue-color/src/components/Swatches'

export default {
  name: 'color-picker',
  components: {
    'swatches-picker': Swatches,
  },
  props: ['name', 'label', 'value'],
  data () {
    return {
      localValue: '',
    }
  },
  watch: {
    value: function (val) {
      this.setLocalValue()
    },
    localValue: function (val) {
      var newColor = typeof(this.localValue) == 'string' ? this.localValue : String(this.localValue.hex)
      this.$emit('value-changed', [this.name, newColor])
    },
  },
  methods: {
    setLocalValue () {
      var color = typeof(this.localValue) == 'string' ? this.localValue : String(this.localValue.hex)
      if (this.value != color) {
        if (this.value) {
          this.localValue = this.value
        } else {
          this.localValue = '#3F51B5'
        }
      }
    },
  },
  mounted () {
    this.setLocalValue()
  },
}
</script>

<style scoped lang="scss">
.my-color-picker {
  div {
    height: 150px;
    width: 290px;
  }
}
</style>
