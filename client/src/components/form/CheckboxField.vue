<template>
  <div class="mt-4">
    <div class="field">
      <label class="label">{{label}}</label>
      <div class="control">
        <label class="checkbox" :disabled="readonly">
          <input type="checkbox" v-model="localValue" :disabled="readonly">
          {{inlineLabel}}
        </label>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'checkbox-field',
  props: ['name', 'label', 'value', 'inlineLabel', 'readonly'],
  data () {
    return {
      localValue: false,
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
      var localValue = this.value   
      if (localValue != this.localValue) {
        this.localValue = localValue
      }
    },
    
  },
  mounted () {
    this.setLocalValue()
  },
}
</script>
