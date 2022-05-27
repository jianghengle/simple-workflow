<template>
  <div class="container">
    <section class="section">
      <h1 class="title is-4">Request to Join Org</h1>

      <div class="field">
        <label class="label">Org Id to Request to Join</label>
        <div class="control">
          <input class="input" type="text" placeholder="Org Id" v-model="orgId">
        </div>
      </div>

      <div class="field">
        <label class="label">Your Email</label>
        <div class="control">
          <input class="input" type="email" placeholder="Email" v-model="email">
        </div>
      </div>

      <div class="field">
        <label class="label">Your Full Name</label>
        <div class="control">
          <input class="input" type="text" placeholder="Full Name" v-model="username">
        </div>
      </div>

      <div class="field is-grouped mt-5">
        <div class="control">
          <button class="button is-link" :class="{'is-loading': waiting}" :disabled="!canRequest" @click="request">Request</button>
        </div>
      </div>

      <div v-if="error" class="notification is-danger is-light">
        <button class="delete" @click="error=''"></button>
        {{error}}
      </div>

      <div v-if="success" class="notification is-success is-light">
        {{success}}
      </div>
    </section>
  </div>
</template>

<script>
import Vue from 'vue'

export default {
  name: 'RequestToJoinOrg',
  data () {
    return {
      orgId: '',
      email: '',
      username: '',
      success: '',
      error: '',
      waiting: false,
    }
  },
  computed: {
    server () {
      return this.$store.state.config.server
    },
    canRequest () {
      return this.orgId.trim() && this.username.trim() && this.isValidEmail(this.email)
    },
  },
  methods: {
    request () {
      if (this.waiting || !this.canRequest) {
        return
      }
      this.orgId = this.orgId.trim().toLowerCase()
      this.email = this.email.trim().toLowerCase()
      this.username = this.username.trim()

      this.waiting = true
      this.error = ''
      this.success = ''

      var message = {
        orgId: this.orgId,
        email: this.email,
        username: this.username,
      }
      this.$http.post(this.server + '/user/request-to-join-org', message).then(resp => {
        this.success = 'Successfully sent the request. The org admin will review your request and get back to you.'
        this.waiting = false
      }, err => {
        this.error = err.body.err
        this.waiting = false
      })
    },
    isValidEmail (email) {
      return String(email)
        .toLowerCase()
        .match(
          /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
        )
    },
  },
}
</script>
