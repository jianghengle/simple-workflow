<template>
  <div class="modal"
      :class="{'is-active': opened}">
    <div class="modal-background"></div>
    <div class="modal-card">
      <header class="modal-card-head">
        <p class="modal-card-title">Permission</p>
        <button class="delete" @click="close"></button>
      </header>
      <section class="modal-card-body" v-if="localModel">

        <string-field :name="'action'" :label="'Action'" :value="localModel.action" @value-changed="onValueChanged" :options="actions" :readonly="index != null" />
        <strings-field v-if="localModel.action != 'Delete'" :name="'actionFields'" :label="'Action Fields'" :value="localModel.actionFields" @value-changed="onValueChanged" :options="fieldOptions"
         :helpInfo="'The affected fields of this permission action.'" />
        <strings-field :name="'groups'" :label="'Actor Groups'" :value="localModel.groups" @value-changed="onValueChanged" :options="groupOptions" />
        <strings-field :name="'others'" :label="'Actor Others'" :value="localModel.others" @value-changed="onValueChanged" :options="otherOptions" />

      </section>
      <footer class="modal-card-foot">
        <a class="button is-link" @click="save">Save</a>
        <a class="button is-danger" @click="remove">Delete</a>
        <a class="button" @click="close">Cancel</a>
      </footer>
    </div>
  </div>
</template>

<script>
import StringField from '@/components/form/StringField'
import StringsField from '@/components/form/StringsField'

export default {
  name: 'permission-modal',
  components: {
    StringsField,
    StringField
  },
  props: ['opened', 'model', 'fields', 'index'],
  data () {
    return {
      localModel: null,
      actions: ['View', 'Edit', 'Delete']
    }
  },
  computed: {
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
      var fieldNames = this.fields.map((f)=> f.name)
      fieldNames.push('Workflow Creator')
      return fieldNames
    },
    fieldOptions () {
      var fieldOptions = this.fields.map((f)=> f.name)
      fieldOptions.unshift('All')
      return fieldOptions
    },
  },
  watch: {
    opened: function (val) {
      if (val) {
        this.localModel = JSON.parse(JSON.stringify(this.model))
      }
    },
  },
  methods: {
    close () {
      this.$emit('permission-modal-closed')
    },
    save () {
      if (this.localModel.action == 'Delete') {
        this.localModel.actionFields = ['All']
      }
      this.$emit('permission-modal-saved', this.localModel)
    },
    remove () {
      this.$emit('permission-modal-deleted')
    },
    onValueChanged (val) {
      var name = val[0]
      var value = val[1]
      if (this.model[name] != value) {
        this.localModel[name] = value
      }
    },
  },
}
</script>

<style scoped>

</style>
