<template>
  <div class="modal"
      :class="{'is-active': opened}">
    <div class="modal-background"></div>
    <div class="modal-card">
      <header class="modal-card-head">
        <p class="modal-card-title">Send Email about Workflow</p>
        <button class="delete" @click="close"></button>
      </header>
      <section class="modal-card-body" >

        <strings-field :name="'receivers'" :label="'Receivers'" :value="message.receivers" @value-changed="onValueChanged" :options="receiverOptions" />
        <textarea-field :name="'additionalMessage'" :label="'Additional Message'" :value="message.additionalMessage" @value-changed="onValueChanged" />
        
        <div v-if="error" class="notification is-danger is-light mt-4">
          <button class="delete" @click="error=''"></button>
          {{error}}
        </div>

        <div v-if="success" class="notification is-success is-light mt-4">
          <button class="delete" @click="success=''"></button>
          {{success}}
        </div>

      </section>
      <footer class="modal-card-foot">
        <a class="button is-link" :disabled="!canSend" :class="{'is-loading': sending}" @click="send">Send</a>
        <a class="button" @click="close">Cancel</a>
      </footer>
    </div>
  </div>
</template>

<script>
import StringsField from '@/components/form/StringsField'
import TextareaField from '@/components/form/TextareaField'

export default {
  name: 'send-email-modal',
  components: {
    StringsField,
    TextareaField
  },
  props: ['opened', 'workflow'],
  data () {
    return {
      sending: false,
      error: '',
      success: '',
      message: {
        receivers: [],
        additionalMessage: '',
        workflowLink: window.location.href,
      }
    }
  },
  computed: {
    server () {
      return this.$store.state.config.server
    },
    orgUsers () {
      return this.$store.state.org.orgUsers
    },
    configId () {
      return this.$route.params.configId
    },
    workflowId () {
      return this.$route.params.workflowId
    },
    orgWorkflowConfigs () {
      return this.$store.state.org.orgWorkflowConfigs
    },
    orgWorkflowConfig () {
      if (!this.orgWorkflowConfigs) {
        return null
      }
      for(const workflowConfig of this.orgWorkflowConfigs) {
        if (workflowConfig.id == this.configId) {
          return workflowConfig
        }
      }
      return null
    },
    receiverOptions () {
      if (!this.orgUsers || !this.orgWorkflowConfig) {
        return []
      }
      var userGroup = this.orgWorkflowConfig.userGroup
      if (userGroup == 'All') {
        return this.orgUsers.map(u => u.email)
      }
      return this.orgUsers.filter(u => {
        return u.groups.includes(userGroup
      )}).map(u => u.email)
    },
    canSend () {
      return this.message.receivers.length
    },
  },
  methods: {
    close () {
      this.$emit('send-email-modal-closed')
    },
    send () {
      if (!this.canSend) {
        return
      }
      this.message.workflowId = this.workflowId
      this.message.workflowConfigId = this.configId
      this.success = ''
      this.error = ''
      this.sending = true

      this.$http.post(this.server + '/org/send-email-about-workflow', this.message).then(resp => {
        this.model = resp.body
        this.sending = false
        this.success = 'The email has been successfully sent.'
      }, err => {
        this.error = err
        this.sending = false
      })
    },
    onValueChanged (val) {
      var name = val[0]
      var value = val[1]
      this.message[name] = value
    },
  },
}
</script>

<style scoped>

</style>
