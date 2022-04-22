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
          model[field.name] = null
        }
        this.model = model
      }
    },
  },
  methods: {
    getWorkflow () {
      this.waiting = true
      this.$http.get(this.server + '/org/get-workflow/' + this.configId + '/' + this.copyFrom).then(resp => {
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
    createWorkflow () {
      if (this.creating) {
        return
      }

      this.creating = true
      this.newModel.state = this.firstStateName
      this.newModel.folderId = this.folderId
      this.$http.post(this.server + '/org/create-workflow', this.newModel).then(resp => {
        this.$router.push('/org/' + this.orgId + '/workflow/' + this.configId + '/' + resp.body.id)
        this.creating = false
      }, err => {
        this.error = err
        this.creating = false
      })
    },
  },
  mounted () {
    if (this.copyFrom != 'new') {
      this.getWorkflow(this.copyFrom)
    } else {
      if (this.orgWorkflowConfig) {
        var model = {}
        for(const field of this.orgWorkflowConfig.fields) {
          model[field.name] = null
        }
        this.model = model
      }
    }
  },
}
</script>

<style scoped lang="scss">

</style>
