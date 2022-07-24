<template>
  <div class="container mt-5 px-2">
    <article class="message is-danger" v-if="!token">
      <div class="message-body">
        You have not signed in yet. Please go back to <a href="/">home page</a> to sign in first.
      </div>
    </article>
    <div v-if="token">
      <div v-if="!orgUser">
        <span class="icon is-medium is-size-4">
          <i class="fas fa-spinner fa-pulse"></i>
        </span>
      </div>
      <div v-else>
        <div v-if="!canAccess">
          <span class="icon is-medium is-size-4">
            <i class="fas fa-spinner fa-pulse"></i>
          </span>
        </div>
        <div v-else>
          <div class="mt-3">
            <div v-if="waiting">
              <span class="icon is-medium is-size-4">
                <i class="fas fa-spinner fa-pulse"></i>
              </span>
            </div>
            <div v-else>
              <div v-if="orgWorkflowConfig && model">
                <div class="mb-5">
                  <nav class="breadcrumb" aria-label="breadcrumbs">
                    <ul>
                      <li><router-link :to="'/org/' + orgId + '/workflow-folder/' + configId + '/' + configId">{{orgWorkflowConfig.name}}</router-link></li>
                      <li class="is-active"><a href="#" aria-current="page">New</a></li>
                    </ul>
                  </nav>
                </div>


                <workflow-model :model="model" @model-updated="onModelUpdated" />

                <div class="field is-grouped mt-5">
                  <div class="control">
                    <button class="button is-link" :class="{'is-loading': creating}" @click="createWorkflow">Create</button>
                  </div>
                </div>

                <div v-if="error" class="notification is-danger is-light">
                  <button class="delete" @click="error=''"></button>
                  {{error}}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import WorkflowModel from '@/components/workflow/WorkflowModel'

