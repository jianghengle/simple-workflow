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

        <div class="field">
          <label class="label">Receivers</label>
          <div>
            <div class="control mb-1" v-for="(r, i) in message.receivers" :key="'receivers-element-' + i">
              <span class="tag is-medium">
                <span>{{r}}</span>
                <button class="delete ml-3" @click="removeReceiver(i)"></button>
              </span>
            </div>
          </div>

          <div class="field has-addons">
            <div class="control has-icons-left">
              <span class="select">
                <select v-model="selectedGroup">
                  <option v-for="(g, i) in groups" :key="'receivers-group-options'+i">{{g}}</option>
                </select>
              </span>
              <span class="icon is-small is-left">
                <i class="fas fa-filter"></i>
              </span>
            </div>
            <div class="control">
              <div class="select" >
                <select v-model="selectedReceiver">
                  <option  v-for="(opt, i) in selectedGroupUsers" :key="'strings-field-option-' + i" :value="opt.value">
                    {{opt.label}}
                  </option>
                </select>
              </div>
            </div>
            <div class="control">
              <a class="button" @click="addReceiver">
                <span class="icon is-small">
                  <i class="fas fa-plus"></i>
                </span>
              </a>
            </div>
          </div>
          
        </div>

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
      },
      selectedGroup: 'All',
      selectedReceiver: ''
    }
  },
  computed: {
    server () {
      return this.$store.state.config.server
    },
    orgUsers () {
      if (!this.$store.state.org.orgUsers) {
        return []
      }
      return this.$store.state.org.orgUsers.map(u => u).sort((a, b) => {
        return String(a.username).localeCompare(String(b.username))
      })
    },
    groups () {
      if (!this.orgUsers) {
        return []
      }
      var groups = []
      for (const u of this.orgUsers) {
        groups = groups.concat(u.groups)
      }
      groups = [...new Set(groups)]
      groups.sort()
      groups.unshift('All')
      return groups
    },
    groupUsers () {
      if (!this.orgUsers) {
        return {}
      }
      var groupUsers = {}
      for (const g of this.groups) {
        groupUsers[g] = []
      }
      for (const u of this.orgUsers) {
        groupUsers['All'].push(u)
        for (const g of u.groups) {
          groupUsers[g].push(u)
        }
      }
      return groupUsers
    },
    selectedGroupUsers () {
      var users = this.groupUsers[this.selectedGroup]
      if (!users) {
        return []
      }
      return users.map(u => ({value: u.email, label: u.username + ' <' + u.email + '>'}))
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
    removeReceiver (index) {
      this.message.receivers.splice(index, 1)
    },
    addReceiver () {
      if (!this.selectedReceiver || this.message.receivers.includes(this.selectedReceiver)) {
        return
      }
      this.message.receivers.push(this.selectedReceiver)
    },
  },
}
</script>

<style scoped>

</style>
