<template>
  <div class="container mt-5 px-2">
    <article class="message is-danger" v-if="!token">
      <div class="message-body">
        You have not signed in yet. Please go back to <a href="/">home page</a> to sign in first.
      </div>
    </article>
    <div v-if="token">
      <div class="mb-5">
        <nav class="breadcrumb" aria-label="breadcrumbs" v-if="orgWorkflowConfig">
          <ul>
            <li><router-link :to="'/org/' + orgId + '/workflow-folder/' + configId + '/' + configId">{{orgWorkflowConfig.name}}</router-link></li>
            <li class="is-active"><a href="#" aria-current="page">{{workflowId}}</a></li>
          </ul>
        </nav>
      </div>

      <div v-if="!orgUser">
        <span class="icon is-medium is-size-4">
          <i class="fas fa-spinner fa-pulse"></i>
        </span>
      </div>
      <div v-else>
        <div v-if="!canAccess">
          <div class="message-body">
            You are not allowed to access this page
          </div>
        </div>
        <div v-else>
          <div class="mt-3">
            <div v-if="waiting">
              <span class="icon is-medium is-size-4">
                <i class="fas fa-spinner fa-pulse"></i>
              </span>
            </div>
            <div v-else>
              <div v-if="model">
                <div v-if="!canView">
                  <div class="message-body">
                    You are not allowed to view this workflow.
                  </div>
                </div>
                <div v-else>
                  <nav class="level">
                    <div class="level-item has-text-centered">
                      <div>
                        <p class="heading">State</p>
                        <span class="tag is-link is-medium has-text-weight-bold">{{model.state}}</span>
                      </div>
                    </div>
                    <div class="level-item has-text-centered">
                      <div>
                        <p class="heading">Created By</p>
                        <p class="title is-6">{{model.createdBy}}</p>
                      </div>
                    </div>
                    <div class="level-item has-text-centered">
                      <div>
                        <p class="heading">Created At</p>
                        <p class="title is-6">{{createdAtLabel}}</p>
                      </div>
                    </div>
                    <div class="level-item has-text-centered">
                      <div>
                        <p class="heading">Updated At</p>
                        <p class="title is-6">{{updatedAtLabel}}</p>
                      </div>
                    </div>
                  </nav>

                  <workflow-model :model="model" :readonly="!canSave" @model-updated="onModelUpdated" />

                  <div class="field is-grouped">
                    <div class="control" v-if="canSave">
                      <button class="button is-link" :class="{'is-loading': updating}" @click="updateWorkflow">Save</button>
                    </div>
                    <div class="control" v-if="canDelete">
                      <button class="button is-danger" :class="{'is-loading': deleting}" @click="deleteWorkflow">Delete</button>
                    </div>
                  </div>

                  <hr />

                  <div class="field is-grouped">
                    <div class="control" v-for="(t, i) in availableTransitions" :key="'at-' + i">
                      <button class="button is-dark" :class="{'is-loading': transiting}" @click="transiteWorkflow(t)">{{t.actionLabel}}</button>
                    </div>
                    <div class="control">
                      <button class="button" @click="sendEmail">Send Email</button>
                    </div>
                    <div class="control" v-if="folderId">
                      <router-link class="button" :to="'/org/' + orgId + '/new-workflow/' + configId + '/' + folderId + '/' + workflowId">Copy to New</router-link>
                    </div>
                  </div>

                  <div v-if="modelDiff" class="notification is-warning is-light">
                    You have unsaved changes!
                  </div>

                  <div v-if="error" class="notification is-danger is-light">
                    <button class="delete" @click="error=''"></button>
                    {{error}}
                  </div>

                  <send-email-modal :opened="sendEmailModal.opened" :workflow="model" @send-email-modal-closed="onSendEmailModalClosed" />
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
import SendEmailModal from '@/components/modals/SendEmailModal'
import dateFormat from 'dateformat'

