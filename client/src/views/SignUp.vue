<template>
  <div class="container">
    <section class="section">
      <h1 class="title is-4">Sign Up</h1>
      <div class="field">
         <label class="label">Email</label>
         <div class="control has-icons-left has-icons-right">
            <input class="input" type="email" placeholder="Email" v-model="email">
            <span class="icon is-small is-left">
              <i class="fas fa-envelope"></i>
            </span>
         </div>
         <p class="help is-info">We will send you an email to verify your email address and finish the sign up process.</p>
      </div>
      <div class="field is-grouped">
        <div class="control">
          <button class="button is-link" :class="{'is-loading': waiting}" :disabled="!canSubmit" @click="submit">Submit</button>
        </div>
      </div>
      <div v-if="error" class="notification is-danger is-light">
        <button class="delete" @click="error=''"></button>
        {{error}}
      </div>
      <div v-if="success" class="notification is-success is-light">
        An email has been sent to your email address, which contains the instruction to set your password.
      </div>
    </section>
  </div>
</template>

<script>
import Vue from 'vue'

export default {
  name: 'SignUp',
  data () {
    return {
      email: '',
      success: false,
      error: '',
      waiting: false,
    }
  },
  computed: {
    server () {
      return this.$store.state.config.server
    },
    canSubmit () {
      return this.isValidEmail(this.email)
    },
  },
  methods: {
    isValidEmail (email) {
      return String(email)
        .toLowerCase()
        .match(
          /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
        )
    },
    submit () {
      if (this.waiting || !this.canSubmit) {
        return
      }
      this.error = ''
      this.success = false
      this.email = this.email.trim().toLowerCase()
      var message = {email: this.email}
      this.$http.post(this.server + '/user/sign-up', message).then(resp => {
        this.success = true
        this.waiting = false
      }, err => {
        this.error = err.body
        this.waiting = false
      })
    },
  },
}
</script>
