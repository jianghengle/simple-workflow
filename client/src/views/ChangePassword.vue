<template>
  <div class="container">
    <section class="section">
      <h1 class="title is-4">Set Password</h1>
      <div v-if="waiting">
        <span class="icon is-medium is-size-4">
          <i class="fas fa-spinner fa-pulse"></i>
        </span>
      </div>
      <div class="field">
         <label class="label">Email</label>
         <div class="control has-icons-left has-icons-right">
            <input class="input" type="email" placeholder="Email" v-model="email" readonly disabled>
            <span class="icon is-small is-left">
               <i class="fas fa-envelope"></i>
            </span>
         </div>
      </div>
      <div class="field" v-if="mode == 'new'">
         <label class="label">Full Name</label>
         <div class="control has-icons-left has-icons-right">
            <input class="input" type="email" placeholder="Full name" v-model="username">
            <span class="icon is-small is-left">
               <i class="fas fa-user"></i>
            </span>
         </div>
      </div>
      <div class="field">
        <label class="label">Password</label>
        <div class="control has-icons-left has-icons-right">
          <input class="input" type="password" placeholder="Password" v-model="password">
          <span class="icon is-small is-left">
            <i class="fas fa-key"></i>
          </span>
        </div>
      </div>
      <div class="field">
        <label class="label">Confirm Password</label>
        <div class="control has-icons-left has-icons-right">
          <input class="input" type="password" placeholder="Password" v-model="passwordAgain">
          <span class="icon is-small is-left">
            <i class="fas fa-key"></i>
          </span>
        </div>
      </div>
      <div class="field is-grouped">
        <div class="control">
          <button class="button is-link" :class="{'is-loading': changing}" :disabled="!canChange" @click="changePassword">Set password</button>
        </div>
      </div>
      <div v-if="error" class="notification is-danger is-light">
        <button class="delete" @click="error=''"></button>
        {{error}}
      </div>
      <div v-if="success" class="notification is-success is-light">
        The password has been set. Please go back to <router-link :to="'/'">Home page</router-link> to sign in
      </div>
    </section>
  </div>
</template>

<script>
import Vue from 'vue'

export default {
  name: 'ChangePassword',
  data () {
    return {
      passwordReset: null,
      password: '',
      passwordAgain: '',
      success: false,
      error: '',
      waiting: false,
      changing: false,
      username: '',
    }
  },
  computed: {
    server () {
      return this.$store.state.config.server
    },
    email () {
      return this.$route.params.email
    },
    key () {
      return this.$route.params.key
    },
    mode () {
      return this.$route.params.mode
    },
    canChange () {
      return this.password && this.password == this.passwordAgain
    },
  },
  methods: {
    changePassword () {
      if (this.changing || !this.canChange) {
        return
      }
      this.changing = true
      this.error = ''
      this.success = false
      var message = {email: this.email, password: this.password, token: this.key}
      if (this.mode == 'new') {
        message.username = this.username
      }
      this.$http.post(this.server + '/user/reset-password', message).then(resp => {
        this.success = true
        this.changing = false
      }, err => {
        this.error = 'Failed to change the password!'
        this.changing = false
      })
    },
  },
}
</script>
