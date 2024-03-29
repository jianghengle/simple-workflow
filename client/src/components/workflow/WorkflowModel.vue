<template>
  <div v-if="localModel" class="mb-6">
    <div v-for="(f, i) in fields" :key="'wfm-f-'+i">
      <string-field v-if="f.type == 'string'" :name="f.name" :label="f.label" :required="f.required" :value="localModel[f.name]" :readonly="f.readonly" @value-changed="onValueChanged" :options="f.optionValues" />
      <strings-field v-if="f.type == 'strings'" :name="f.name" :label="f.label" :required="f.required" :value="localModel[f.name]" :readonly="f.readonly" @value-changed="onValueChanged" :options="f.optionValues" />
      <textarea-field v-if="f.type == 'textarea'" :name="f.name" :label="f.label" :required="f.required" :value="localModel[f.name]" :readonly="f.readonly"  @value-changed="onValueChanged" />
      <number-field v-if="f.type == 'number'" v-show="!f.linkedFrom" :name="f.name" :required="f.required" :label="f.label" :value="localModel[f.name]" :readonly="f.readonly"  @value-changed="onValueChanged" />
      <checkbox-field v-if="f.type == 'checkbox'" :name="f.name" :label="f.label" :required="f.required" :value="localModel[f.name]" :readonly="f.readonly"  @value-changed="onValueChanged" />
      <file-field v-if="f.type == 'file'" :name="f.name" :label="f.label" :required="f.required" :value="localModel[f.name]" :readonly="f.readonly"  @value-changed="onValueChanged" />
      <files-field v-if="f.type == 'files'" :name="f.name" :label="f.label" :required="f.required" :value="localModel[f.name]" :readonly="f.readonly"  @value-changed="onValueChanged" />
      <sheet-field v-if="f.type == 'sheet'" :name="f.name" :label="f.label" :required="f.required" :value="localModel[f.name]" :readonly="f.readonly" :columns="f.columns"  @value-changed="onValueChanged" />
      <items-field v-if="f.type == 'items'" :name="f.name" :label="f.label" :required="f.required" :value="localModel[f.name]" :readonly="f.readonly" :fields="f.itemFields" :parentModel="localModel"  @value-changed="onValueChanged" />
    </div>

  </div>
</template>

<script>
import StringField from '@/components/form/StringField'
import StringsField from '@/components/form/StringsField'
import TextareaField from '@/components/form/TextareaField'
import NumberField from '@/components/form/NumberField'
import CheckboxField from '@/components/form/CheckboxField'
import FileField from '@/components/form/FileField'
import FilesField from '@/components/form/FilesField'
import SheetField from '@/components/form/SheetField'
import ItemsField from '@/components/form/ItemsField'

export default {
  name: 'WorkflowModel',
  components: {
    StringField,
    StringsField,
    TextareaField,
    NumberField,
    CheckboxField,
    FileField,
    FilesField,
    SheetField,
    ItemsField
  },
  props: ['model'],
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
    email () {
      return this.$store.state.user.email
    },
    orgUser () {
      if (!this.email || !this.orgUsers) {
        return null
      }
      var email = this.email
      return this.orgUsers.filter(function(u){
        return u.email == email
      })[0]
    },
    groups () {
      if (!this.orgUsers) {
        return {}
      }
      var groups = {'All': []}
      this.orgUsers.forEach(function(user) {
        groups['All'].push({value: user.email, label: user.username ? (user.username + ' <' + user.email + '>') : user.email})
        if (user.groups) {
          user.groups.forEach(function(g) {
            if (!groups[g]) {
              groups[g] = []
            }
            groups[g].push({value: user.email, label: user.username ? (user.username + ' <' + user.email + '>') : user.email})
          })
        }
      })
      return groups
    },
    configId () {
      return this.$route.params.configId
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
    statePermissions () {
      if (!this.orgWorkflowConfig || !this.model) {
        return null
      }
      var state = this.model.state
      var stateConfig = null
      for (const sc of this.orgWorkflowConfig.states) {
        if (sc.name == state) {
          stateConfig = sc
        }
      }
      if (stateConfig) {
        return stateConfig.permissions
      }
      return null
    },
    fields () {
      if (!this.orgWorkflowConfig || !this.statePermissions) {
        return []    
      }
      var fields = []
      for (const f of this.orgWorkflowConfig.fields) {
        var field = JSON.parse(JSON.stringify(f))
        if (field.options) {
          if (Array.isArray(field.options)) {
            field.optionValues = field.options
          } else if (typeof(field.options) == 'string') {
            field.optionValues = this.groups[field.options]
          } else {
            var v = this.localModel[field.options.from]
            var mappings = {}
            mappings[v] = []
            for (const m of field.options.mappings) {
              mappings[m.from] = m.deprivedOptions
            }
            field.optionValues = mappings[v]
          }
        }
        if (this.isFieldViewable(f)) {
          if (this.isFieldEditable(f)) {
            field.readonly = false
          } else {
            field.readonly = true
          }
          fields.push(field)
        }
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
      var changedField = null
      for (const f of this.fields) {
        if (f.name == name) {
          changedField = f
        }
      }
      if (!changedField) {
        return
      }
      for (const f of this.fields) {
        if (changedField.type == 'items') {
          if (f.type == 'number' && f.linkedFrom.startsWith(name + '.') && this.isFieldEditable(f)) {
            var firstDot = f.linkedFrom.indexOf('.')
            var lastDot = f.linkedFrom.lastIndexOf('.')
            var itemFieldName = f.linkedFrom.substring(firstDot + 1, lastDot)
            var sum = 0
            for (const item of value) {
              sum += Number(item[itemFieldName])
            }
            this.localModel[f.name] = sum
          }
        } else {
          if (f.type == 'string' && f.linkedFrom == name && this.isFieldEditable(f)) {
            for (const v of f.linkedValues) {
              if (value == v['From']) {
                this.localModel[f.name] = v['To']
              }
            }
          }
          if (f.type == 'number' && f.linkedFrom == name && this.isFieldEditable(f)) {
            this.localModel[f.name] = value
          }
        }
      }
    },
    isFieldViewable (f) {
      for (const permission of this.statePermissions) {
        if (permission.action != 'View') {
          continue
        }
        if (this.userIsActor(permission)) {
          if (permission.actionFields.includes(f.name) || permission.actionFields.includes('All')) {
            return true
          }
        }
      }
      return false
    },
    isFieldEditable (f) {
      for (const permission of this.statePermissions) {
        if (permission.action != 'Edit') {
          continue
        }
        if (this.userIsActor(permission)) {
          if (permission.actionFields.includes(f.name) || permission.actionFields.includes('All')) {
            return true
          }
        }
      }
      return false
    },
    userIsActor (permission) {
      var allowedGroups = permission.groups
      for (const g of allowedGroups) {
        if (this.orgUser.groups.includes(g)) {
          return true
        }
      }
      var others = permission.others
      for (const o of others) {
        if (o == 'Workflow Creator') {
          if (this.localModel.createdBy == this.email) {
            return true
          }
        } else {
          var field = null
          for (const f of this.orgWorkflowConfig.fields) {
            if (f.name == o) {
              field = f
            }
          }
          if (field) {
            if (field.type == 'string') {
              if (this.email == this.localModel[field.name]) {
                return true
              }
            }
            if (field.type == 'strings') {
              if (this.localModel[field.name].includes(this.email)) {
                return true
              }
            }
          }
        }
      }
      return false
    },
  },
  mounted () {
    this.setLocalModel()
  },
}
</script>

<style scoped lang="scss">

</style>
