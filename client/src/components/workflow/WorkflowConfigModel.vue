<template>
  <div v-if="localModel" class="mb-6">

    <div v-if="isNew">
      <string-field :name="'tableName'" :label="'Table Name'" :value="localModel.tableName" :placeholder="'Database table name for this kind of workflows'" @value-changed="onValueChanged" :prefix="org.id + '-'"
        :helpInfo="'The database table will be created to contain these workflow instances. The table name cannot be changed afterwards.'" />
    </div>
    <div v-else>
      <string-field :name="'tableName'" :label="'Workflow Table Name'" :value="model.tableName" :readonly="true" />
    </div>

    <string-field :name="'name'" :label="'Name'" :value="localModel.name" :placeholder="'Workflow name'" @value-changed="onValueChanged" />

    <!--<textarea-field :name="'description'" :label="'Description'" :value="localModel.description" :placeholder="'Workflow description'" @value-changed="onValueChanged" />-->

    <string-field :name="'userGroup'" :label="'User Group'" :value="localModel.userGroup" @value-changed="onValueChanged" :options="groupOptions" :helpInfo="'The user group can see and create workflows.'" />

    <custom-fields :model="localModel.fields" @model-changed="onValueChanged" />

    <strings-field :name="'creationNotifyingGroups'" :label="'Creation Notifying Groups'" :value="localModel.creationNotifyingGroups" @value-changed="onValueChanged" :options="groupOptions" />
    <strings-field :name="'creationNotifyingOthers'" :label="'Creation Notifying Others'" :value="localModel.creationNotifyingOthers" @value-changed="onValueChanged" :options="otherOptions" />

    <custom-states :model="localModel.states" @model-changed="onValueChanged" :fields="localModel.fields" />

  </div>
</template>

<script>
import StringField from '@/components/form/StringField'
import StringsField from '@/components/form/StringsField'
import TextareaField from '@/components/form/TextareaField'
import CustomFields from '@/components/workflow/CustomFields'
import CustomStates from '@/components/workflow/CustomStates'
import CheckboxField from '@/components/form/CheckboxField'

export default {
  name: 'workflow-config-model',
  components: {
    StringField,
    StringsField,
    TextareaField,
    CustomFields,
    CustomStates,
    CheckboxField
  },
  props: ['model', 'isNew'],
  data () {
    return {
      localModel: null,
    }
  },
  computed: {
    org () {
      return this.$store.state.org.org
    },
    orgUsers () {
      return this.$store.state.org.orgUsers
    },
    groupOptions () {
      if (!this.orgUsers) {
        return ['All']
      }
      var groups = new Set()
      this.orgUsers.forEach(function(user) {
        if (user.groups) {
          user.groups.forEach(function(g) {
            groups.add(g)
          })
        }
      })
      var arr = Array.from(groups)
      arr.unshift('All')
      return arr
    },
    otherOptions () {
      var fieldNames = this.localModel.fields.map((f)=> f.name)
      fieldNames.push('Workflow Creator')
      return fieldNames
    },
  },
  watch: {
    model: function (val) {
      this.setLocalModel()
    },
    localModel: {
      handler (newValue, oldValue) {
        this.$emit('model-updated', this.localModel)
      },
      deep: true,
    },
  },
  methods: {
    setLocalModel () {
      var model = JSON.parse(JSON.stringify(this.model))
      var localModel = {}
      var attrs = ['tableName', 'name', 'description', 'userGroup', 'fields', 'states', 'creationNotifyingGroups', 'creationNotifyingOthers']
      for(const attr of attrs) {
        localModel[attr] = model[attr]
      }
      this.localModel = localModel
    },
    onValueChanged (val) {
      var name = val[0]
      var value = val[1]
      this.localModel[name] = value
    },
  },
  mounted () {
    this.setLocalModel()
  },
}
</script>

<style scoped lang="scss">

</style>
