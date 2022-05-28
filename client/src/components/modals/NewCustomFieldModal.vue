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

        <string-field v-if="insertOptions.length" :label="'Insert'" :value="insertAfter" :options="insertOptions" @value-changed="onInsertAfterChanged" />

        <string-field :name="'name'" :label="'Name'" :value="model.name" @value-changed="onValueChanged" :constraints="nameConstraints" />
        <string-field :name="'label'" :label="'Label'" :value="model.label" @value-changed="onValueChanged" />
        <string-field :name="'type'" :label="'Type'" :value="model.type" :options="typeOptions" @value-changed="onValueChanged" />

        <string-field v-if="model.type == 'string'" :name="'defaultValue'" :label="'Default Value'" :value="model.defaultValue" @value-changed="onValueChanged" />
        <number-field v-if="model.type == 'number'" :name="'defaultValue'" :label="'Default Value'" :value="model.defaultValue" @value-changed="onValueChanged" />

        <div class="field mt-4" v-if="model.type == 'string' || model.type == 'strings'">
          <label class="label">Options</label>
          <div class="control">
            <label class="radio">
              <input type="radio" value="NoOptions" v-model="optionsMode">
              No Options
            </label>
          </div>
          <div class="control">
            <label class="radio">
              <input type="radio" value="Fixed" v-model="optionsMode">
              Static
            </label>
          </div>
          <div class="my-options" v-if="optionsMode == 'Fixed'">
            <strings-field :value="fixedOptions" @value-changed="onFixedOptionsValueChanged" />
          </div>
          <div class="control">
            <label class="radio">
              <input type="radio" value="Deprived" v-model="optionsMode">
              Derived
            </label>
          </div>
          <div class="my-options" v-if="optionsMode == 'Deprived'">
            <string-field :name="'from'" :value="optionsDeprived.from" :options="linkedFromOptions" @value-changed="onOptionsDeprivedChanged" />
            <items-field v-if="optionsDeprived.from" :name="'mappings'" :value="optionsDeprived.mappings" :fields="optionsDeprivedMappingFields" @value-changed="onOptionsDeprivedChanged" />
          </div>
          <div class="control">
            <label class="radio">
              <input type="radio" value="OrgUsers" v-model="optionsMode">
              Org Users
            </label>
          </div>
          <div class="my-options" v-if="optionsMode == 'OrgUsers'">
            <string-field :value="orgUsersOptions" :options="groupOptions" @value-changed="onOrgUsersValueChanged" />
          </div>
        </div>

        <div class="field mt-4" v-if="model.type == 'sheet'">
          <label class="label">Columns</label>
          <div class="my-columns">
            <strings-field :value="model.columns" @value-changed="onColumnsValueChanged" />
          </div>
        </div>

        <div class="field mt-4" v-if="model.type == 'items'">
          <custom-item-fields :model="model.itemFields" :linkedFromOptions="linkedFromOptions" @model-changed="onValueChanged" />
        </div>

        <string-field v-if="model.type == 'string' && linkedFromOptions && linkedFromOptions.length > 1"
          :name="'linkedFrom'" :label="'Auto Fill With'" :value="model.linkedFrom" :options="linkedFromOptions" @value-changed="onValueChanged" />

        <sheet-field v-if="model.type == 'string' && linkedFromOptions && linkedFromOptions.length > 1 && model.linkedFrom" :name="'linkedValues'" :label="'Auto Fill Values'" :columns="['From', 'To']" :value="model.linkedValues"  @value-changed="onValueChanged" />

        <string-field v-if="model.type == 'number' && numberLinkedFromOptions && numberLinkedFromOptions.length > 1"
          :name="'linkedFrom'" :label="'Auto Fill With'" :value="model.linkedFrom" :options="numberLinkedFromOptions" @value-changed="onValueChanged" />

        <number-field v-if="(model.type == 'string' || model.type == 'number')" :name="'dashboard'" :label="'Dashboard Index (0 means Not-Show)'" :value="model.dashboard" @value-changed="onValueChanged" />

        <checkbox-field v-if="(model.dashboard > 0 && model.type == 'number')"  :name="'twoDigits'" :label="'Number in Dashboard'" :inlineLabel="'Show two digits'" :value="model.twoDigits" @value-changed="onValueChanged" />

      </section>
      <footer class="modal-card-foot">
        <a class="button is-link"  :disabled="!canSave" @click="save">Save</a>
        <a class="button" @click="close">Cancel</a>
      </footer>
    </div>
  </div>
</template>

<script>
import StringField from '@/components/form/StringField'
import StringsField from '@/components/form/StringsField'
import CheckboxField from '@/components/form/CheckboxField'
import SheetField from '@/components/form/SheetField'
import ItemsField from '@/components/form/ItemsField'
import CustomItemFields from '@/components/workflow/CustomItemFields'
import NumberField from '@/components/form/NumberField'

export default {
  name: 'new-custom-field-modal',
  components: {
    StringField,
    StringsField,
    CheckboxField,
    SheetField,
    ItemsField,
    CustomItemFields,
    NumberField
  },
  props: ['opened', 'insertOptions', 'linkedFromOptions', 'numberLinkedFromOptions'],
  data () {
    return {
      model: {
        name: '',
        label: '',
        type: 'string',
        options: null,
        columns: [],
        itemFields: [],
        linkedFrom: '',
        linkedValues: [],
        dashboard: 0,
        twoDigits: true,
        defaultValue: null,
      },
      typeOptions: ['string', 'textarea', 'number', 'checkbox', 'file', 'files', 'sheet', 'items'],
      optionsMode: 'NoOptions',
      fixedOptions: [],
      orgUsersOptions: 'All',
      insertAfter: 0,
      nameConstraints: [
        {match: /^([a-zA-Z][a-zA-Z\d]*)$/, info: 'Name must only contain alphabet and digital charactors.'},
        {notMatch: /(^id$|^folderId$|^state$|^stateEvents$|^createdBy$|^All$)/, info: 'Name must NOT be reserved names.'}
      ],
      optionsDeprived: {
        from: '',
        mappings: [],
      },
      optionsDeprivedMappingFields: [
        {name: 'from', type: 'string', label: 'Derived From'},
        {name: 'deprivedOptions', type: 'strings', label: 'Derived Options'},
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
        this.model.linkedFrom = ''
        this.optionsMode = 'NoOptions'
        this.insertAfter = this.insertOptions.length - 2
      }
    }
  },
  methods: {
    close () {
      this.$emit('new-custom-field-modal-closed')
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
        } else if (typeof(this.field.options) == 'string') {
          this.model.options = this.orgUsersOptions
        } else {
          if (this.optionsDeprived.from && this.optionsDeprived.mappings.length) {
            this.model.options = JSON.parse(JSON.stringify(this.optionsDeprived))
          } else {
            this.model.options = null
          }
        }
      }
      if (this.model.type != 'string' && this.model.type != 'number') {
        this.model.dashboard = 0
        this.model.defaultValue = null
      }
      this.$emit('new-custom-field-modal-saved', [this.insertAfter, this.model])
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
    onInsertAfterChanged (val) {
      this.insertAfter = val[1]
    },
    onColumnsValueChanged (val) {
      this.model.columns = val[1]
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

.my-columns {
  margin-top: -15px;
}
</style>
