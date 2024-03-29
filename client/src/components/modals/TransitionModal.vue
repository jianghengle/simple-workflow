<template>
  <div class="modal"
      :class="{'is-active': opened}">
    <div class="modal-background"></div>
    <div class="modal-card">
      <header class="modal-card-head">
        <p class="modal-card-title">Edit Transition</p>
        <button class="delete" @click="close"></button>
      </header>
      <section class="modal-card-body" v-if="localModel">
        <string-field :label="'From State'" :value="stateName" :readonly="true" :options="stateNames" />
        <string-field :name="'toState'" :label="'To State'" :value="localModel.toState" @value-changed="onValueChanged" :options="toStateOptions" />
        <string-field :name="'actionLabel'" :label="'Action Label'" :value="localModel.actionLabel" @value-changed="onValueChanged"
          :helpInfo="'The text shown on the transition button.'" />

        <items-field :name="'permissions'" :label="'Permissions'" :value="localModel.permissions" :fields="permissionFields" @value-changed="onValueChanged"
          :helpInfo="'Leave Condition Field empty if no condition needed.'" />

        <strings-field :name="'transitionNotifyingGroups'" :label="'Transition Notifying Groups'" :value="localModel.transitionNotifyingGroups" @value-changed="onValueChanged" :options="groupOptions" />
        <strings-field :name="'transitionNotifyingOthers'" :label="'Transition Notifying Others'" :value="localModel.transitionNotifyingOthers" @value-changed="onValueChanged" :options="otherOptions" />
      </section>
      <footer class="modal-card-foot">
        <a class="button is-link" :disabled="!canSave" :class="{'my-disabled-button': !canSave}" @click="save">Save</a>
        <a class="button is-danger" @click="remove">Remove</a>
        <a class="button" @click="close">Cancel</a>
      </footer>
    </div>
  </div>
</template>

<script>
import StringField from '@/components/form/StringField'
import StringsField from '@/components/form/StringsField'
import ItemsField from '@/components/form/ItemsField'

export default {
  name: 'transition-modal',
  components: {
    StringField,
    StringsField,
    ItemsField
  },
  props: ['opened', 'fields', 'stateName', 'stateNames', 'model'],
  data () {
    return {
      localModel: null,
    }
  },
  computed: {
    canSave () {
      if (!this.localModel) {
        return false
      } 
      return this.localModel.toState.trim() && this.localModel.actionLabel.trim()
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
      var fieldNames = this.fields.map(f => f.name)
      fieldNames.push('Workflow Creator')
      return fieldNames
    },
    toStateOptions () {
      return this.stateNames.filter(n => n != this.stateName)
    },
    numberFields () {
      var fieldNames = this.fields.filter(f => f.type == 'number').map(f => f.name)
      return fieldNames
    },
    allFields () {
      return this.fields.map(f => f.name)
    },
    permissionFields () {
      return [
        {name: 'groups', label: 'Groups', type: 'strings', optionValues: this.groupOptions},
        {name: 'others', label: 'Others', type: 'strings', optionValues: this.otherOptions},
        {name: 'conditionField', label: 'Condition Field', type: 'string', optionValues: this.numberFields},
        {name: 'conditionOperator', label: 'Condition Operator', type: 'string', options: ['<', '<=', '==', '>=', '>']},
        {name: 'conditionOperand', label: 'Condition Operand', type: 'number'},
        {name: 'requiredFields', label: 'Required Fields', type: 'strings', optionValues: this.allFields},
      ]
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
      this.$emit('transition-modal-closed')
    },
    save () {
      if (!this.canSave) {
        return
      }
      this.localModel.actionLabel = this.localModel.actionLabel.trim()
      this.$emit('transition-modal-saved', this.localModel)
    },
    remove () {
      var confirm = {
        title: 'Remove Transition',
        message: 'Are you sure to remove this transition?',
        button: 'Yes, I am sure.',
        callback: {
          context: this,
          method: this.removeConfirmed,
          args: []
        }
      }
      this.$store.commit('modals/openConfirmModal', confirm)
    },
    removeConfirmed () {
      this.$emit('transition-modal-removed')
    },
    onValueChanged (val) {
      var name = val[0]
      var value = val[1]
      if (this.localModel[name] != value) {
        this.localModel[name] = value
      }
    },
    onPermissionValueChanged (val) {
      var name = val[0]
      var value = val[1]
      if (this.localModel.actor[name] != value) {
        this.localModel.actor[name] = value
      }
    },
  },
}
</script>

<style scoped>

</style>