export default {
  name: 'NewWorkflow',
  components: {
    WorkflowModel
  },
  data () {
    return {
      error: '',
      waiting: false,
      model: null,
      newModel: null,
      creating: false,
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
    copyFrom () {
      return this.$route.params.copyFrom
    },
    orgId () {
      return this.$route.params.orgId
    },
    org () {
      return this.$store.state.org.org
    },
    orgUsers () {
      return this.$store.state.org.orgUsers
    },
    orgUser () {
      if (!this.email || !this.orgUsers) {
        return null
      }
      var email = this.email
      return this.orgUsers.filter(function(u){
        return u.email == email
      })[0]
    },
    configId () {
      return this.$route.params.configId
    },
    folderId () {
      return this.$route.params.folderId
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
    firstStateName () {
      if (!this.orgWorkflowConfig) {
        return null
      }
      return this.orgWorkflowConfig.states[0].name
    },
    statePermissions () {
      if (!this.orgWorkflowConfig) {
        return null
      }
      return this.orgWorkflowConfig.states[0].permissions
    },
    canAccess () {
      if (!this.orgUser) {
        return false
      }
      if (!this.orgWorkflowConfig) {
        return false
      }
      if (this.orgWorkflowConfig.userGroup == 'All') {
        return true
      }
      if (this.orgUser.groups.includes(this.orgWorkflowConfig.userGroup)) {
        return true
      }
      return false
    },
  },
  watch: {
    orgWorkflowConfig: function (val) {
      if (val && this.copyFrom == 'new') {
        var model = {}
        for(const field of val.fields) {
          if (field.defaultValue != null) {
            model[field.name] = field.defaultValue
          } else {
            model[field.name] = null
          }
        }
        model.state = this.firstStateName
        model.createdBy = this.email
        this.model = model
      }
    },
  },
  methods: {
    getWorkflow () {
      this.waiting = true
      this.$http.post(this.server + '/org/get-workflow/' + this.configId + '/' + this.copyFrom + '/', this.orgWorkflowConfig).then(resp => {
        var model = resp.body
        model.state = this.firstStateName
        model.createdBy = this.email
        for(const f of this.orgWorkflowConfig.fields) {
          if (!this.isFieldEditable(f, model)) {
            model[f.name] = null
          }
        }
        this.model = model
        this.waiting = false
      }, err => {
        console.log('Failed to get workflow')
        this.waiting = false
      })
    },
    onModelUpdated (val) {
      this.newModel = val
    },
    createWorkflow () {
      if (this.creating) {
        return
      }

      this.creating = true
      this.newModel.state = this.firstStateName
      this.newModel.folderId = this.folderId
      this.$http.post(this.server + '/org/create-workflow', this.newModel).then(resp => {
        this.sendNotification(resp.body)
        this.$router.push('/org/' + this.orgId + '/workflow/' + this.configId + '/' + resp.body.id)
        this.creating = false
      }, err => {
        this.error = err
        this.creating = false
      })
    },
    sendNotification (workflow) {
      var emails = this.collectEmails(workflow)
      if (!emails.length) {
        return
      }
      var message = {
        workflowId: workflow.id,
        workflowConfigId: this.orgWorkflowConfig.id,
        receivers: emails,
        additionalMessage: 'A workflow has been created by ' + this.orgUser.username + ' <' + this.orgUser.email + '>.',
        workflowLink: window.location.origin + '/org/' + this.orgId + '/workflow/' + this.orgWorkflowConfig.id + '/' + workflow.id,
      }
      this.$http.post(this.server + '/org/send-email-about-workflow', message)
    },
    collectEmails (workflow) {
      var emails = []
      if (this.orgWorkflowConfig.creationNotifyingGroups && this.orgWorkflowConfig.creationNotifyingGroups.length) {
        for (const u of this.orgUsers) {
          if (this.orgWorkflowConfig.creationNotifyingGroups.includes('All')) {
            emails.push(u.email)
          } else {
            for (const g of u.groups) {
              if (this.orgWorkflowConfig.creationNotifyingGroups.includes(g)) {
                emails.push(u.email)
              }
            }
          }
        }
      }
      if (this.orgWorkflowConfig.creationNotifyingOthers && this.orgWorkflowConfig.creationNotifyingOthers.length) {
        for (const o of this.orgWorkflowConfig.creationNotifyingOthers) {
          if (o == 'Workflow Creator') {
            emails.push(this.email)
          } else if(this.isValidateEmail(workflow[o])) {
            emails.push(workflow[o])
          }
        }
      }
      return [...new Set(emails)]
    },
    isValidateEmail (email) {
      if (!email) {
        return false
      }
      return String(email)
        .toLowerCase()
        .match(/^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/)
    },
    isFieldEditable (f, model) {
      for (const permission of this.statePermissions) {
        if (permission.action != 'Edit') {
          continue
        }
        if (this.userIsActor(permission, model)) {
          if (permission.actionFields.includes(f.name) || permission.actionFields.includes('All')) {
            return true
          }
        }
      }
      return false
    },
    userIsActor (permission, model) {
      var allowedGroups = permission.groups
      for (const g of allowedGroups) {
        if (this.orgUser.groups.includes(g)) {
          return true
        }
      }
      var others = permission.others
      for (const o of others) {
        if (o == 'Workflow Creator') {
          return true
        } else {
          var field = null
          for (const f of this.orgWorkflowConfig.fields) {
            if (f.name == o) {
              field = f
            }
          }
          if (field) {
            if (field.type == 'string') {
              if (this.email == model[field.name]) {
                return true
              }
            }
            if (field.type == 'strings') {
              if (model[field.name].includes(this.email)) {
                return true
              }
            }
          }
        }
      }
    },
  },
  mounted () {
    if (this.copyFrom != 'new') {
      this.$nextTick(function () {
        this.getWorkflow(this.copyFrom)
      })
    } else {
      if (this.orgWorkflowConfig) {
        var model = {}
        for(const field of this.orgWorkflowConfig.fields) {
          if (field.defaultValue != null) {
            model[field.name] = field.defaultValue
          } else {
            model[field.name] = null
          }
        }
        model.state = this.firstStateName
        model.createdBy = this.email
        this.model = model
      }
    }
  },
}
</script>

<style scoped lang="scss">

</style>
