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

      <string-field :name="'email'" :label="'Email'" :value="email" :readonly="true" />

      <string-field :name="'username'" :label="'Full Name'" :value="newUsername" @value-changed="onUsernameChanged" />

      <div class="field is-grouped mt-5">
        <p class="control">
          <a class="button is-link" :class="{'is-loading': waiting, 'my-disabled-button': !usernameChanged}" :disabled="!usernameChanged" @click="save">
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
  },
  mounted () {
    this.newUsername = this.username
  },
}
</script>

<style scoped lang="scss">
 
</style>
