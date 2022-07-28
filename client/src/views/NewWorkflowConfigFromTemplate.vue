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
          <li class="is-active"><a href="#" aria-current="page">New From Template</a></li>
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
              <div v-if="template">
                <div>{{template.name}}</div>
                <string-field :label="'Template Name'" :value="template.name" :readonly="true" />
                <textarea-field :label="'Template Description'" :value="template.description" :readonly="true" />

                <workflow-config-model :model="template.workflowConfig" :isNew="true" @model-updated="onModelUpdated"  />

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
import StringField from '@/components/form/StringField'
import TextareaField from '@/components/form/TextareaField'

export default {
  name: 'NewWorkflowConfigFromTemplate',
  components: {
    WorkflowConfigModel,
    StringField,
    TextareaField
  },
  data () {
    return {
      error: '',
      waiting: false,
      model: null,
      newModel: null,
      creating: false,
      template: null,
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
    templateId () {
      return this.$route.params.templateId
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
      if (!this.newModel || !this.newModel.tableName) {
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
  },
  watch: {
    templateId: function (val) {
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
        this.$router.push('/org/' + this.orgId + '/workflow-configs')
        this.creating = false
      }, err => {
        this.error = err
        this.creating = false
      })
    },
    getTemplate () {
      this.waiting = true
      this.$http.get(this.server + '/template/get-template/' + this.templateId + '/').then(resp => {
        this.template = resp.body
        this.waiting = false
      }, err => {
        this.error = err
        this.waiting = false
      })
    },
  },
  mounted () {
    this.getTemplate()
  },
}
</script>

<style scoped lang="scss">

</style>
