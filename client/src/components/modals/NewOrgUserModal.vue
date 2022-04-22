<template>
  <div class="modal"
      :class="{'is-active': opened}">
    <div class="modal-background"></div>
    <div class="modal-card">
      <header class="modal-card-head">
        <p class="modal-card-title">New Org User</p>
        <button class="delete" @click="close"></button>
      </header>
      <section class="modal-card-body" v-if="model">

        <div v-if="error" class="notification is-danger is-light">
          <button class="delete" @click="error=''"></button>
          {{error}}
        </div>

        <string-field :name="'email'" :label="'Email'" :value="model.email" @value-changed="onValueChanged" />

        <string-field v-if="!canEditRole" :label="'Role'" :value="model.role" :readonly="true" :options="['Owner', 'Admin', 'User']" />
        <string-field v-if="canEditRole" :name="'role'" :label="'Role'" :value="model.role" :options="['Admin', 'User']" @value-changed="onValueChanged" />

        <strings-field :name="'groups'" :label="'Groups'" :value="model.groups" @value-changed="onValueChanged" :options="{'allowNew': true, 'values': availableGroups}" />

      </section>
      <footer class="modal-card-foot">
        <a class="button is-link"  :disabled="!canCreate" :class="{'is-loading': waiting}" @click="save">Create</a>
        <a class="button" @click="close">Cancel</a>
      </footer>
    </div>
  </div>
</template>

<script>
import StringField from '@/components/form/StringField'
import StringsField from '@/components/form/StringsField'

export default {
  name: 'new-org-user-modal',
  components: {
    StringField,
    StringsField
  },
  props: ['opened', 'defaultGroup'],
  data () {
    return {
      model: {
        email: '',
        role: 'User',
        groups: [],
      },
      waiting: false,
      error: '',
    }
  },
  computed: {
    server () {
      return this.$store.state.config.server
    },
    email () {
      return this.$store.state.user.email
    },
    orgUsers () {
      return this.$store.state.org.orgUsers
    },
    actor () {
      if (!this.email || !this.orgUsers) {
        return null
      }
      var email = this.email
      return this.orgUsers.filter(function(u){
        return u.email == email
      })[0]
    },
    canEditRole () {
      if (!this.actor) {
        return false
      }
      return this.actor.role == 'Owner'
    },
    availableGroups () {
      if (!this.orgUsers) {
        return
      }
      var groups = new Set()
      this.orgUsers.forEach(function(user) {
        if (user.groups) {
          user.groups.forEach(function(g) {
            groups.add(g)
          })
        }
      })
      return Array.from(groups)
    },
    canCreate () {
      return this.model.email
    },
  },
  watch: {
    opened: function (val) {
      if (val) {
        this.model.email = ''
        this.model.groups = []
        if (this.defaultGroup && this.defaultGroup != 'All') {
          this.model.groups = [this.defaultGroup]
        }
      }
    },
  },
  methods: {
    close () {
      this.$emit('new-org-user-modal-closed')
    },
    onValueChanged (val) {
      var name = val[0]
      var value = val[1]
      if (this.model[name] != value) {
        this.model[name] = value
      }
    },
    save () {
      if (this.waiting || !this.canCreate) {
        return
      }
      this.waiting = true
      this.model.email = this.model.email.toLowerCase()
      this.$http.post(this.server + '/org/create-org-user', this.model).then(resp => {
        var orgUser = resp.body
        this.$store.commit('org/updateOrgUser', orgUser)
        this.waiting = false
        this.close()
      }, err => {
        this.error = err
        this.waiting = false
      })
    },
  },
}
</script>
