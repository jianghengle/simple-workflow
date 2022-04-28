<template>
  <div class="modal"
      :class="{'is-active': opened}">
    <div class="modal-background"></div>
    <div class="modal-card">
      <header class="modal-card-head">
        <p class="modal-card-title">New Transition</p>
        <button class="delete" @click="close"></button>
      </header>
      <section class="modal-card-body" v-if="localModel">
        <string-field :label="'From State'" :value="stateName" :readonly="true" :options="stateNames" />
        <string-field :name="'toState'" :label="'To State'" :value="localModel.toState" @value-changed="onValueChanged" :options="toStateOptions" />
        <string-field :name="'actionLabel'" :label="'Action Label'" :value="localModel.actionLabel" @value-changed="onValueChanged" />
        <strings-field :name="'groups'" :label="'Actor Groups'" :value="localModel.actor.groups" @value-changed="onPermissionValueChanged" :options="groupOptions" />
        <strings-field :name="'others'" :label="'Actor Others'" :value="localModel.actor.others" @value-changed="onPermissionValueChanged" :options="otherOptions" />
      </section>
      <footer class="modal-card-foot">
        <a class="button is-link" :disabled="!canSave" @click="save">Save</a>
        <a class="button" @click="close">Cancel</a>
      </footer>
    </div>
  </div>
</template>

<script>
import StringField from '@/components/form/StringField'
import StringsField from '@/components/form/StringsField'

export default {
  name: 'new-transition-modal',
  components: {
    StringField,
    StringsField,
  },
  props: ['opened', 'fields', 'stateName', 'stateNames'],
  data () {
    return {
      localModel: {
        toState: '',
        actionLabel: '',
        actor: {
           groups: [],
           others: [],
        },
      },
    }
  },
  computed: {
    canSave () {
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
  },
  methods: {
    close () {
      this.$emit('new-transition-modal-closed')
    },
    save () {
      if (!this.canSave) {
        return
      }
      this.localModel.actionLabel = this.localModel.actionLabel.trim()
      this.$emit('new-transition-modal-saved', this.localModel)
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
