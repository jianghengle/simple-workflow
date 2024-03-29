<template>
  <div class="container mt-5 px-2">
    <article class="message is-danger" v-if="!token">
      <div class="message-body">
        You have not signed in yet. Please go back to <a href="/">home page</a> to sign in first.
      </div>
    </article>
    <div v-if="token">
      <div class="mb-5" v-if="folderId">
        <address-bar :workflowFolderId="folderId" />
      </div>

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
                        <span class="tag is-link is-medium has-text-weight-bold" :style="{'background-color': stateColor}">
                          {{model.state}}
                        </span>
                      </div>
                    </div>
                    <div class="level-item has-text-centered">
                      <div>
                        <p class="heading">Created By</p>
                        <p class="title is-6">
                          <span>{{orgUsersMap[model.createdBy].username}}</span><br/>
                          <span class="has-text-weight-light">{{model.createdBy}}</span>
                        </p>
                      </div>
                    </div>
                    <div class="level-item has-text-centered">
                      <div>
                        <p class="heading">Created At</p>
                        <p class="title is-6">
                          <span>{{createdAtLabel}}</span>
                        </p>
                      </div>
                    </div>
                    <div class="level-item has-text-centered">
                      <div>
                        <p class="heading">Updated At</p>
                        <p class="title is-6">{{updatedAtLabel}}</p>
                      </div>
                    </div>
                  </nav>

                  <workflow-model :model="model" @model-updated="onModelUpdated" />

                  <div class="field is-grouped">
                    <div class="control" v-if="canSave">
                      <button class="button is-link" :disabled="!requiredFieldsReady" :class="{'is-loading': updating}" @click="updateWorkflow">Save</button>
                    </div>
                    <div class="control" v-if="canDelete">
                      <button class="button is-danger" :class="{'is-loading': deleting}" @click="deleteWorkflow">Delete</button>
                    </div>
                  </div>

                  <div v-if="modelDiff" class="notification is-warning is-light">
                    You have unsaved changes!
                  </div>

                  <hr />

                  <div class="field is-grouped">
                    <div class="control" v-for="(t, i) in availableTransitions" :key="'at-' + i">
                      <button class="button is-link" :disabled="!requiredFieldsReady" :class="{'is-loading': transiting}" @click="transiteWorkflow(t)" :style="{'background-color': getTransitionColor(t.toState)}">
                        {{t.actionLabel}}
                      </button>
                    </div>
                    <div class="control">
                      <button class="button" @click="sendEmail">Send Email</button>
                    </div>
                    <div class="control" v-if="folderId">
                      <router-link class="button" :to="'/org/' + orgId + '/new-workflow/' + configId + '/' + configId + '/' + workflowId">Copy to New</router-link>
                    </div>
                  </div>

                  <div v-if="error" class="notification is-danger is-light">
                    <button class="delete" @click="error=''"></button>
                    {{error}}
                  </div>
                  <div v-if="orgUsers">
                    <send-email-modal :opened="sendEmailModal.opened" :workflow="model" @send-email-modal-closed="onSendEmailModalClosed" />
                  </div>
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
import AddressBar from '@/components/workflow/AddressBar'

