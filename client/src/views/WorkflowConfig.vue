<template>
  <div class="container mt-5 px-2">
    <article class="message is-danger" v-if="!token">
      <div class="message-body">
        You have not signed in yet. Please go back to <a href="/">home page</a> to sign in first.
      </div>
    </article>
    <div v-if="token">
      <nav class="breadcrumb" aria-label="breadcrumbs">
        <ul>
          <li><router-link :to="'/org/' + orgId + '/workflow-configs'">All Workflow Configs</router-link></li>
          <li class="is-active"><a href="#" aria-current="page">{{configId}}</a></li>
        </ul>
      </nav>

      <div v-if="!orgUser">
        <span class="icon is-medium is-size-4">
          <i class="fas fa-spinner fa-pulse"></i>
        </span>
      </div>
      <div v-else>
        <div v-if="!isAdmin">
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

                <workflow-config-model :model="model" :isNew="false" @model-updated="onModelUpdated"  />

                <hr />

                <div class="field is-grouped mt-5">
                  <div class="control">
                    <button class="button is-link" :class="{'is-loading': updating}" :disabled="!canUpdate" @click="updateWorkflowConfig">Update</button>
                  </div>
                  <div class="control">
                    <button class="button is-danger" :class="{'is-loading': deleting}" @click="deleteWorkflowConfig">Delete</button>
                  </div>
                  <div class="control">
                    <router-link class="button" :to="'/org/' + orgId + '/new-workflow-config/' + configId">Copy to New</router-link>
                  </div>
                </div>

                <div v-if="modelChanged" class="notification is-warning is-light">
                  You have unsaved changes!
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
import WorkflowConfigModel from '@/components/workflow/WorkflowConfigModel'

export default {
  name: 'WorkflowConfig',
  components: {
    WorkflowConfigModel
  },
  data () {
    return {
      error: '',
      waiting: false,
      newModel: null,
      updating: false,
      deleting: false,
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
    orgId () {
      return this.$route.params.orgId
    },
    configId () {
      return this.$route.params.configId
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
    isAdmin () {
      if (!this.orgUser) {
        return false
      }
      return this.orgUser.role == 'Owner' || this.orgUser.role == 'Admin'
    },
    canUpdate () {
      if (!this.newModel) {
        return false
      }
      if (!this.newModel.name.trim()) {
        return false
      }
      return true
    },
    orgWorkflowConfigs () {
      return this.$store.state.org.orgWorkflowConfigs
    },
    model () {
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
    modelChanged () {
      if (!this.model || !this.newModel) {
        return false
      }
      return this.model.name != this.newModel.name
        || this.model.description != this.newModel.description
        || this.model.userGroup != this.newModel.userGroup
        || JSON.stringify(this.model.fields) != JSON.stringify(this.newModel.fields)
        || JSON.stringify(this.model.states) != JSON.stringify(this.newModel.states)
    },
  },
  methods: {
    onModelUpdated (val) {
      this.newModel = val
    },
    updateWorkflowConfig () {
      if (this.updating || !this.canUpdate) {
        return
      }

      this.updating = true
      this.$http.post(this.server + '/org/update-workflow-config/' + this.configId, this.newModel).then(resp => {
        this.$store.commit('org/updateOrgWorkflowConfig', resp.body)
        this.updating = false
      }, err => {
        this.error = err
        this.updating = false
      })
    },
    deleteWorkflowConfig () {
      var confirm = {
        title: 'Delete Workflow Config',
        message: 'Are you sure to delete this workflow config? All the workflows under it will be missing then',
        button: 'Yes, I am sure.',
        callback: {
          context: this,
          method: this.deleteWorkflowConfigConfirmed,
          args: []
        }
      }
      this.$store.commit('modals/openConfirmModal', confirm)
    },
    deleteWorkflowConfigConfirmed () {
      this.deleting = true
      this.$http.post(this.server + '/org/delete-workflow-config/' + this.configId).then(resp => {
        this.$store.commit('org/removeOrgWorkflowConfig', resp.body)
        this.$router.push('/org/' + this.orgId + '/workflows')
        this.deleting = false
      }, err => {
        this.error = err
        this.deleting = false
      })
    },
  },
}
</script>

<style scoped lang="scss">

</style>
