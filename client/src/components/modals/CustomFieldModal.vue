<template>
  <div class="modal"
      :class="{'is-active': opened}">
    <div class="modal-background"></div>
    <div class="modal-card">
      <header class="modal-card-head">
        <p class="modal-card-title">New Field</p>
        <button class="delete" @click="close"></button>
      </header>
      <section class="modal-card-body">

        <string-field :name="'name'" :label="'Name'" :value="model.name" @value-changed="onValueChanged" :constraints="nameConstraints" />
        <string-field :name="'label'" :label="'Label'" :value="model.label" @value-changed="onValueChanged" />
        <string-field :name="'type'" :label="'Type'" :value="model.type" :options="typeOptions" @value-changed="onValueChanged" />

        <div class="field mt-4" v-if="model.type == 'string' || model.type == 'strings'">
          <label class="label">Options</label>
          <div class="control">
            <label class="radio">
              <input type="radio" name="optionsMode" value="NoOptions" v-model="optionsMode">
              No Options
            </label>
          </div>
          <div class="control">
            <label class="radio">
              <input type="radio" name="optionsMode" value="Fixed" v-model="optionsMode">
              Fixed
            </label>
          </div>
          <div class="my-options" v-if="optionsMode == 'Fixed'">
            <strings-field :value="fixedOptions" @value-changed="onFixedOptionsValueChanged" />
          </div>
          <div class="control">
            <label class="radio">
              <input type="radio" name="optionsMode" value="OrgUsers" v-model="optionsMode">
              Org Users
            </label>
          </div>
          <div class="my-options" v-if="optionsMode == 'OrgUsers'">
            <string-field :value="orgUsersOptions" :options="groupOptions" @value-changed="onOrgUsersValueChanged" />
          </div>
        </div>

        <checkbox-field :name="'dashboard'" :label="'Dashboard'" :inlineLabel="'Show'" :value="model.dashboard" @value-changed="onValueChanged" />

      </section>
      <footer class="modal-card-foot">
        <a class="button is-link"  :disabled="!canSave" @click="save">Save</a>
        <a class="button is-danger" @click="deleteField">Delete</a>
        <a class="button" @click="close">Cancel</a>
      </footer>
    </div>
  </div>
</template>

<script>
import StringField from '@/components/form/StringField'
import StringsField from '@/components/form/StringsField'
import CheckboxField from '@/components/form/CheckboxField'

export default {
  name: 'custom-field-modal',
  components: {
    StringField,
    StringsField,
    CheckboxField
  },
  props: ['opened', 'field', 'index'],
  data () {
    return {
      model: {
        name: '',
        label: '',
        type: 'string',
        options: null,
        dashboard: true,
      },
      typeOptions: ['string', 'strings', 'textarea', 'number', 'checkbox', 'file', 'files'],
      optionsMode: 'NoOptions',
      fixedOptions: [],
      orgUsersOptions: 'All',
      nameConstraints: [
        {match: /^([a-zA-Z][a-zA-Z\d]*)$/, info: 'Name must only contain alphabet and digital charactors.'},
        {notMatch: /(^id$|^folderId$|^state$|^stateEvents$|^createdBy$)/, info: 'Name must not be reserved names.'}
      ]
    }
  },
  computed: {
    canSave () {
      return this.model.name.trim() && this.model.label.trim()
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
  },
  watch: {
    opened: function (val) {
      if (val) {
        this.model.name = this.field.name
        this.model.label = this.field.label
        this.model.type = this.field.type
        if (this.field.options) {
          if (Array.isArray(this.field.options)) {
            this.optionsMode = 'Fixed'
            this.fixedOptions = this.field.options
            this.orgUsersOptions ='All'
          } else {
            this.optionsMode = 'OrgUsers'
            this.fixedOptions = []
            this.orgUsersOptions = this.field.options
          }
        } else {
          this.optionsMode = 'NoOptions'
          this.fixedOptions = []
          this.orgUsersOptions ='All'
        }
        this.model.dashboard = this.field.dashboard
      }
    },
  },
  methods: {
    close () {
      this.$emit('custom-field-modal-closed')
    },
    save () {
      if (!this.canSave) {
        return
      }
      this.model.name = this.model.name.trim()
      this.model.label = this.model.label.trim()
      if (this.model.type != 'string' && this.model.type != 'strings') {
        this.model.options = null
      } else {
        if (this.optionsMode == 'NoOptions') {
          this.model.options = null
        } else if (this.optionsMode == 'Fixed') {
          this.model.options = this.fixedOptions
        } else {
          this.model.options = this.orgUsersOptions
        }
      }
      this.$emit('custom-field-modal-saved', [this.index, this.model])
    },
    onValueChanged (val) {
      var name = val[0]
      var value = val[1]
      if (this.model[name] != value) {
        this.model[name] = value
      }
    },
    onFixedOptionsValueChanged (val) {
      this.fixedOptions = val[1]
    },
    onOrgUsersValueChanged (val) {
      this.orgUsersOptions = val[1]
    },
    deleteField () {
      var confirm = {
        title: 'Delete Field',
        message: 'Are you sure to delete this field?',
        button: 'Yes, I am sure.',
        callback: {
          context: this,
          method: this.deleteFieldConfirmed,
          args: []
        }
      }
      this.$store.commit('modals/openConfirmModal', confirm)
    },
    deleteFieldConfirmed () {
      this.$emit('custom-field-modal-deleted', this.index)
    },
  },
}
</script>

<style scoped>
.my-options {
  margin-left: 15px;
  margin-top: -15px;
}
</style>