export default {
  name: 'Workflow',
  components: {
    WorkflowModel,
    SendEmailModal,
    AddressBar
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
    folderMap () {
      return this.$store.state.folders.folderMap
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
    orgUsersMap () {
      if (!this.orgUsers) {
        return {}
      }
      var result = {}
      for (const u of this.orgUsers) {
        result[u.email] = u
      }
      return result
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
    stateColorMap () {
      var stateColorMap = {}
      if (!this.orgWorkflowConfig) {
        return stateColorMap
      }
      for (const state of this.orgWorkflowConfig.states) {
        stateColorMap[state.name] = state.color
      }
      return stateColorMap
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
    statePermissions () {
      if (this.stateConfig) {
        return this.stateConfig.permissions
      }
      return null
    },
    stateColor () {
      if (!this.stateConfig || !this.stateConfig.color) {
        return '#485fc7'
      }
      return this.stateConfig.color
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
      return this.isAnyFieldViewable()
    },
    canSave () {
      if (!this.canAccess) {
        return false
      }
      if (!this.stateConfig) {
        return false
      }
      return this.isAnyFieldEditable()
    },
    canDelete () {
      if (!this.canAccess) {
        return false
      }
      if (!this.stateConfig) {
        return false
      }
      for (const permission of this.statePermissions) {
        if (permission.action == 'Delete' && this.userIsActor(permission)) {
          return true
        }
      }
      return false
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
        if (f.type == 'sheet' || f.type == 'items') {
          if (!this.model[f.name] || !this.newModel[f.name]) {
            continue
          }
          if (this.model[f.name].length != this.newModel[f.name].length) {
            return true
          }
          for (var i=0;i<this.model[f.name].length;i++) {
            var modelRow = this.model[f.name][i]
            var newModelRow = this.newModel[f.name][i]
            if (f.type == 'sheet') {
              for (const c of f.columns) {
                if (modelRow[c] != newModelRow[c]) {
                  return true
                }
              }
            } else {
              for (const c of f.itemFields) {
                if (modelRow[c.name] != newModelRow[c.name]) {
                  return true
                }
              }
            }
          }
        } else if (f.type == 'files' || f.type == 'file') {
          if (!this.model[f.name] && this.newModel[f.name]) {
            return true
          }
          if (this.model[f.name] && !this.newModel[f.name]) {
            return true
          }
          if (this.model[f.name] && this.newModel[f.name]) {
            if (f.type == 'file') {
              if (this.model[f.name].key != this.newModel[f.name].key) {
                return true
              }
            } else if (this.model[f.name].length != this.newModel[f.name].length) {
              return true
            } else {
              for (var i=0;i<this.model[f.name].length;i++) {
                if (this.model[f.name][i].key != this.newModel[f.name][i].key) {
                  return true
                }
              }
            }
          }
        } else {
          if (this.model[f.name] == null) {
            if (this.newModel[f.name]) {
              return true
            }
          } else if (this.model[f.name] != this.newModel[f.name]) {
            return true
          }
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
        var canTransite = false
        if (!t.permissions) {
          continue
        }
        for (const p of t.permissions) {
          if (this.userIsActor(p) && this.isConditionSatisfied(p) && this.areRequiredFieldsFilled(p)) {
            canTransite = true
            break
          }
        }
        if (canTransite) {
          transitions.push(t)
        }        
      }
      return transitions
    },
    requiredFieldsReady () {
      if (!this.newModel || !this.orgWorkflowConfig) {
        return false
      }
      for(const field of this.orgWorkflowConfig.fields) {
        if (field.required && !this.newModel[field.name] && this.newModel[field.name] !== 0) {
          return false
        }
      }
      return true
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
    orgWorkflowConfig: function (val) {
      if (val) {
        this.getWorkflow()
        if (!this.folderMap) {
          this.getFolders()
        }
      }
    },
    configId: function (val) {
      this.getFolders()
    },
  },
  methods: {
    getTransitionColor (stateName) {
      var color = this.stateColorMap[stateName]
      return color || '#485fc7'
    },
    getWorkflow () {
      if (!this.orgWorkflowConfig) {
        return
      }
      this.waiting = true
      this.$http.post(this.server + '/org/get-workflow/' + this.configId + '/' + this.workflowId + '/', this.orgWorkflowConfig).then(resp => {
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
      if (!this.requiredFieldsReady || this.updating) {
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
    isAnyFieldViewable () {
      for (const f of this.orgWorkflowConfig.fields) {
        if (this.isFieldViewable(f)) {
          return true
        }
      }
      return false
    },
    isFieldViewable (f) {
      for (const permission of this.statePermissions) {
        if (permission.action != 'View') {
          continue
        }
        if (this.userIsActor(permission)) {
          if (permission.actionFields.includes(f.name) || permission.actionFields.includes('All')) {
            return true
          }
        }
      }
      return false
    },
    isAnyFieldEditable () {
      for (const f of this.orgWorkflowConfig.fields) {
        if (this.isFieldEditable(f)) {
          return true
        }
      }
      return false
    },
    isFieldEditable (f) {
      for (const permission of this.statePermissions) {
        if (permission.action != 'Edit') {
          continue
        }
        if (this.userIsActor(permission)) {
          if (permission.actionFields.includes(f.name) || permission.actionFields.includes('All')) {
            return true
          }
        }
      }
      return false
    },
    userIsActor (permission) {
      var allowedGroups = permission.groups
      for (const g of allowedGroups) {
        if (this.orgUser.groups.includes(g)) {
          return true
        }
      }
      var model = this.newModel || this.model
      var others = permission.others
      for (const o of others) {
        if (o == 'Workflow Creator') {
          if (model.createdBy == this.email) {
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
      return false
    },
    isConditionSatisfied (c) {
      var conditionField = c.conditionField
      if (!conditionField) {
        return true
      }
      if (!this.newModel) {
        return false
      }
      var conditionFieldValue = Number(this.newModel[conditionField])
      return this.isNumberConditionSatisfied(conditionFieldValue, c.conditionOperator, c.conditionOperand)
    },
    isNumberConditionSatisfied (v, operator, operand) {
      if (operator == '<') {
        return v < operand
      }
      if (operator == '<=') {
        return v <= operand
      }
      if (operator == '==') {
        return v == operand
      }
      if (operator == '>=') {
        return v >= operand
      }
      if (operator == '>') {
        return v > operand
      }
      return false
    },
    areRequiredFieldsFilled (p) {
      if (!p.requiredFields || !p.requiredFields.length) {
        return true
      }
      if (!this.newModel) {
        return false
      }
      for (const f of this.orgWorkflowConfig.fields) {
        if (p.requiredFields.includes(f.name)) {
          var value = this.newModel[f.name]
          if (f.type == 'number') {
            if (value == undefined || value == null || value == '') {
              return false
            }
          } else if (f.type == 'items') {
            if (!value || !value.length) {
              return false
            }
          } else if (!value) {
            return false
          }
        }
      }
      return true
    },
    transiteWorkflow (transition) {
      if (!this.requiredFieldsReady) {
        return
      }
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
        this.sendNotification(resp.body, transition)
        this.transiting = false
      }, err => {
        this.error = err
        this.transiting = false
      })
    },
    sendNotification (workflow, transition) {
      var emails = this.collectEmails(workflow, transition)
      if (!emails.length) {
        return
      }
      var message = {
        workflowId: workflow.id,
        workflowConfigId: this.orgWorkflowConfig.id,
        receivers: emails,
        additionalMessage: 'The workflow has transitioned to ' + workflow.state,
        workflowLink: window.location.origin + '/org/' + this.orgId + '/workflow/' + this.orgWorkflowConfig.id + '/' + workflow.id,
      }
      this.$http.post(this.server + '/org/send-email-about-workflow', message)
    },
    collectEmails (workflow, transition) {
      var emails = []
      if (transition.transitionNotifyingGroups && transition.transitionNotifyingGroups.length) {
        for (const u of this.orgUsers) {
          if (transition.transitionNotifyingGroups.includes('All')) {
            emails.push(u.email)
          } else {
            for (const g of u.groups) {
              if (transition.transitionNotifyingGroups.includes(g)) {
                emails.push(u.email)
              }
            }
          }
        }
      }
      if (transition.transitionNotifyingOthers && transition.transitionNotifyingOthers.length) {
        for (const o of transition.transitionNotifyingOthers) {
          if (o == 'Workflow Creator') {
            emails.push(workflow.createdBy)
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
    sendEmail () {
      this.sendEmailModal.opened = true
    },
    onSendEmailModalClosed () {
      this.sendEmailModal.opened = false
    },
    getFolders () {
      this.$http.get(this.server + '/org/get-folders-for-workflow-config/' + this.configId + '/').then(resp => {
        this.$store.commit('folders/setFolderMap', resp.body)
      }, err => {
        console.log('Failed to get folders')
      })
    },
  },
  mounted () {
    if (this.org) {
      this.getWorkflow()
      if (!this.folderMap) {
        this.getFolders()
      }
    }
  },
}
</script>

<style scoped lang="scss">

</style>
