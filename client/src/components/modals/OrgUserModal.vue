<template>
  <div class="modal"
      :class="{'is-active': opened}">
    <div class="modal-background"></div>
    <div class="modal-card">
      <header class="modal-card-head">
        <p class="modal-card-title">Org User</p>
        <button class="delete" @click="close"></button>
      </header>
      <section class="modal-card-body" v-if="orgUser && model">

        <div v-if="error" class="notification is-danger is-light">
          <button class="delete" @click="error=''"></button>
          {{error}}
        </div>

        <string-field :label="'Email'" :value="orgUser.email" :readonly="true" />

        <string-field v-if="!isRoleEditable" :label="'Role'" :value="orgUser.role" :readonly="true" :options="['Owner', 'Admin', 'User']" />
        <string-field v-if="isRoleEditable" :name="'role'" :label="'Role'" :value="model.role" :options="['Admin', 'User']" @value-changed="onValueChanged" />

        <strings-field :name="'groups'" :label="'Groups'" :value="model.groups" @value-changed="onValueChanged" :options="{'allowNew': true, 'values': availableGroups}" />

      </section>
      <footer class="modal-card-foot">
        <a class="button is-link"  :disabled="!modelChanged" :class="{'is-loading': waiting}" @click="save">Update</a>
        <a class="button is-danger" v-if="canDelete" :class="{'is-loading': waiting}" @click="deleteOrgUser">Delete</a>
        <a class="button" @click="close">Cancel</a>
      </footer>
    </div>
  </div>
</template>

<script>
import StringField from '@/components/form/StringField'
import StringsField from '@/components/form/StringsField'

export default {
  name: 'org-user-modal',
  components: {
    StringField,
    StringsField
  },
  props: ['opened', 'orgUser'],
  data () {
    return {
      model: null,
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
    orgUserEmail () {
      return this.orgUser.email
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
    isRoleEditable () {
      if (!this.orgUser) {
        return false
      }
      if (this.orgUser.role == 'Owner') {
        return false
      }
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
    modelChanged () {
      if (!this.model || !this.orgUser) {
        return false
      }
      return this.orgUser.role != this.model.role
        || JSON.stringify(this.orgUser.groups) != JSON.stringify(this.model.groups)
    },
    canDelete () {
      if (!this.orgUser) {
        return false
      }
      if (this.orgUser.role == 'Owner') {
        return false
      }
      if (!this.actor) {
        return false
      }
      if (this.actor.role == 'Owner') {
        return true
      }
      if (this.actor.role == 'Admin') {
        if (this.orgUser.role == 'Admin') {
          return false
        }
        return true
      }
      return false
    },
  },
  watch: {
    orgUser: function (val) {
      if (val) {
        this.makeOrgUserModel()
      }
    },
  },
  methods: {
    close () {
      this.$emit('org-user-modal-closed')
    },
    makeOrgUserModel () {
      this.model = {
        role: this.orgUser.role,
        groups: this.orgUser.groups.slice()
      }
    },
    onValueChanged (val) {
      var name = val[0]
      var value = val[1]
      if (this.model[name] != value) {
        this.model[name] = value
      }
    },
    save () {
      if (this.waiting || !this.modelChanged) {
        return
      }
      this.waiting = true
      var message = {
        email: this.orgUserEmail,
        updates: this.model
      }
      this.$http.post(this.server + '/org/update-org-user', message).then(resp => {
        var orgUser = resp.body
        this.$store.commit('org/updateOrgUser', orgUser)
        this.waiting = false
        this.close()
      }, err => {
        this.error = err
        this.waiting = false
      })
    },
    deleteOrgUser () {
      if (this.waiting) {
        return
      }
      var confirm = {
        title: 'Delete Org User',
        message: 'Are you sure to delete this org user: ' + this.orgUserEmail + '?',
        button: 'Yes, I am sure.',
        callback: {
          context: this,
          method: this.deleteConfirmed,
          args: []
        }
      }
      this.$store.commit('modals/openConfirmModal', confirm)
    },
    deleteConfirmed () {
      this.waiting = true
      this.$http.post(this.server + '/org/delete-org-user', {email: this.orgUserEmail}).then(resp => {
        var orgUser = resp.body
        this.$store.commit('org/deleteOrgUser', this.orgUserEmail)
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
