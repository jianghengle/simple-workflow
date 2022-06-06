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
          <li class="is-active"><a href="#" aria-current="page">New</a></li>
        </ul>
      </nav>

      <div v-if="!orgUser">
        <span class="icon is-medium is-size-4">
          <i class="fas fa-spinner fa-pulse"></i>
        </span>
      </div>
      <div v-else>
        <div v-if="!isAdmin">
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

                <workflow-config-model :model="model" :isNew="true" @model-updated="onModelUpdated"  />

                <div class="field is-grouped mt-5">
                  <div class="control">
                    <button class="button is-link" :class="{'is-loading': creating}" :disabled="!canCreate" @click="createWorkflowConfig">Create</button>
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
import WorkflowConfigModel from '@/components/workflow/WorkflowConfigModel'

export default {
  name: 'NewWorkflowConfig',
  components: {
    WorkflowConfigModel
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
    isAdmin () {
      if (!this.orgUser) {
        return false
      }
      return this.orgUser.role == 'Owner' || this.orgUser.role == 'Admin'
    },
    canCreate () {
      if (!this.newModel) {
        return false
      }
      if (!this.newModel.tableName.slice(this.orgId.length + 1)) {
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
    copyFromConfig () {
      if (!this.orgWorkflowConfigs) {
        return null
      }
      for(const workflowConfig of this.orgWorkflowConfigs) {
        if (workflowConfig.id == this.copyFrom) {
          return workflowConfig
        }
      }
      return null
    },
  },
  watch: {
    copyFromConfig: function (val) {
      if (val) {
        this.model = val
      }
    },
  },
  methods: {
    onModelUpdated (val) {
      this.newModel = val
    },
    createWorkflowConfig () {
      if (this.creating || !this.canCreate) {
        return
      }

      this.creating = true
      this.$http.post(this.server + '/org/create-workflow-config', this.newModel).then(resp => {
        this.$store.commit('org/addOrgWorkflowConfig', resp.body)
        this.$router.push('/org/' + this.orgId + '/workflow-config/' + resp.body.id)
        this.creating = false
      }, err => {
        this.error = err
        this.creating = false
      })
    },
  },
  mounted () {
    if (this.copyFrom == 'new') {
      this.model = {
        tableName: this.orgId + '-',
        name: '',
        description: '',
        userGroup: 'All',
        adminGroup: 'All',
        fields: [],
        states: [
          {
            name: 'Created',
            color: '#1A237E',
            permissions: [],
            transitions: []
          }
        ],
        creationNotifyingGroups: [],
        creationNotifyingOthers: []
      }
    }
  },
}
</script>

<style scoped lang="scss">

</style>
