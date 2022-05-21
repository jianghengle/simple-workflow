<template>
  <div class="container">
    <section class="section">
      <h1 class="title">Welcome to Simple Workflow!</h1>
      <h2 class="subtitle">
        A simple tool to manage your workflows.
      </h2>

      <div v-if="token">
        <div v-if="orgIds">
          <div v-if="orgIds.length">
            <article class="message is-success">
              <div class="message-body">
                You will be directed to your org page shortly... but please refresh or sign in again if not.
              </div>
            </article>
          </div>
          <div v-else>
            <article class="message is-warn">
              <div class="message-body">
                Seems you are not in any org...
              </div>
            </article>
          </div>
        </div>
        <div v-else>
          <article class="message is-warn">
            <div class="message-body">
              Waiting for your org info to redirect...
            </div>
          </article>
        </div>
      </div>
      <div v-else>
        <div class="field">
          <label class="label">Email</label>
          <div class="control has-icons-left has-icons-right">
            <input class="input" type="email" placeholder="Email" v-model="email">
            <span class="icon is-small is-left">
              <i class="fas fa-envelope"></i>
            </span>
          </div>
        </div>

        <div class="field">
          <label class="label">Password</label>
          <div class="control has-icons-left has-icons-right">
            <input class="input" type="password" placeholder="Password" v-model="password" @keyup.enter="signin">
            <span class="icon is-small is-left">
              <i class="fas fa-key"></i>
            </span>
          </div>
        </div>

        <div class="field">
          <div class="control">
            <label class="checkbox">
              <input type="checkbox" v-model="rememberMe">
              Remember me
            </label>
          </div>
        </div>

        <div class="field is-grouped">
          <div class="control">
            <button class="button is-link" :class="{'is-loading': waiting}" @click="signin">Sign in</button>
          </div>
        </div>

        <div v-if="error" class="notification is-danger is-light">
          <button class="delete" @click="error=''"></button>
          {{error}}
        </div>

        <div>
          <router-link :to="'/user/forgot-password'">
            Forgot your password?
          </router-link>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import Vue from 'vue'

export default {
  name: 'Home',
  data () {
    return {
      email: '',
      password: '',
      rememberMe: true,
      error: '',
      waiting: false,
    }
  },
  computed: {
    server () {
      return this.$store.state.config.server
    },
    token () {
      return this.$store.state.user.token
    },
    orgIds () {
      return this.$store.state.user.orgIds
    },
  },
  watch: {
    orgIds: function (val) {
      if (val && val.length) {
        var orgId = localStorage.getItem('orgId')
        if (orgId && val.includes(orgId)) {
          this.$router.push('/org/' + orgId + '/workflow-configs')
        } else {
          this.$router.push('/org/' + val[0] + '/workflow-configs')
        }
      }
    },
  },
  methods: {
    signin () {
      this.email = this.email.trim().toLowerCase()
      this.waiting = true
      var message = {email: this.email, password: this.password}
      this.$http.post(this.server + '/user/auth-user', message).then(resp => {
        if (resp.body) {
          var user = resp.body
          Vue.http.headers.common['Authorization'] = user.token
          this.$store.commit('user/setUser', user)
          if (this.rememberMe) {
            localStorage.setItem('token', user.token)
            localStorage.setItem('email', user.email)
            localStorage.setItem('username', user.username)
          }
          this.email = ''
          this.password = ''
        } else {
          this.error = 'Failed to sign in!'
          this.$store.commit('user/reset')
        }
        this.waiting = false
      }, err => {
        this.error = err.body
        this.waiting = false
      })
    },
  },
}
</script>
