<template>
  <div class="mt-4">
    <div class="field">
      <label class="label">{{label}}</label>
      <div class="field">
        <div class="control" v-if="!options">
          <input class="input" type="number" :placeholder="placeholder" v-model.number="localValue" :readonly="readonly" :disabled="readonly">
        </div>
        <div class="control" v-if="options">
          <div class="select">
            <select v-model="localValue" :disabled="readonly">
              <option  v-for="(opt, i) in selectOptions" :key="'string-field-option-' + i" :value="opt.value">
                {{opt.label}}
              </option>
            </select>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'number-field',
  props: ['name', 'label', 'value', 'placeholder', 'readonly', 'options'],
  data () {
    return {
      localValue: null,
    }
  },
  computed: {
    selectOptions () {
      if (!this.options || !this.options.length) {
        return []
      }
      var first = this.options[0]
      if (typeof first === 'object') {
        return this.options
      }
      return this.options.map(opt => ({value: opt, label: opt}))
    },
  },
  watch: {
    value: function (val) {
      this.setLocalValue()
    },
    localValue: function (val) {
      if (!this.readonly) {
        var value = this.localValue
        this.$emit('value-changed', [this.name, value])
      }
    },
  },
  methods: {
    setLocalValue () {
      if (this.localValue != this.value) {
        this.localValue = Number(this.value)
      }
    },
    
  },
  mounted () {
    this.setLocalValue()
  },
}
</script>
