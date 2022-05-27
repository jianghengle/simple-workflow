<template>
  <div class="container mt-5 px-2">
    <div v-if="!token">
      <article class="message is-danger">
        <div class="message-body">
          You have not signed in yet. Please go back to <a href="/">home page</a> to sign in first.
        </div>
      </article>
    </div>
    <div v-else>
      <a class="button back-button" @click="$router.go(-1)">
        <span class="icon back-icon">
          <i class="fas fa-angle-left"></i>
        </span>
      </a>

      <hr />

      <h1 class="title is-4">Update Full Name</h1>
        
      <string-field :name="'email'" :label="'Email'" :value="email" :readonly="true" />

      <string-field :name="'username'" :label="'Full Name'" :value="newUsername" @value-changed="onUsernameChanged" />

      <div class="field is-grouped mt-5">
        <p class="control">
          <a class="button is-link" :disabled="!usernameChanged" :class="{'is-loading': waiting}" @click="save">
            Update
          </a>
        </p>
      </div>

      <div v-if="error" class="notification is-danger is-light">
        <button class="delete" @click="error=''"></button>
        {{error}}
      </div>

      <div v-if="success" class="notification is-success is-light">
        <button class="delete" @click="success=''"></button>
        {{success}}
      </div>

      <hr />

      <h1 class="title is-4">Request to join org</h1>

      <string-field :name="'orgId'" :label="'Org Id to request to join'" :value="newOrgId" @value-changed="onOrgIdChanged" />
      <string-field :name="'email'" :label="'Email'" :value="email" :readonly="true" />
      <string-field :name="'username'" :label="'Full Name'" :value="username" :readonly="true" />

      <div class="field is-grouped mt-5">
        <p class="control">
          <a class="button is-link" :disabled="!newOrgId" :class="{'is-loading': waiting}" @click="request">
            Request
          </a>
        </p>
      </div>

      <div v-if="requestError" class="notification is-danger is-light">
        <button class="delete" @click="requestError=''"></button>
        {{requestError}}
      </div>

      <div v-if="requestSuccess" class="notification is-success is-light">
        <button class="delete" @click="requestSuccess=''"></button>
        {{requestSuccess}}
      </div>

    </div>

    
  </div>
</template>

<script>
import Vue from 'vue'
import StringField from '@/components/form/StringField'

export default {
  name: 'UserEdit',
  components: {
    StringField
  },
  data () {
    return {
      error: '',
      success: '',
      waiting: false,
      newUsername: '',
      newOrgId: '',
      requestError: '',
      requestSuccess: '',
    }
  },
  computed: {
    server () {
      return this.$store.state.config.server
    },
    token () {
      return this.$store.state.user.token
    },
    email () {
      return this.$store.state.user.email
    },
    username () {
      return this.$store.state.user.username
    },
    usernameChanged () {
      return this.username != this.newUsername
    },
  },
  watch: {
    username: function (val) {
      this.newUsername = val
    },
  },
  methods: {
    onUsernameChanged (val) {
      this.newUsername = val[1]
    },
    save () {
      if (this.waiting || !this.usernameChanged) {
        return
      }
      this.waiting = true
      this.$http.post(this.server + '/user/update-username', {username: this.newUsername}).then(resp => {
        var user = resp.body
        this.$store.commit('user/setUser', user)
        this.success = 'Update succeeded.'
        this.waiting = false
      }, err => {
        this.error = err
        this.waiting = false
      })
    },
    onOrgIdChanged (val) {
      this.newOrgId = val[1]
    },
    request () {
      if (this.waiting || !this.newOrgId) {
        return
      }
      this.newOrgId = this.newOrgId.toLowerCase()
      this.waiting = true
      var message = {
        orgId: this.newOrgId,
        email: this.email,
        username: this.username,
      }
      this.$http.post(this.server + '/user/request-to-join-org', message).then(resp => {
        this.requestSuccess = 'Successfully sent the request. The org admin will review your request and get back to you.'
        this.waiting = false
      }, err => {
        this.requestError = err.body.err
        this.waiting = false
      })
    },
  },
  mounted () {
    this.newUsername = this.username
  },
}
</script>

<style scoped lang="scss">
 
</style>
