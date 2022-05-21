<template>
  <div class="modal"
      :class="{'is-active': opened}">
    <div class="modal-background"></div>
    <div class="modal-card">
      <header class="modal-card-head">
        <p class="modal-card-title">Item Field</p>
        <button class="delete" @click="close"></button>
      </header>
      <section class="modal-card-body">

        <string-field :name="'name'" :label="'Name'" :value="model.name" @value-changed="onValueChanged" />
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
              <input type="radio" name="optionsMode" value="Deprived" v-model="optionsMode">
              Deprived
            </label>
          </div>
          <div class="my-options" v-if="optionsMode == 'Deprived'">
            <string-field :name="'from'" :value="optionsDeprived.from" :options="linkedFromOptions" @value-changed="onOptionsDeprivedChanged" />
            <items-field v-if="optionsDeprived.from" :name="'mappings'" :value="optionsDeprived.mappings" :fields="optionsDeprivedMappingFields" @value-changed="onOptionsDeprivedChanged" />
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

        <checkbox-field v-if="model.type == 'number'"  :name="'showSum'" :label="'Sum'" :inlineLabel="'Show'" :value="model.showSum" @value-changed="onValueChanged" />

        <checkbox-field v-if="model.type == 'number'"  :name="'twoDigits'" :label="'Number in table'" :inlineLabel="'Show two digits'" :value="model.twoDigits" @value-changed="onValueChanged" />

      </section>
      <footer class="modal-card-foot">
        <a class="button is-link"  :disabled="!canSave" @click="save">Save</a>
        <a class="button is-danger" v-if="index != null" @click="deleteField">Delete</a>
        <a class="button" @click="close">Cancel</a>
      </footer>
    </div>
  </div>
</template>

<script>
import StringField from '@/components/form/StringField'
import StringsField from '@/components/form/StringsField'
import CheckboxField from '@/components/form/CheckboxField'
import ItemsField from '@/components/form/ItemsField'

export default {
  name: 'custom-field-modal',
  components: {
    StringField,
    StringsField,
    CheckboxField,
    ItemsField,
  },
  props: ['opened', 'field', 'index', 'linkedFromOptions'],
  data () {
    return {
      model: {
        name: '',
        label: '',
        type: 'string',
        options: null,
        showSum: false,
        twoDigits: true,
      },
      typeOptions: ['string', 'number'],
      optionsMode: 'NoOptions',
      fixedOptions: [],
      orgUsersOptions: 'All',
      optionsDeprived: {
        from: '',
        mappings: [],
      },
      optionsDeprivedMappingFields: [
        {name: 'from', type: 'string', label: 'Deprived From'},
        {name: 'deprivedOptions', type: 'strings', label: 'Deprived Options'},
      ],
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
          } else if (typeof(this.field.options) == 'string') {
            this.optionsMode = 'OrgUsers'
            this.fixedOptions = []
            this.orgUsersOptions = this.field.options
          } else {
            this.optionsMode = 'Deprived'
            this.optionsDeprived = JSON.parse(JSON.stringify(this.field.options))
          }
        } else {
          this.optionsMode = 'NoOptions'
          this.fixedOptions = []
          this.orgUsersOptions ='All'
        }
        this.model.showSum = this.field.showSum
        this.model.twoDigits = this.field.twoDigits
      }
    },
  },
  methods: {
    close () {
      this.$emit('item-field-modal-closed')
    },
    save () {
      if (!this.canSave) {
        return
      }
      this.model.name = this.model.name.trim()
      this.model.label = this.model.label.trim()
      if (this.model.type != 'string') {
        this.model.options = null
      } else {
        if (this.optionsMode == 'NoOptions') {
          this.model.options = null
        } else if (this.optionsMode == 'Fixed') {
          this.model.options = this.fixedOptions
        } else if (this.optionsMode == 'OrgUsers') {
          this.model.options = this.orgUsersOptions
        } else {
          if (this.optionsDeprived.from && this.optionsDeprived.mappings.length) {
            this.model.options = JSON.parse(JSON.stringify(this.optionsDeprived))
          } else {
            this.model.options = null
          }
        }
      }
      if (this.model.type != 'number') {
        this.model.showSum = false
      }
      this.$emit('item-field-modal-saved', this.model)
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
      this.$emit('item-field-modal-deleted')
    },
    onOptionsDeprivedChanged (val) {
      this.optionsDeprived[val[0]] = JSON.parse(JSON.stringify(val[1]))
    }
  },
}
</script>

<style scoped>
.my-options {
  margin-left: 15px;
  margin-top: -15px;
}
</style>