export default {
  name: 'Workflow',
  components: {
    WorkflowModel,
    SendEmailModal
  },
  data () {
    return {
      error: '',
      waiting: false,
      model: null,
      newModel: null,
      updating: false,
      deleting: false,
      transiting: false,
      sendEmailModal: {
        opened: false,
      }
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
    workflowId () {
      return this.$route.params.workflowId
    },
    folderId () {
      if (!this.model) {
        return ''
      }
      return this.model.folderId
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
    stateConfig () {
      if (!this.orgWorkflowConfig || !this.model) {
        return null
      }
      var state = this.model.state
      var stateConfig = null
      for (const sc of this.orgWorkflowConfig.states) {
        if (sc.name == state) {
          stateConfig = sc
        }
      }
      return stateConfig
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
    canView () {
      if (!this.canAccess) {
        return false
      }
      if (!this.stateConfig) {
        return false
      }
      return this.userHasPermission(this.stateConfig.permissions.view)
    },
    canSave () {
      if (!this.canAccess) {
        return false
      }
      if (!this.stateConfig) {
        return false
      }
      return this.userHasPermission(this.stateConfig.permissions.save)
    },
    canDelete () {
      if (!this.canAccess) {
        return false
      }
      if (!this.stateConfig) {
        return false
      }
      return this.userHasPermission(this.stateConfig.permissions.delete)
    },
    createdAtLabel () {
      if (!this.model || !this.model.createdAt) {
        return ''
      }
      return dateFormat(new Date(this.model.createdAt), 'mm/dd/yyyy h:MM TT')
    },
    updatedAtLabel () {
      if (!this.model || !this.model.updatedAt) {
        return ''
      }
      return dateFormat(new Date(this.model.updatedAt), 'mm/dd/yyyy h:MM TT')
    },
    modelDiff () {
      if (!this.model || !this.newModel) {
        return false
      }
      for (const f of this.orgWorkflowConfig.fields) {
        if (JSON.stringify(this.model[f.name]) != JSON.stringify(this.newModel[f.name])) {
          return true
        }
      }
      return false
    },
    availableTransitions () {
      if (!this.canAccess) {
        return []
      }
      if (!this.stateConfig) {
        return []
      }
      var transitions = []
      for (const t of this.stateConfig.transitions) {
        if (this.userHasPermission(t.actor)) {
          transitions.push(t)
        }
      }
      return transitions
    },
  },
  watch: {
    workflowId: function (val) {
      if (val) {
        this.getWorkflow()
      }
    },
    org: function (val) {
      if (val) {
        this.getWorkflow()
      }
    },
  },
  methods: {
    getWorkflow () {
      this.waiting = true
      this.$http.get(this.server + '/org/get-workflow/' + this.configId + '/' + this.workflowId).then(resp => {
        this.model = resp.body
        this.waiting = false
      }, err => {
        console.log('Failed to get workflow')
        this.waiting = false
      })
    },
    onModelUpdated (val) {
      this.newModel = val
    },
    updateWorkflow () {
      if (this.updating) {
        return
      }

      this.updating = true
      this.$http.post(this.server + '/org/update-workflow', this.newModel).then(resp => {
        this.model = resp.body
        this.updating = false
      }, err => {
        this.error = err
        this.updating = false
      })
    },
    deleteWorkflow () {
      var confirm = {
        title: 'Delete Workflow',
        message: 'Are you sure to delete this workflow?',
        button: 'Yes, I am sure.',
        callback: {
          context: this,
          method: this.deleteWorkflowConfirmed,
          args: []
        }
      }
      this.$store.commit('modals/openConfirmModal', confirm)
    },
    deleteWorkflowConfirmed () {
      if (this.deleting) {
        return
      }

      this.deleting = true
      this.$http.post(this.server + '/org/delete-workflow', this.model).then(resp => {
        this.$router.push('/org/' + this.orgId + '/workflow-folder/' + this.configId + '/' + this.model.folderId)
        this.deleting = false
      }, err => {
        this.error = err
        this.deleting = false
      })
    },
    userHasPermission (permission) {
      var allowedGroups = permission.groups
      for (const g of allowedGroups) {
        if (this.orgUser.groups.includes(g)) {
          return true
        }
      }
      var others = permission.others
      for (const o of others) {
        if (o == 'Workflow Creator') {
          if (this.model.createdBy == this.email) {
            return true
          }
        } else {
          var field = null
          for (const f of this.orgWorkflowConfig.fields) {
            if (f.name == o) {
              field = f
            }
          }
          if (field) {
            if (field.type == 'string') {
              if (this.email == this.model[field.name]) {
                return true
              }
            }
            if (field.type == 'strings') {
              if (this.model[field.name].includes(this.email)) {
                return true
              }
            }
          }
        }
        return false
      }
    },
    transiteWorkflow (transition) {
      var confirm = {
        title: 'Transite Workflow',
        message: 'Are you sure to transite the state to "' + transition.toState + '"?',
        button: 'Yes, I am sure.',
        callback: {
          context: this,
          method: this.transiteWorkflowConfirmed,
          args: [transition]
        }
      }
      this.$store.commit('modals/openConfirmModal', confirm)
    },
    transiteWorkflowConfirmed (transition) {
      var model = this.newModel || this.model
      model.state = transition.toState

      this.transiting = true
      this.$http.post(this.server + '/org/update-workflow', model).then(resp => {
        this.model = resp.body
        this.transiting = false
      }, err => {
        this.error = err
        this.transiting = false
      })
    },
    sendEmail () {
      this.sendEmailModal.opened = true
    },
    onSendEmailModalClosed () {
      this.sendEmailModal.opened = false
    },
  },
  mounted () {
    if (this.org) {
      this.getWorkflow()
    }
  },
}
</script>

<style scoped lang="scss">

</style>
