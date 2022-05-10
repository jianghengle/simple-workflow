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
          <input class="input" :class="{'is-danger': brokenConstraint}" type="text" :placeholder="placeholder" v-model="localValue" :readonly="readonly" :disabled="readonly">
        </div>
        <p class="help is-danger" v-if="brokenConstraint">{{brokenConstraint.info}}</p>
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
  props: ['name', 'label', 'value', 'placeholder', 'prefix', 'readonly', 'options', 'constraints'],
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
    brokenConstraint () {
      if (this.localValue == null) {
        return null
      }
      if (!this.constraints) {
        return null
      }
      for(const c of this.constraints) {
        if (c.match && !c.match.test(this.localValue)) {
          return c
        }
        if (c.notMatch && c.notMatch.test(this.localValue)) {
          return c
        }
      }
      return null
    },
  },
  watch: {
    value: function (val) {
      this.setLocalValue()
    },
    localValue: function (val) {
      this.$nextTick(function () {
        if (!this.readonly && !this.brokenConstraint) {
          var value = this.prefix ? (this.prefix + this.localValue) : this.localValue
          this.$emit('value-changed', [this.name, value])
        }
      })
    },
  },
  methods: {
    setLocalValue () {
      var localValue = null
      var value = ''
      if (this.value) {
        value = String(this.value)
      }
      if (this.prefix) {
        if (value && value.startsWith(this.prefix)) {
          localValue = value.slice(this.prefix.length)
        } else {
          localValue = value
        }
      } else {
        localValue = value
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
