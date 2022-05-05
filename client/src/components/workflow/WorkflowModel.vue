<template>
  <div v-if="localModel" class="mb-6">
    <div v-for="(f, i) in fields" :key="'wfm-f-'+i">
      <string-field v-if="f.type == 'string'" :name="f.name" :label="f.label" :value="localModel[f.name]" :readonly="readonly" @value-changed="onValueChanged" :options="f.optionValues" />
      <textarea-field v-if="f.type == 'textarea'" :name="f.name" :label="f.label" :value="localModel[f.name]" :readonly="readonly"  @value-changed="onValueChanged" />
      <number-field v-if="f.type == 'number'" :name="f.name" :label="f.label" :value="localModel[f.name]" :readonly="readonly"  @value-changed="onValueChanged" :options="f.optionValues" />
      <checkbox-field v-if="f.type == 'checkbox'" :name="f.name" :label="f.label" :value="localModel[f.name]" :readonly="readonly"  @value-changed="onValueChanged" />
      <file-field v-if="f.type == 'file'" :name="f.name" :label="f.label" :value="localModel[f.name]" :readonly="readonly"  @value-changed="onValueChanged" />
      <files-field v-if="f.type == 'files'" :name="f.name" :label="f.label" :value="localModel[f.name]" :readonly="readonly"  @value-changed="onValueChanged" />
      <sheet-field v-if="f.type == 'sheet'" :name="f.name" :label="f.label" :value="localModel[f.name]" :readonly="readonly" :columns="f.columns"  @value-changed="onValueChanged" />
    </div>

  </div>
</template>

<script>
import StringField from '@/components/form/StringField'
import TextareaField from '@/components/form/TextareaField'
import NumberField from '@/components/form/NumberField'
import CheckboxField from '@/components/form/CheckboxField'
import FileField from '@/components/form/FileField'
import FilesField from '@/components/form/FilesField'
import SheetField from '@/components/form/SheetField'

export default {
  name: 'WorkflowModel',
  components: {
    StringField,
    TextareaField,
    NumberField,
    CheckboxField,
    FileField,
    FilesField,
    SheetField
  },
  props: ['model', 'readonly'],
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
    groups () {
      if (!this.orgUsers) {
        return {}
      }
      var groups = {'All': []}
      this.orgUsers.forEach(function(user) {
        groups['All'].push(user.email)
        if (user.groups) {
          user.groups.forEach(function(g) {
            if (!groups[g]) {
              groups[g] = []
            }
            groups[g].push(user.email)
          })
        }
      })
      return groups
    },
    configId () {
      return this.$route.params.configId
    },
    folderId () {
      return this.$route.params.folderId
    },
    orgWorkflowConfigs () {
      return this.$store.state.org.orgWorkflowConfigs
    },
    orgWorkflowConfig () {
      if (!this.orgWorkflowConfigs) {
        return null
      }
      for(const workflowConfig of this.orgWorkflowConfigs) {
        if (workflowConfig.id == this.configId) {
          return workflowConfig
        }
      }
      return null
    },
    fields () {
      if (!this.orgWorkflowConfig) {
        return []    
      }
      var fields = []
      for (const f of this.orgWorkflowConfig.fields) {
        var field = JSON.parse(JSON.stringify(f))
        if (field.options) {
          if (Array.isArray(field.options)) {
            field.optionValues = field.options
          } else {
            field.optionValues = this.groups[field.options]
          }
        }
        fields.push(field)
      }
      return fields
    },
  },
  watch: {
    model: function (val) {
      this.setLocalModel()
    },
    localModel: function (val) {
      this.$emit('model-updated', this.localModel)
    },
  },
  methods: {
    setLocalModel () {
      this.localModel = JSON.parse(JSON.stringify(this.model))
    },
    onValueChanged (val) {
      var name = val[0]
      var value = JSON.parse(JSON.stringify(val[1]))
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
