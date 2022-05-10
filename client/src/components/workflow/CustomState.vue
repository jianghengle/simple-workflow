<template>
  <div v-if="localModel" class="pl-4 pr-4">
    <string-field :name="'name'" :label="'Name'" :value="localModel.name" :placeholder="'State name'" @value-changed="onValueChanged" />
    <color-picker :name="'color'" :label="'Color'" :value="localModel.color" @value-changed="onValueChanged" />
    <state-permissions :model="localModel.permissions" @model-changed="onValueChanged" :fields="fields" :stateName="localModel.name" />
    <state-transitions :model="localModel.transitions" @model-changed="onValueChanged" :fields="fields" :stateName="localModel.name" :stateNames="stateNames" />
  </div>
</template>

<script>
import StringField from '@/components/form/StringField'
import ColorPicker from '@/components/form/ColorPicker'
import StatePermissions from '@/components/workflow/StatePermissions'
import StateTransitions from '@/components/workflow/StateTransitions'

export default {
  name: 'CustomState',
  components: {
    StringField,
    StatePermissions,
    StateTransitions,
    ColorPicker
  },
  props: ['model', 'index', 'fields', 'stateNames'],
  data () {
    return {
      localModel: null,
    }
  },
  watch: {
    model: function (val) {
      if (val) {
        this.setLocalModel()
      }
    },
    localModel: {
      handler (val) {
        this.$emit('model-changed', [this.index, this.localModel])
      },
      deep: true,
    },
  },
  methods: {
    setLocalModel () {
      if (this.model) {
        var modelJson = JSON.stringify(this.model)
        if (JSON.stringify(this.localModel) != modelJson) {
          this.localModel = JSON.parse(modelJson)
        }
      }
    },
    onValueChanged (val) {
      var name = val[0]
      var value = val[1]
      var valueJson = JSON.stringify(value)
      if (JSON.stringify(this.localModel[name]) != valueJson) {
        this.localModel[name] = JSON.parse(valueJson)
      }
    },
  },
  mounted () {
    this.setLocalModel()
  },
}
</script>

<style scoped lang="scss">

</style>
