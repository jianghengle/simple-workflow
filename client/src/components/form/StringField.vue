<template>
  <div class="mt-4">
    <div class="field">
      <label class="label">{{label}}</label>
      <div class="field" :class="{'has-addons': prefix}">
        <p class="control" v-if="prefix">
          <a class="button is-static">
              {{prefix}}
          </a>
        </p>
        <div class="control" v-if="!options" :class="{'is-expanded': prefix}">
          <input class="input" type="text" :placeholder="placeholder" v-model="localValue" :readonly="readonly" :disabled="readonly">
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
  name: 'string-field',
  props: ['name', 'label', 'value', 'placeholder', 'prefix', 'readonly', 'options'],
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
        var value = this.prefix ? (this.prefix + this.localValue) : this.localValue
        this.$emit('value-changed', [this.name, value])
      }
    },
  },
  methods: {
    setLocalValue () {
      var localValue = null
      if (this.prefix) {
        if (this.value && this.value.startsWith(this.prefix)) {
          localValue = this.value.slice(this.prefix.length)
        } else {
          localValue = this.value
        }
      } else {
        localValue = this.value
      }
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
